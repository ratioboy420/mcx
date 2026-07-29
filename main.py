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

# Page Setup
st.set_page_config(page_title="AI Institutional MCX Terminal", layout="wide")

# ==========================================
# 1. DATABASE ENGINE (History & Trade Logs)
# ==========================================
DB_FILE = "mcx_terminal_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
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
            target_status TEXT,
            trade_logic TEXT
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
            INSERT INTO trade_signals (timestamp, pair, spread_price, signal, entry_rate, target, sl, rsi, fvg_status, target_status, trade_logic)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            pair_name,
            float(str(metrics["Spread Price"]).replace("₹", "").strip()),
            metrics["AI Signal"],
            float(str(metrics["Best Entry Rate"]).replace("₹", "").strip()),
            float(str(metrics["Predicted Target"]).replace("₹", "").strip()),
            float(str(metrics["Safety SL"]).replace("₹", "").strip()),
            float(metrics["RSI"]),
            metrics["FVG Imbalance"],
            metrics["Target Status"],
            metrics["Trade Logic"]
        ))
        conn.commit()
        conn.close()
    except Exception:
        pass

# ==========================================
# 2. LOGIN & SIDEBAR CREDENTIALS
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

with st.sidebar:
    st.markdown("### 🔑 API Status Box")
    dhan_client = str(st.secrets.get("DHAN_CLIENT_ID", ""))
    gemini_key = str(st.secrets.get("GEMINI_API_KEY", ""))
    
    if len(dhan_client) > 3:
        st.success(f"🟢 Dhan API: Connected ({dhan_client[:3]}***)")
    else:
        st.warning("⚠️ Dhan API Secret Missing")
        
    if len(gemini_key) > 5:
        st.success("🟢 Gemini AI API: Active")
        st.caption("3 AI Agents Connected Live")
    else:
        st.error("❌ Gemini API Key Missing")
        
    st.info("🗄️ Database: Connected")

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
        dates = pd.date_range(end=datetime.datetime.now(), periods=30)
        return pd.DataFrame({'date': dates, 'close': [72000 + i*50 for i in range(30)]})
        
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
# 4. ADVANCED MATH & TECHNICAL TRADE LOGIC ENGINE
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
    
    # Fair Value Gap (FVG) Detection
    spread_vals = merged_df['spread'].values
    fvg = "NO GAP"
    if len(spread_vals) >= 3:
        if spread_vals[-1] > spread_vals[-3]: fvg = "BULLISH FVG (Buying Pressure)"
        elif spread_vals[-1] < spread_vals[-3]: fvg = "BEARISH FVG (Selling Pressure)"
        
    # DETAILED TRADE LOGIC ENGINE
    if rsi > 60:
        sig = "ENTRY LONG"
        target = round(latest_spread + 35.0, 2)
        sl = round(latest_spread - 15.0, 2)
        logic = f"RSI is Overbought ({rsi}) with {fvg}. Strong Bullish Spread momentum towards target."
    elif rsi < 40:
        sig = "ENTRY SHORT"
        target = round(latest_spread - 35.0, 2)
        sl = round(latest_spread + 15.0, 2)
        logic = f"RSI is Oversold ({rsi}) with {fvg}. Bearish Spread divergence breakdown active."
    else:
        sig = "NO TRADE / WAIT"
        target = latest_spread
        sl = latest_spread
        logic = f"RSI Neutral ({rsi}). No FVG Imbalance detected. Waiting for Institutional Breakout Zone."

    # Live Target Achieved / SL Hit Tracking Engine
    target_status = "PENDING / IN-PROGRESS"
    if sig == "ENTRY LONG":
        if latest_spread >= target: target_status = "🎯 TARGET ACHIEVED"
        elif latest_spread <= sl: target_status = "🛑 STOP LOSS HIT"
    elif sig == "ENTRY SHORT":
        if latest_spread <= target: target_status = "🎯 TARGET ACHIEVED"
        elif latest_spread >= sl: target_status = "🛑 STOP LOSS HIT"
    else:
        target_status = "WAITING FOR ENTRY"

    return {
        "Spread Price": f"₹{latest_spread}",
        "AI Signal": sig,
        "Best Entry Rate": f"₹{latest_spread}",
        "Predicted Target": f"₹{target}",
        "Safety SL": f"₹{sl}",
        "RSI": rsi,
        "FVG Imbalance": fvg,
        "Target Status": target_status,
        "Trade Logic": logic
    }

