
import streamlit as st
from views.dashboard import render_dashboard
from views.add_pair import render_add_pair
from core.dhan_client import DhanClient

st.set_page_config(page_title="MCX Quant Spread & Trading Desk", page_icon="📈", layout="wide")

# Sidebar Authentication & Credentials Management (3 Credentials)
st.sidebar.markdown("### 🔐 Dhan API Credentials")
st.sidebar.markdown("Enter your 3 required credentials for live market feed & WebSocket integration:")

client_id_input = st.sidebar.text_input("Client ID / Code", value="1112783972")
access_token_input = st.sidebar.text_input("Access Token (API Key)", type="password", value="")
secret_key_input = st.sidebar.text_input("Secret Key", type="password", value="")

if st.sidebar.button("Test & Connect API"):
    if client_id_input and access_token_input and secret_key_input:
        client = DhanClient(client_id_input, access_token_input, secret_key_input)
        success, msg = client.test_connection()
        if success:
            st.sidebar.success(msg)
            st.session_state.api_connected = True
        else:
            st.sidebar.error(msg)
            st.session_state.api_connected = False
    else:
        st.sidebar.warning("Please fill in all 3 credentials.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Navigation")
selected_tab = st.sidebar.radio("Go to", ["📊 Trading Desk & AI Insights", "➕ Add New Contract Pair"])

# Main execution
if selected_tab == "📊 Trading Desk & AI Insights":
    render_dashboard(client_id_input, access_token_input, secret_key_input)
elif selected_tab == "➕ Add New Contract Pair":
    render_add_pair(client_id_input, access_token_input, secret_key_input)
