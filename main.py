import streamlit as st
import pandas as pd
from datetime import datetime
from database import init_db, save_trade

st.set_page_config(page_title="Dynamic MCX Quant Desk", layout="wide")
init_db()

# --- 1. FETCH REAL MCX SCRIP MASTER (Dynamic Metals & Expiries) ---
@st.cache_data(ttl=3600)  # Har 1 ghante me master file auto-update hogi
def get_mcx_master():
    try:
        # Dhan's official scrip master CSV
        url = "https://images.dhan.co/api-data/api-scrip-master.csv"
        df = pd.read_csv(url, low_memory=False)
        
        # Filter strictly for MCX exchange
        mcx_df = df[df['SEM_EXM_EXCH_ID'] == 'MCX'].copy()
        
        # Clean up missing data to prevent KeyError: nan
        mcx_df = mcx_df.dropna(subset=['SEM_CUSTOM_SYMBOL', 'SEM_EXPIRY_DATE'])
        
        # Create a clean Base Symbol column (e.g., 'GOLDM' from 'GOLDM 05OCT2026')
        mcx_df['BASE_SYMBOL'] = mcx_df['SEM_CUSTOM_SYMBOL'].str.extract(r'^([A-Za-z]+)')
        return mcx_df
    except Exception as e:
        st.error(f"Failed to fetch Dhan Scrip Master: {e}")
        return pd.DataFrame()

mcx_master = get_mcx_master()

# --- 2. SECURE CONNECTION ---
@st.cache_resource
def connect_dhan(client_id, access_token):
    # from dhanhq import dhanhq
    # return dhanhq(client_id, access_token)
    return True # Replace with actual connection

with st.sidebar:
    st.header("🔑 API Login")
    client_id = st.text_input("Dhan Client ID", type="password")
    access_token = st.text_input("Access Token", type="password")
    if st.button("Connect"):
        if client_id and access_token:
            st.session_state.dhan = connect_dhan(client_id, access_token)
            st.success("Connected to Dhan API!")
        else:
            st.error("Please enter credentials.")

# --- 3. DYNAMIC ADD ROW POP-UP ---
@st.dialog("➕ Add New Strategy Leg")
def add_row_dialog():
    st.write("Select Metal and Expiries for Pair Generation")
    
    if mcx_master.empty:
        st.error("Scrip master data not available.")
        return

    # A. Get All Unique MCX Metals
    all_metals = sorted(mcx_master['BASE_SYMBOL'].dropna().unique().tolist())
    
    if not all_metals:
        st.error("No metals found.")
        return

    selected_metal = st.selectbox("1. Select Base Metal", all_metals)
    
    # B. Filter Dataframe for Selected Metal to get its specific Expiries
    metal_df = mcx_master[mcx_master['BASE_SYMBOL'] == selected_metal]
    
    # Sort expiries chronologically
    metal_df['EXPIRY_DATETIME'] = pd.to_datetime(metal_df['SEM_EXPIRY_DATE'])
    active_expiries = sorted(metal_df['EXPIRY_DATETIME'].dt.date.unique().tolist())
    
    # Format expiries as strings for the dropdown
    expiry_options = [exp.strftime('%d-%b-%Y') for exp in active_expiries]
    
    if len(expiry_options) < 2:
        st.warning(f"Not enough expiries found for {selected_metal} to create a spread.")
        return
        
    col1, col2 = st.columns(2)
    with col1:
        near_expiry = st.selectbox("2. Near Expiry (Leg 1)", expiry_options, index=0)
    with col2:
        far_expiry = st.selectbox("3. Far Expiry (Leg 2)", expiry_options, index=1)
        
    action = st.radio("Spread Action", ["SHORT (Sell Near, Buy Far)", "LONG (Buy Near, Sell Far)"])

    if st.button("Generate & Save Pair", type="primary"):
        pair_name = f"{selected_metal} {near_expiry}/{far_expiry}"
        side = "SHORT" if "SHORT" in action else "LONG"
        save_trade(pair_name, side, "pending", 0.0, 0.0, 0.0)
        st.success(f"Added {pair_name} to Dashboard!")
        time.sleep(1) # Chhota sa pause user experience ke liye
        st.rerun()

# --- 4. LIVE DASHBOARD ---
@st.fragment(run_every=5)
def render_live_dashboard():
    st.subheader("📊 Live Pair Spread Desk")
    
    # DYNAMIC LIVE TICKER LOGIC
    # Note: Replace these static numbers with st.session_state.dhan.get_market_quote() calls 
    # once your API is fully authenticated.
    try:
        live_gold = "₹72,450"  # Replace with actual live fetch
        live_silver = "₹89,120" # Replace with actual live fetch
        live_crude = "₹6,430"   # Replace with actual live fetch
        
        col1, col2 = st.columns([8, 2])
        with col1:
            st.markdown(f"**Live MCX Rates:** GOLD **{live_gold}** | SILVER **{live_silver}** | CRUDE **{live_crude}**")
        with col2:
            if st.button("➕ Add Row", use_container_width=True):
                add_row_dialog()
    except Exception:
        pass
            
    # Load and display trades
    try:
        import sqlite3
        conn = sqlite3.connect('mcx_trades.db')
        df = pd.read_sql_query("SELECT pair as Pair, side as Side, status as Status, open_time as Opened, entry_price as Entry, target as Target, stop_loss as Stop, pnl as 'P/L' FROM trades", conn)
        conn.close()
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No active trades. Click 'Add Row' to generate a spread.")
            
    except Exception as e:
        st.error(f"Error loading database: {e}")

render_live_dashboard()
