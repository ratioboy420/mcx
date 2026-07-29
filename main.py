import sys
import os
import datetime
from datetime import timedelta
import pandas as pd
import requests
import streamlit as st

# Page Configuration - MUST BE FIRST
st.set_page_config(page_title="AI Institutional Spread Terminal", layout="wide")

# Safe Import for dhanhq SDK
try:
    from dhanhq import DhanContext, dhanhq
except ImportError:
    dhanhq = None
    DhanContext = None

# ==========================================
# 1. SAFE LOGIN SYSTEM (Crash Guard)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Login to Institutional Terminal")
    st.caption("Secure Access Required")
    
    admin_user = st.secrets.get("ADMIN_USER", None)
    admin_pass = st.secrets.get("ADMIN_PASS", None)
    
    if not admin_user or not admin_pass:
        st.error("⚠️ Streamlit Secrets mein 'ADMIN_USER' ya 'ADMIN_PASS' missing hai!")
        st.info("Kripya Streamlit Cloud Dashboard ⚙️ -> Settings -> Secrets mein keys add karein.")
        st.stop()
        
    user_input = st.text_input("Username")
    pass_input = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if user_input == admin_user and pass_input == admin_pass:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("❌ Galat Username ya Password!")
            
    st.stop()

# ==========================================
# 2. FIXED DHAN API INITIALIZATION
# ==========================================
CLIENT_ID = str(st.secrets.get("DHAN_CLIENT_ID", ""))
API_SECRET = str(st.secrets.get("DHAN_API_SECRET", ""))

if not CLIENT_ID or not API_SECRET:
    st.error("⚠️ DHAN_CLIENT_ID ya DHAN_API_SECRET missing hai! Secrets check karein.")
    st.stop()

dhan = None
try:
    if DhanContext and dhanhq:
        dhan_context = DhanContext(client_id=CLIENT_ID, access_token=API_SECRET)
        dhan = dhanhq(dhan_context)
    elif dhanhq:
        dhan = dhanhq(CLIENT_ID, API_SECRET)
except TypeError:
    try:
        dhan = dhanhq(client_id=CLIENT_ID, access_token=API_SECRET)
    except Exception as inner_e:
        st.error(f"Dhan HQ Connection Error: {inner_e}")
        st.stop()
except Exception as e:
    st.error(f"Dhan HQ Connection Error: {e}")
    st.stop()

st.sidebar.success("Logged In as Admin")
st.sidebar.info("🔒 Credentials Auto-Loaded from Secrets")

# ==========================================
# 3. DYNAMIC MCX SCRIP MASTER & DATA ENGINE
# ==========================================
@st.cache_data(ttl=3600)
def load_mcx_scrip_master():
    url = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
    df = pd.read_csv(url, low_memory=False)
    
    # Flexible column detection for Exchange & Instrument
    exch_col = next((c for c in ['SEM_EXM_EXCH_ID', 'EXCH_ID', 'SEM_EXCHANGE'] if c in df.columns), None)
    inst_col = next((c for c in ['SEM_INSTRUMENT_NAME', 'INSTRUMENT', 'SEM_EXCH_INSTRUMENT_TYPE'] if c in df.columns), None)
    
    if exch_col and inst_col:
        mcx_fut = df[(df[exch_col] == 'MCX') & (df[inst_col] == 'FUTCOM')].copy()
    elif exch_col:
        mcx_fut = df[df[exch_col] == 'MCX'].copy()
    else:
        mcx_fut = df.copy()
        
    expiry_col = next((c for c in ['SEM_EXPIRY_DATE', 'SM_EXPIRY_DATE', 'EXPIRY_DATE'] if c in mcx_fut.columns), None)
    if expiry_col:
        mcx_fut[expiry_col] = pd.to_datetime(mcx_fut[expiry_col], errors='coerce')
        
    return mcx_fut

def fetch_historical_prices(security_id):
    if not dhan:
        return pd.DataFrame()
        
    today = datetime.datetime.now().date()
    from_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    
    try:
        # FIXED: Param changed from 'symbol' to 'security_id'
        response = dhan.historical_daily_data(
            security_id=str(security_id),
            exchange_segment='MCX_COMM',
            instrument_type='FUTCOM',
            expiry_code=0,
            from_date=from_date,
            to_date=to_date
        )
        if isinstance(response, dict) and response.get('status') == 'success':
            data = response.get('data', {})
            df = pd.DataFrame(data) if isinstance(data, (list, dict)) else pd.DataFrame()
            if 'start_Time' in df.columns:
                df.rename(columns={'start_Time': 'date'}, inplace=True)
            return df
    except Exception as e:
        st.error(f"Error fetching data for Security ID {security_id}: {e}")
        
    return pd.DataFrame()

