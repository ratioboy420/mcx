import streamlit as st
import pandas as pd
import time
from database import init_db, save_trade

# --- PAGE CONFIG ---
st.set_page_config(page_title="Dynamic MCX Quant Desk", layout="wide")

# Initialize Database
init_db()

# --- 1. SECURE CONNECTION (No Drops) ---
@st.cache_resource
def connect_dhan(client_id, access_token):
    # Yahan DhanClient initialize hoga. Caching ki wajah se bar bar reload nahi hoga.
    # from dhanhq import dhanhq
    # return dhanhq(client_id, access_token)
    return "Connected to Dhan" # Placeholder

# --- 2. SIDEBAR LOGIN ---
with st.sidebar:
    st.header("🔑 API Login")
    client_id = st.text_input("Dhan Client ID", type="password")
    access_token = st.text_input("Access Token", type="password")
    
    if st.button("Connect"):
        if client_id and access_token:
            st.session_state.dhan = connect_dhan(client_id, access_token)
            st.success("Connected!")
        else:
            st.error("Please enter credentials.")

# --- 3. ADD ROW POP-UP (Dialog) ---
@st.dialog("➕ Add New Strategy Leg")
def add_row_dialog():
    st.write("Select Metal to generate FUT to FUT Pair")
    metal = st.selectbox("Metal", ["GOLD", "SILVER", "CRUDEOIL", "COPPER"])
    
    if st.button("Generate Pair"):
        # Yahan hum current aur next expiry auto-fetch karenge
        pair_name = f"{metal} Current / Next Expiry"
        save_trade(pair_name, "LONG", "pending", 0.0, 0.0, 0.0)
        st.success(f"{pair_name} added to Dashboard!")
        st.rerun()

# --- 4. LIVE DASHBOARD (Using Fragment to prevent full page reload) ---
@st.fragment(run_every=5) # Refreshes every 5 seconds
def render_live_dashboard():
    st.subheader("📊 Live Pair Spread Desk")
    
    # Header buttons
    col1, col2 = st.columns([8, 2])
    with col1:
        st.markdown("**Live Ticker:** GOLD ₹72,000 | SILVER ₹89,500 | CRUDE ₹6,500")
    with col2:
        if st.button("➕ Add Row", use_container_width=True):
            add_row_dialog()
            
    # Fetch from DB and display (Simulating your layout)
    try:
        import sqlite3
        conn = sqlite3.connect('mcx_trades.db')
        df = pd.read_sql_query("SELECT pair as Pair, side as Side, status as Status, open_time as Opened, entry_price as Entry, target as Target, stop_loss as Stop, pnl as 'P/L' FROM trades", conn)
        conn.close()
        
        if not df.empty:
            # Custom styling from our previous discussion
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No active trades. Click 'Add Row' to start.")
            
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

# Call the dashboard
render_live_dashboard()
