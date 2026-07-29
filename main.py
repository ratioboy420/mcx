import streamlit as st
from views.dashboard import render_dashboard
from views.add_pair import render_add_pair
from core.dhan_client import DhanClient

st.set_page_config(page_title="MCX Quant & AI Trading Desk", page_icon="⚡", layout="wide")

st.sidebar.markdown("## 🔐 Dhan API Credentials")
st.sidebar.info("Enter your 3 required credentials for live market feed & WebSocket integration:")

client_id_input = st.sidebar.text_input("Client ID / Code", value="1112783972")
access_token_input = st.sidebar.text_input("Access Token (API Key)", type="password")
secret_key_input = st.sidebar.text_input("Secret Key", type="password")

if st.sidebar.button("Test & Connect API"):
    client = DhanClient(client_id_input, access_token_input, secret_key_input)
    success, msg = client.test_connection()
    if success:
        st.sidebar.success(msg)
    else:
        st.sidebar.error(msg)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Navigation")
nav_choice = st.sidebar.radio("Go to", ["Trading Desk & AI Insights", "Add New Contract Pair"])

if nav_choice == "Trading Desk & AI Insights":
    render_dashboard(client_id_input, access_token_input, secret_key_input)
else:
    render_add_pair(client_id_input, access_token_input, secret_key_input)
