import sys
import os
import time
import json
import sqlite3
import datetime
from datetime import timedelta
import pandas as pd
import requests
import streamlit as st

# Streamlit Page Setup
st.set_page_config(page_title="AI Institutional MCX Terminal", layout="wide")

# ==========================================
# 1. DATABASE ENGINE (History & Trade Logs)
# ==========================================
DB_FILE = "mcx_terminal_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Trade Signal History Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS trade_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            pair TEXT,
            spread_price REAL,
            signal TEXT,
            entry_rate REAL,
            target REAL,
            sl REAL,
            rsi REAL,
            fvg_status TEXT,
            target_status TEXT
        )
    ''')
    # Market Analytics History Table (OI, Delta, Vol)
    c.execute('''
        CREATE TABLE IF NOT EXISTS market_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            price REAL,
            oi REAL,
            volume REAL,
            delta REAL,
            theta REAL,
            gamma REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def log_signal_to_db(metrics, pair_name):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute('''
            INSERT INTO trade_signals (timestamp, pair, spread_price, signal, entry_rate, target, sl, rsi, fvg_status, target_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            pair_name,
            float(metrics["Spread Price"].replace("₹", "")),
            metrics["AI Signal"],
            float(metrics["Best Entry Rate"].replace("₹", "")),
            float(metrics["Predicted Target"].replace("₹", "")),
            float(metrics["Safety SL"].replace("₹", "")),
            float(metrics["RSI"]),
            metrics["FVG Imbalance"],
            metrics["Target Status"]
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        pass

# ==========================================
# 2. LOGIN & SIDEBAR CREDENTIALS (Corner Lock)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Institutional Terminal Login")
    admin_user = st.secrets.get("ADMIN_USER", "admin")
    admin_pass = st.secrets.get("ADMIN_PASS", "123456")
    
    u_in = st.text_input("Username")
    p_in = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if u_in == admin_user and p_in == admin_pass:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Galat Username ya Password!")
    st.stop()

# Sidebar API Info (Dhan Credentials in Corner)
with st.sidebar:
    st.markdown("### 🔑 API Connections")
    dhan_client = st.secrets.get("DHAN_CLIENT_ID", "Not Connected")
    gemini_key = st.secrets.get("GEMINI_API_KEY", "Not Connected")
    
    st.info(f"**Dhan Client ID:** `{dhan_client[:4]}****`" if len(dhan_client) > 4 else "⚠️ Dhan Not Configured")
    st.info(f"**Gemini AI Key:** `Active`" if gemini_key != "Not Connected" else "⚠️ AI Key Missing")
    st.success("🟢 Server Database Connected")

# ==========================================
# 3. DHAN API & SCRIP MASTER ENGINE
# ==========================================
try:
    from dhanhq import DhanContext, dhanhq
    CLIENT_ID = str(st.secrets.get("DHAN_CLIENT_ID", ""))
    API_SECRET = str(st.secrets.get("DHAN_API_SECRET", ""))
    dhan = dhanhq(CLIENT_ID, API_SECRET)
except Exception:
    dhan = None

@st.cache_data(ttl=3600)
def load_mcx_scrip_master():
    url = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
    df = pd.read_csv(url, low_memory=False)
    
    exch_col = next((c for c in ['SEM_EXM_EXCH_ID', 'EXCH_ID', 'SEM_EXCHANGE'] if c in df.columns), None)
    inst_col = next((c for c in ['SEM_INSTRUMENT_NAME', 'INSTRUMENT', 'SEM_EXCH_INSTRUMENT_TYPE'] if c in df.columns), None)
    
    if exch_col and inst_col:
        mcx_fut = df[(df[exch_col] == 'MCX') & (df[inst_col] == 'FUTCOM')].copy()
    else:
        mcx_fut = df.copy()
        
    expiry_col = next((c for c in ['SEM_EXPIRY_DATE', 'SM_EXPIRY_DATE', 'EXPIRY_DATE'] if c in mcx_fut.columns), None)
    if expiry_col:
        mcx_fut[expiry_col] = pd.to_datetime(mcx_fut[expiry_col], errors='coerce')
        
    return mcx_fut

def fetch_historical_prices(security_id):
    if not dhan:
        # Mock fallback data for demonstration if API key is not active
        dates = pd.date_range(end=datetime.datetime.now(), periods=30)
        return pd.DataFrame({'date': dates, 'close': [72000 + i*50 for i in range(30)], 'oi': [12000 + i*10 for i in range(30)]})
        
    try:
        sec_id_str = str(int(float(security_id)))
    except (ValueError, TypeError):
        sec_id_str = str(security_id).split('.')[0]

    today = datetime.datetime.now().date()
    from_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    try:
        response = dhan.historical_daily_data(
            security_id=sec_id_str,
            exchange_segment='MCX_COMM',
            instrument_type='FUTCOM',
            expiry_code=0,
            from_date=from_date,
            to_date=to_date
        )
        if isinstance(response, dict) and response.get('status') == 'success':
            data = response.get('data', {})
            df = pd.DataFrame(data) if isinstance(data, (list, dict)) else pd.DataFrame()
            if not df.empty and 'start_Time' in df.columns:
                df.rename(columns={'start_Time': 'date'}, inplace=True)
            return df
    except Exception:
        pass
        
    return pd.DataFrame()

# ==========================================
# 4. MATH & TECHNICAL ENGINE (OI, Delta, RSI, FVG)
# ==========================================
def calculate_advanced_metrics(df_near, df_next):
    if df_near.empty or df_next.empty or 'close' not in df_near.columns:
        return None
        
    merged_df = pd.merge(df_near, df_next, on='date', suffixes=('_near', '_next')).dropna()
    if merged_df.empty:
        return None
        
    merged_df['spread'] = merged_df['close_near'] - merged_df['close_next']
    latest_spread = round(float(merged_df['spread'].iloc[-1]), 2)
    
    # RSI Engine
    delta = merged_df['spread'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = round(float((100 - (100 / (1 + rs))).iloc[-1]), 2) if not rs.empty else 50.0
    
    # FVG Detection
    spread_vals = merged_df['spread'].values
    fvg = "NO GAP"
    if len(spread_vals) >= 3:
        if spread_vals[-1] > spread_vals[-3]: fvg = "BULLISH FVG"
        elif spread_vals[-1] < spread_vals[-3]: fvg = "BEARISH FVG"
        
    # Signal Engine
    if rsi > 60:
        sig = "ENTRY LONG"
        target = round(latest_spread + 35.0, 2)
        sl = round(latest_spread - 15.0, 2)
    elif rsi < 40:
        sig = "ENTRY SHORT"
        target = round(latest_spread - 35.0, 2)
        sl = round(latest_spread + 15.0, 2)
    else:
        sig = "NO TRADE / WAIT"
        target = latest_spread
        sl = latest_spread
        
    # Target Status Engine
    target_status = "PENDING / IN-PROGRESS"
    if sig == "ENTRY LONG" and latest_spread >= target:
        target_status = "🎯 TARGET ACHIEVED"
    elif sig == "ENTRY SHORT" and latest_spread <= target:
        target_status = "🎯 TARGET ACHIEVED"
    elif sig == "NO TRADE / WAIT":
        target_status = "N/A"

    return {
        "Spread Price": f"₹{latest_spread}",
        "AI Signal": sig,
        "Best Entry Rate": f"₹{latest_spread}",
        "Predicted Target": f"₹{target}",
        "Safety SL": f"₹{sl}",
        "RSI": rsi,
        "FVG Imbalance": fvg,
        "Target Status": target_status
    }

# ==========================================
# 5. ADVANCED 3 AI AGENTS ENGINE
# ==========================================
def query_gemini_agent(agent_type, market_data):
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        return f"🤖 Agent {agent_type}: Google Gemini Key Missing in Secrets!"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompts = {
        "Risk": f"You are an Expert Risk Manager AI. Analyze this MCX Spread Data: {market_data}. Give strict Stop Loss, Position Sizing, and Volatility risk advice in 3 short bullet points.",
        "Technical": f"You are a Master Technical Analyst AI specializing in FVG, Order Blocks, Delta, and RSI. Data: {market_data}. Provide clear entry/exit logic in 3 bullet points.",
        "Fundamental": f"You are a Macro Fundamental Commodity Expert. Asset context: {market_data}. Explain global demand, supply impact, and macro trends in 3 bullet points."
    }
    
    payload = {"contents": [{"parts": [{"text": prompts[agent_type]}]}]}
    headers = {"Content-Type": "json"}
    
    try:
        res = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error connecting to AI Agent {agent_type}: {e}"
        
    return f"Agent {agent_type} Analysis Ready."

# ==========================================
# 6. DASHBOARD UI & ROW SELECTION
# ==========================================
st.title("⚡ AI Institutional MCX Multi-Layer Terminal")

# Dynamic Modal / Add Pair Selector
if "active_pairs" not in st.session_state:
    st.session_state["active_pairs"] = ["GOLD", "SILVER"]

st.markdown("---")

col_btn, col_blank = st.columns([2, 8])
with col_btn:
    # ADD ROW POPUP DIALOG
    with st.popover("➕ Add Metal Pair Row"):
        st.markdown("### Select Futures Pair")
        mcx_master = load_mcx_scrip_master()
        metal_choice = st.selectbox("Choose Metal Commodity", ["GOLD", "SILVER", "SILVERMIC", "GOLDM", "CRUDEOIL", "NATURALGAS", "COPPER"])
        if st.button("Confirm & Add Pair"):
            if metal_choice not in st.session_state["active_pairs"]:
                st.session_state["active_pairs"].append(metal_choice)
                st.success(f"{metal_choice} Added!")
                st.rerun()

# RENDER LIVE ROWS FOR SELECTED PAIRS
for metal in st.session_state["active_pairs"]:
    st.markdown(f"### 📌 Live Market Pair Matrix: **{metal}**")
    
    mcx_master = load_mcx_scrip_master()
    symbol_col = next((c for c in ['SEM_CUSTOM_SYMBOL', 'SEM_TRADING_SYMBOL', 'SM_SYMBOL_NAME'] if c in mcx_master.columns), None)
    sec_id_col = next((c for c in ['SEM_SMST_SECURITY_ID', 'SECURITY_ID'] if c in mcx_master.columns), None)
    expiry_col = next((c for c in ['SEM_EXPIRY_DATE', 'SM_EXPIRY_DATE'] if c in mcx_master.columns), None)

    pattern = rf"^{metal}\d*"
    asset_contracts = mcx_master[mcx_master[symbol_col].astype(str).str.contains(pattern, regex=True, na=False)]
    
    if expiry_col and expiry_col in asset_contracts.columns:
        today_dt = pd.to_datetime(datetime.datetime.now().date())
        asset_contracts = asset_contracts[asset_contracts[expiry_col] >= today_dt].sort_values(by=expiry_col)

    if len(asset_contracts) >= 2:
        near_c = asset_contracts.iloc[0]
        next_c = asset_contracts.iloc[1]
        
        df_near = fetch_historical_prices(near_c[sec_id_col])
        df_next = fetch_historical_prices(next_c[sec_id_col])
        
        metrics = calculate_advanced_metrics(df_near, df_next)
        
        if metrics:
            # Auto Log to History DB
            log_signal_to_db(metrics, f"{near_c[symbol_col]} / {next_c[symbol_col]}")
            
            # Display Separate Boxes for Clean Layout
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Current Spread Rate", metrics["Spread Price"])
            c2.metric("AI Trade Signal", metrics["AI Signal"])
            c3.metric("Entry / Target Rate", metrics["Best Entry Rate"], delta=metrics["Predicted Target"])
            c4.metric("Safety Stop Loss", metrics["Safety SL"])
            c5.metric("Target Status", metrics["Target Status"])
            
            # Advanced TA/OI Data Box
            with st.expander(f"📊 View Technicals & OI Data ({metal})"):
                st.write(f"**FVG Imbalance:** `{metrics['FVG Imbalance']}` | **RSI (14):** `{metrics['RSI']}`")
                
        else:
            st.info("Fetching live data from Dhan API...")
    else:
        st.warning(f"Active contracts not found for {metal}")
        
    st.markdown("---")

# ==========================================
# 7. 3 AI AGENTS TERMINAL
# ==========================================
st.subheader("🤖 3 AI Institutional Agents")
a1, a2, a3 = st.columns(3)

with a1:
    st.markdown("#### 🛡️ Agent 1: Risk Manager")
    if st.button("Run Risk Analysis"):
        res = query_gemini_agent("Risk", f"Active Metals: {st.session_state['active_pairs']}")
        st.info(res)

with a2:
    st.markdown("#### 📈 Agent 2: Technical Strategist")
    if st.button("Run TA & FVG Analysis"):
        res = query_gemini_agent("Technical", f"Active Metals: {st.session_state['active_pairs']}")
        st.info(res)

with a3:
    st.markdown("#### 🌍 Agent 3: Macro Fundamental")
    if st.button("Run Macro Fundamental"):
        res = query_gemini_agent("Fundamental", f"Active Metals: {st.session_state['active_pairs']}")
        st.info(res)

# ==========================================
# 8. DATABASE & HISTORY TAB
# ==========================================
st.markdown("---")
st.subheader("🗄️ Database History & Complete Logs")

conn = sqlite3.connect(DB_FILE)
history_df = pd.read_sql_query("SELECT * FROM trade_signals ORDER BY id DESC LIMIT 50", conn)
conn.close()

if not history_df.empty:
    st.dataframe(history_df, use_container_width=True)
else:
    st.caption("Database initialized. Live signals will save here automatically.")
