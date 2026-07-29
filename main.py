import streamlit as st
import pandas as pd
from utils.dhan_api import DhanLiveClient

st.set_page_config(page_title="Real MCX Spread & Quant Desk", layout="wide")

st.sidebar.title("🔐 Dhan API Credentials")
client_code = st.sidebar.text_input("Client Code", value=st.session_state.get("client_code", ""))
api_key = st.sidebar.text_input("API Key (Access Token)", type="password", value=st.session_state.get("api_key", ""))
secret_key = st.sidebar.text_input("Secret Key", type="password", value=st.session_state.get("secret_key", ""))

if st.sidebar.button("Connect Account"):
    if client_code and api_key and secret_key:
        st.session_state["client_code"] = client_code
        st.session_state["api_key"] = api_key
        st.session_state["secret_key"] = secret_key
        
        client = DhanLiveClient(client_code, api_key, secret_key)
        res = client.verify_account_connection()
        if res["status"] == "connected":
            st.sidebar.success(res["message"])
        else:
            st.sidebar.error(res["message"])
    else:
        st.sidebar.warning("Enter all 3 credentials!")

st.title("⚡ Real MCX Spread Tracking & Execution Desk")

if not st.session_state.get("api_key"):
    st.warning("⚠️ Please provide your 3 Dhan credentials in the sidebar to load the live system.")
else:
    client = DhanLiveClient(
        st.session_state["client_code"], 
        st.session_state["api_key"], 
        st.session_state["secret_key"]
    )

    # Initialize Session State for Spreads Management
    if "spread_pairs" not in st.session_state:
        st.session_state.spread_pairs = [
            {"Pair": "GOLD Aug/Oct", "Security ID 1": "13327", "Security ID 2": "13328", "Side": "SHORT", "Status": "LIVE"}
        ]

    # --- TAB NAVIGATION ---
    tab1, tab2 = st.tabs(["📊 Live Spreads Dashboard", "➕ Add New Spread Pair"])

    with tab1:
        st.subheader("Active MCX Spread Monitor")
        if not st.session_state.spread_pairs:
            st.info("No spread pairs added yet. Use the 'Add New Spread Pair' tab.")
        else:
            display_data = []
            for item in st.session_state.spread_pairs:
                tick1 = client.get_live_market_data(item["Security ID 1"])
                tick2 = client.get_live_market_data(item["Security ID 2"])
                
                ltp1 = tick1.get("last_price", 0.0) if tick1 else "N/A"
                ltp2 = tick2.get("last_price", 0.0) if tick2 else "N/A"
                
                display_data.append({
                    "Pair Spread": item["Pair"],
                    "Leg 1 LTP": ltp1,
                    "Leg 2 LTP": ltp2,
                    "Side": item["Side"],
                    "Status": item["Status"]
                })
            
            st.dataframe(pd.DataFrame(display_data), use_container_width=True)

    with tab2:
        st.subheader("Configure & Add Spread Pair")
        with st.form("add_pair_form"):
            pair_name = st.text_input("Pair Name (e.g., SILVER Sep/Dec)", value="SILVER Sep/Dec")
            col1, col2 = st.columns(2)
            with col1:
                sec_id_1 = st.text_input("Leg 1 Security ID (e.g. 13348 for SILVER)", value="13348")
            with col2:
                sec_id_2 = st.text_input("Leg 2 Security ID (e.g. 13349 for SILVERM)", value="13349")
            
            side = st.selectbox("Execution Side", ["LONG", "SHORT"])
            submitted = st.form_submit_button("Add Pair to Tracker")
            
            if submitted:
                if pair_name and sec_id_1 and sec_id_2:
                    new_entry = {
                        "Pair": pair_name,
                        "Security ID 1": sec_id_1.strip(),
                        "Security ID 2": sec_id_2.strip(),
                        "Side": side,
                        "Status": "LIVE"
                    }
                    st.session_state.spread_pairs.append(new_entry)
                    st.success(f"Successfully added {pair_name} to live monitoring dashboard!")
                else:
                    st.error("Please fill all required fields correctly.")