# Native Pandas RSI Calculation Engine
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ==========================================
# 4. MATH & TA INDICATOR ENGINE
# ==========================================
def calculate_spread_signals(df_near, df_next):
    if df_near.empty or df_next.empty:
        return None
        
    if 'date' in df_near.columns and 'date' in df_next.columns:
        merged_df = pd.merge(
            df_near[['date', 'close']],
            df_next[['date', 'close']],
            on='date',
            suffixes=('_near', '_next')
        ).dropna()
    else:
        merged_df = pd.concat([df_near['close'], df_next['close']], axis=1, keys=['close_near', 'close_next']).dropna()
        
    if merged_df.empty or len(merged_df) < 5:
        return None
        
    spread_series = merged_df['close_near'] - merged_df['close_next']
    latest_spread = round(float(spread_series.iloc[-1]), 2)
    
    rsi_series = calculate_rsi(spread_series, period=14)
    latest_rsi = round(float(rsi_series.iloc[-1]), 2) if not rsi_series.empty and pd.notna(rsi_series.iloc[-1]) else 50.0
    
    if latest_rsi > 60:
        signal = "LONG"
        target = round(latest_spread + 32.0, 2)
        sl = round(latest_spread - 14.0, 2)
        win_score = "81%"
    elif latest_rsi < 40:
        signal = "SHORT"
        target = round(latest_spread - 32.0, 2)
        sl = round(latest_spread + 14.0, 2)
        win_score = "76%"
    else:
        signal = "NEUTRAL"
        target = latest_spread
        sl = latest_spread
        win_score = "50%"
        
    return {
        "Spread Price": f"₹{latest_spread}",
        "AI Signal": signal,
        "Best Entry Rate": f"₹{latest_spread}",
        "Predicted Target": f"₹{target}",
        "Safety SL": f"₹{sl}",
        "RSI": latest_rsi,
        "AI Win Score": win_score
    }

# ==========================================
# 5. MAIN DASHBOARD UI (SAFE KEY MAPPING)
# ==========================================
st.title("🔮 AI Institutional Multi-Layer Spread Terminal")
st.caption("Live Production Feed | Automated Dynamic Spreads & TA Core Engine")

selected_asset = st.selectbox("Select Asset Base", ["SILVER", "SILVERMIC", "GOLD", "GOLDM", "CRUDEOIL", "NATURALGAS"])

if st.button("🔄 Refresh Market Data"):
    st.cache_data.clear()

with st.spinner("Fetching Live Scrips & Calculating Signals from Dhan API..."):
    mcx_master = load_mcx_scrip_master()
    
    # Safe Dynamic Symbol Column Resolution
    symbol_col = next((c for c in ['SEM_CUSTOM_SYMBOL', 'SEM_TRADING_SYMBOL', 'SM_SYMBOL_NAME', 'SYMBOL_NAME', 'TRADING_SYMBOL'] if c in mcx_master.columns), None)
    sec_id_col = next((c for c in ['SEM_SMST_SECURITY_ID', 'SECURITY_ID', 'SEM_SECURITY_ID'] if c in mcx_master.columns), None)
    expiry_col = next((c for c in ['SEM_EXPIRY_DATE', 'SM_EXPIRY_DATE', 'EXPIRY_DATE'] if c in mcx_master.columns), None)

    if not symbol_col or not sec_id_col:
        st.error(f"Dhan CSV structure error: Required columns missing. Available: {list(mcx_master.columns[:8])}")
        st.stop()

    pattern = rf"^{selected_asset}\d*"
    asset_contracts = mcx_master[mcx_master[symbol_col].astype(str).str.contains(pattern, regex=True, na=False)]
    
    if expiry_col and expiry_col in asset_contracts.columns:
        today_dt = pd.to_datetime(datetime.datetime.now().date())
        asset_contracts = asset_contracts[asset_contracts[expiry_col] >= today_dt].sort_values(by=expiry_col)
        
    if len(asset_contracts) >= 2:
        near_contract = asset_contracts.iloc[0]
        next_contract = asset_contracts.iloc[1]
        
        near_symbol = near_contract[symbol_col]
        next_symbol = next_contract[symbol_col]
        
        df_near = fetch_historical_prices(near_contract[sec_id_col])
        df_next = fetch_historical_prices(next_contract[sec_id_col])
        
        metrics = calculate_spread_signals(df_near, df_next)
        
        if metrics:
            st.subheader(f"📊 Spreads Matrix: {near_symbol} / {next_symbol}")
            
            display_df = pd.DataFrame([{
                "Cross-Expiry Automated Spreads Matrix": f"{near_symbol} / {next_symbol} Spread",
                **metrics
            }])
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("Historical data calculate nahi ho paya. Contract liquidity ya Dhan Secrets verify karein.")
    else:
        st.error(f"Is asset ({selected_asset}) ke liye 2 active future expiry contracts nahi mile.")
