import streamlit as st
import pandas as pd
from utils.dhan_api import DhanLiveClient
from agents.ai_engine import run_real_multi_agent_pipeline

st.set_page_config(page_title="Real Quant Trading & Live Metal Ticker Desk", layout="wide")

st.sidebar.markdown("### 🔐 Dhan API Credentials")
client_code = st.sidebar.text_input("Client Code", type="default")
api_key = st.sidebar.text_input("API Key (Access Token)", type="password")
secret_key = st.sidebar.text_input("Secret Key", type="password")

st.markdown("### ⚡ Real-Time Quant Trading & Live Metal Desk")

if not client_code or not api_key or not secret_key:
    st.warning("⚠️ Please enter all **3 API credentials** in the sidebar to verify your Dhan account connection and view live metal rates.")
else:
    # Initialize real Dhan client
    dhan = DhanLiveClient(client_code, api_key, secret_key)
    
    # 1. Verify Connection Status
    with st.spinner("Verifying Dhan account connection..."):
        conn_status = dhan.verify_account_connection()
        
    if conn_status["status"] == "connected":
        st.success(f"✅ **Status:** {conn_status['message']}")
    else:
        st.error(f"❌ **Status:** {conn_status['message']}")
        st.stop()

    st.markdown("---")
    
    # 2. Live Metal Rates Ticker Column (Connection & Feed Monitor)
    st.markdown("#### 📈 Live MCX Metal Rates Ticker (All Commodities Feed)")
    
    with st.spinner("Fetching live metal rates from Dhan..."):
        metal_rates = dhan.get_live_metal_rates()
        
    cols = st.columns(len(metal_rates))
    for idx, metal in enumerate(metal_rates):
        with cols[idx]:
            st.metric(label=metal["Commodity"], value=str(metal["Live Rate"]))

    st.markdown("---")
    
    # 3. Real Multi-Agent AI Core Section
    st.markdown("### 🧠 Real Groq 3-Agent AI Inspector")
    
    c1, c2 = st.columns(2)
    with c1:
        target_pair = st.text_input("Enter Spread Pair Symbol", value="GOLD_AUG_OCT")
        spread_input = st.number_input("Current Spread Value", value=3474.0)
    with c2:
        z_input = st.number_input("Calculated Z-Score", value=0.42)
        rsi_input = st.number_input("Calculated RSI", value=48.5)

    if st.button("Run Real 3-Agent Analysis", type="primary"):
        with st.spinner("Executing real multi-agent pipeline via Groq..."):
            try:
                analysis = run_real_multi_agent_pipeline(target_pair, spread_input, z_input, rsi_input)
                
                st.markdown("#### 🤖 Execution Results")
                st.success(f"**Agent 1 (Researcher):**\n{analysis['Agent_1']}")
                st.info(f"**Agent 2 (Technical Analyst):**\n{analysis['Agent_2']}")
                st.warning(f"**Agent 3 Expert Verdict [{analysis['Agent_3_Verdict']}]:**\n{analysis['Strategy_Note']}")
            except Exception as ai_err:
                st.error(f"AI Execution Error: {str(ai_err)}")
