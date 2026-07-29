import streamlit as st
import pandas as pd
import datetime
from datetime import timedelta
from dhanhq import dhanhq

st.set_page_config(page_title="MCX Live Terminal", layout="wide")

# 1. Automatic Scrip Master Fetcher
@st.cache_data(ttl=3600)
def load_mcx_scrip_master():
    url = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
    df = pd.read_csv(url, low_memory=False)
    mcx_fut = df[(df['SEM_EXM_EXCH_ID'] == 'MCX') & (df['SEM_INSTRUMENT_NAME'] == 'FUTCOM')].copy()
    return mcx_fut

st.title("⚡ MCX Live Rate Terminal")

# Fetch Master Data
try:
    mcx_data = load_mcx_scrip_master()
    st.success("✅ Live MCX Scrip Master Loaded Successfully!")
    
    # Filter Gold & Silver contracts
    metals = ["GOLD", "SILVER", "COPPER", "CRUDEOIL"]
    selected = st.selectbox("Select Commodity", metals)
    
    filtered = mcx_data[mcx_data['SEM_TRADING_SYMBOL'].str.startswith(selected, na=False)]
    
    st.write("### Active Contracts & Security IDs:")
    st.dataframe(filtered[['SEM_TRADING_SYMBOL', 'SEM_SMST_SECURITY_ID', 'SEM_EXPIRY_DATE']], use_container_width=True)

except Exception as e:
    st.error(f"Error loading master data: {e}")
