import streamlit as st
import pandas as pd
from utils.dhan_api import DhanLiveClient
from agents.ai_engine import run_real_multi_agent_pipeline

st.set_page_config(page_title="MCX Quant & Spread Desk", page_icon="⚡", layout="wide")

# --- SIDEBAR: 3 Dhan Credentials ---
st.sidebar.title("🔐 Dhan API Credentials")
client_code = st.sidebar.text_input("Client Code", value=st.session_state.get("client_code", ""))
api_key = st.sidebar.text_input("API Key (Access Token)", type="password", value=st.session_state.get("api_key", ""))
secret_key = st.sidebar.text_input("Secret Key", type="password", value=st.session_state.get("secret_key", ""))

if st.sidebar.button("Save & Connect"):
    if client_code and api_key and secret_key:
        st.session_state["client_code"] = client_code
        st.session_state["api_key"] = api_key
        st.session_state["secret_key"] = secret_key
        
        # Test connection
        client = DhanLiveClient(client_code, api_key, secret_key)
        res = client.verify_account_connection()
        if res["status"] == "connected":
            st.sidebar.success(res["message"])
        else:
            st.sidebar.error(res["message"])
    else:
        st.sidebar.warning("Please fill all 3 credentials!")

st.title("⚡ Real-Time Quant Trading & Live MCX Spread Desk")

# Check if connected
if not st.session_state.get("api_key"):
    st.info("👈 Please enter your 3 Dhan API credentials in the sidebar and click 'Save & Connect' to start.")
else:
    client = DhanLiveClient(
        st.session_state["client_code"], 
        st.session_state["api_key"], 
        st.session_state["secret_key"]
    )
    
    # Connection Banner
    conn_status = client.verify_account_connection()
    if conn_status["status"] == "connected":
        st.success("Status: Dhan Account Successfully Connected!")
    else:
        st.error(f"Connection Failed: {conn_status['message']}")

    # --- SECTION 1: Live MCX Metal Rates & All Spreads ---
    st.markdown("### 📊 Live MCX Metal Rates & All Spreads Ticker")
    with st.spinner("Fetching live rates from MCX..."):
        rates_data = client.get_live_metal_rates()
        if rates_data:
            df_rates = pd.DataFrame(rates_data)
            st.table(df_rates)
        else:
            st.warning("No live data returned from MCX feed.")

    # --- SECTION 2: Add Custom Spread Pair ---
    st.markdown("---")
    st.markdown("### ➕ Add Custom MCX Spread Pair")
    col1, col2, col3 = st.columns(3)
    with col1:
        leg1 = st.selectbox("Leg 1 Commodity", ["GOLD", "GOLDM", "SILVER", "SILVERM", "COPPER", "ZINC", "CRUDEOIL"])
    with col2:
        leg2 = st.selectbox("Leg 2 Commodity", ["GOLDM", "SILVER", "SILVERM", "COPPER", "ZINC", "CRUDEOIL", "GOLD"])
    with col3:
        spread_type = st.selectbox("Spread Type", ["Near-Next Month Spread", "Ratio Spread", "Inter-Commodity Spread"])
    
    if st.button("Add & Monitor Pair"):
        st.success(f"Successfully added spread pair: **{leg1} vs {leg2}** ({spread_type}) for live tracking!")

    # --- SECTION 3: Real Groq 3-Agent AI Inspector & Result Dashboard ---
    st.markdown("---")
    st.markdown("### 🧠 Real Groq 3-Agent AI Inspector & Result Dashboard")
    
    col_a, col_b = st.columns(2)
    with col_a:
        pair_symbol = st.text_input("Enter Spread Pair Symbol (e.g. SILVERM-SILVER)", value="SILVERM-SILVER")
        current_spread = st.number_input("Current Spread Value", value=1250.50)
    with col_b:
        z_score = st.number_input("Calculated Z-Score", value=2.15)
        rsi = st.number_input("RSI Indicator", value=68.4)

    if st.button("Run AI Multi-Agent Pipeline"):
        with st.spinner("Running 3-Agent Quant Analysis via Groq AI..."):
            try:
                pipeline_result = run_real_multi_agent_pipeline(pair_symbol, current_spread, z_score, rsi)
                
                st.markdown("#### 🎯 Execution Verdict & Reports")
                verdict_color = "green" if pipeline_result["Agent_3_Verdict"] == "LIVE" else "orange"
                st.markdown(f"**Final Verdict:** :{verdict_color}[**{pipeline_result['Agent_3_Verdict']}**]")
                
                tab1, tab2, tab3 = st.tabs(["🔍 Agent 1 (Researcher)", "📈 Agent 2 (Technical)", "💡 Agent 3 (Expert Advisor)"])
                with tab1:
                    st.write(pipeline_result["Agent_1"])
                with tab2:
                    st.write(pipeline_result["Agent_2"])
                with tab3:
                    st.write(pipeline_result["Strategy_Note"])
            except Exception as e:
                st.error(f"AI Execution Error: {str(e)}")