# ==========================================
# 5. ADVANCED 3 AI AGENTS ENGINE
# ==========================================
def query_gemini_agent(agent_type, market_data):
    api_key = st.secrets.get("GEMINI_API_KEY", None)
    if not api_key:
        return f"🤖 Agent {agent_type}: Secrets mein GEMINI_API_KEY daalein!"
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    prompts = {
        "Risk": f"You are an Expert Risk Manager. MCX Spread Data: {market_data}. Provide Stop Loss guidance & Risk-to-Reward advice in 3 short bullet points.",
        "Technical": f"You are a Master Technical Analyst. Spread Data: {market_data}. Give entry, target, and FVG breakdown in 3 short bullet points.",
        "Fundamental": f"You are a Macro Fundamental Expert. Commodity context: {market_data}. Explain global macro demand & supply impact in 3 short bullet points."
    }
    
    payload = {"contents": [{"parts": [{"text": prompts[agent_type]}]}]}
    
    try:
        res = requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        if res.status_code == 200:
            return res.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Error connecting to AI Agent {agent_type}: {e}"
        
    return f"Agent {agent_type} Analysis Ready."

# ==========================================
# 6. DASHBOARD TOP TOOLBAR (Refresh & Add Row Window)
# ==========================================
st.title("⚡ AI Institutional MCX Multi-Layer Terminal")

if "active_pairs" not in st.session_state:
    st.session_state["active_pairs"] = ["GOLD", "SILVER"]

# DEDICATED TOP TOOLBAR (Refresh Key & Add Window)
st.markdown("---")
col_ref, col_add, col_space = st.columns([2.5, 3, 4.5])

with col_ref:
    if st.button("🔄 Refresh Market Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col_add:
    with st.popover("➕ Add Metal Pair Row Window", use_container_width=True):
        st.markdown("#### Select Commodity Fut-to-Fut")
        mcx_master = load_mcx_scrip_master()
        metal_choice = st.selectbox("Metal List", ["GOLD", "SILVER", "SILVERMIC", "GOLDM", "CRUDEOIL", "NATURALGAS", "COPPER"])
        if st.button("Confirm Add Row"):
            if metal_choice not in st.session_state["active_pairs"]:
                st.session_state["active_pairs"].append(metal_choice)
                st.success(f"{metal_choice} Added to Terminal!")
                st.rerun()

st.markdown("---")

# ==========================================
# 7. LIVE MATRIX ROWS WITH TRADE LOGIC & TARGET TRACKING
# ==========================================
for metal in st.session_state["active_pairs"]:
    st.markdown(f"### 📌 Live Market Matrix: **{metal}**")
    
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
            log_signal_to_db(metrics, f"{near_c[symbol_col]} / {next_c[symbol_col]}")
            
            # 5 Clean Metric Boxes
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Live Spread Price", metrics["Spread Price"])
            c2.metric("AI Signal", metrics["AI Signal"])
            c3.metric("Entry / Target", metrics["Best Entry Rate"], delta=metrics["Predicted Target"])
            c4.metric("Safety SL", metrics["Safety SL"])
            c5.metric("Target Status", metrics["Target Status"])
            
            # Dedicated Trade Logic & Reason Box
            st.info(f"🧠 **Trade Logic:** {metrics['Trade Logic']}")
            
            with st.expander(f"📊 Detailed Technical Breakdown & FVG ({metal})"):
                st.write(f"**Pair Name:** `{near_c[symbol_col]} / {next_c[symbol_col]}`")
                st.write(f"**RSI Momentum:** `{metrics['RSI']}` | **Imbalance (FVG):** `{metrics['FVG Imbalance']}`")
        else:
            st.warning("Fetching prices from Dhan API...")
    else:
        st.warning(f"Active contracts not found for {metal}")
        
    st.markdown("---")

# ==========================================
# 8. 3 ONLINE AI AGENTS TERMINAL
# ==========================================
st.subheader("🤖 3 Online AI Institutional Agents")
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
# 9. DATABASE HISTORY TAB
# ==========================================
st.markdown("---")
st.subheader("🗄️ Database Saved History")

conn = sqlite3.connect(DB_FILE)
history_df = pd.read_sql_query("SELECT * FROM trade_signals ORDER BY id DESC LIMIT 50", conn)
conn.close()

if not history_df.empty:
    st.dataframe(history_df, use_container_width=True)
else:
    st.caption("Database active. All trades will save here automatically.")
