import streamlit as st
import pandas as pd
from utils.dhan_api import DhanClient

st.set_page_config(page_title="All MCX Spread Tracker", layout="wide")

st.sidebar.title("🔐 Dhan API Credentials")
client_code = st.sidebar.text_input("Client Code", value="")
api_key = st.sidebar.text_input("API Key (Access Token)", type="password", value="")
secret_key = st.sidebar.text_input("Secret Key", type="password", value="")

connect_btn = st.sidebar.button("Connect & Initialize")

st.title("📈 All MCX Live Spread & Quant Desk")

if not api_key or not client_code or not secret_key:
    st.info("👈 Please enter your Client Code, API Key, and Secret Key in the sidebar to view live MCX data.")
else:
    try:
        client = DhanClient(client_code, api_key, secret_key)
        
        if connect_btn:
            with st.spinner("Verifying connection..."):
                status, msg = client.test_connection()
                if status:
                    st.sidebar.success(msg)
                else:
                    st.sidebar.error(msg)
        
        st.subheader("Live Tracking: All MCX Spread & Commodity Feed")
        
        if st.button("Refresh Live Market Data"):
            st.rerun()
            
        with st.spinner("Fetching all MCX market spreads..."):
            data = client.get_all_mcx_spreads()
            if data:
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No data retrieved from exchange.")
                
    except Exception as e:
        st.error(f"Application Runtime Error: {str(e)}")
