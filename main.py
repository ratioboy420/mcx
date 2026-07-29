import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import csv
from datetime import datetime
from utils.dhan_api import DhanClient
from utils.instruments import MCX_INSTRUMENTS, get_instrument_names
from agents.ai_engine import run_real_multi_agent_pipeline

# ... (baki credentials code same rahega) ...

if active_api_key and active_secret_key:
    client = DhanClient(active_client_code, active_api_key, active_secret_key)
    
    # Ab metal_map manual likhne ki jagah instruments.py se auto-load hoga
    metal_map = MCX_INSTRUMENTS

    # --- TOP LIVE FLASHING METAL TICKER ---
    st.subheader("🔴 Live MCX Metal Rates & Expiry Ticker")
    
    # Dropdown to select tickers to show on header
    selected_tickers = st.multiselect(
        "Select Metals to display on Top Ticker:",
        options=get_instrument_names(),
        default=["GOLD (Current Expiry)", "SILVER (Current Expiry)", "COPPER", "CRUDEOIL (Current Expiry)"]
    )
    
    if selected_tickers:
        ticker_cols = st.columns(len(selected_tickers))
        live_quotes_cache = {}
        
        for i, m_name in enumerate(selected_tickers):
            m_info = metal_map[m_name]
            q = client.get_market_quote(m_info["id"], m_info["seg"])
            price = q.get("last_price", 0.0)
            live_quotes_cache[m_name] = price
            with ticker_cols[i]:
                st.metric(label=m_name, value=f"₹{price:,.2f}")
