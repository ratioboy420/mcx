import streamlit as st
import pandas as pd
import os
from utils.dhan_api import DhanClient
from agents.ai_engine import run_real_multi_agent_pipeline

st.set_page_config(page_title="Real MCX Quant & Spread Desk", layout="wide")

# --- SIDEBAR: Credentials Setup ---
st.sidebar.title("🔐 API Credentials Setup")
client_code = st.sidebar.text_input("Dhan Client Code", value=st.session_state.get("client_code", ""))
api_key = st.sidebar.text_input("Dhan API Key (Access Token)", type="password", value=st.session_state.get("api_key", ""))
secret_key = st.sidebar.text_input("Dhan Secret Key", type="password", value=st.session_state.get("secret_key", ""))
groq_input = st.sidebar.text_input("Groq AI API Key", type="password", value=st.session_state.get("groq_key", ""))

if st.sidebar.button("Save & Connect"):
    if client_code and api_key and secret_key:
        st.session_state["client_code"] = client_code
        st.session_state["api_key"] = api_key
        st.session_state["secret_key"] = secret_key
        if groq_input:
            st.session_state["groq_key"] = groq_input
            os.environ["GROQ_API_KEY"] = groq_input
            
        client = DhanClient(client_code, api_key, secret_key)
        status, msg = client.test_connection()
        if status:
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)
    else:
        st.sidebar.warning("Please fill all Dhan credentials.")

st.title("⚡ Real-Time MCX Spread Trading & AI Desk")

if not st.session_state.get("api_key"):
    st.info("👈 Please enter your 3 Dhan API credentials in the sidebar to activate the terminal.")
else:
    client = DhanClient(
        st.session_state["client_code"],
        st.session_state["api_key"],
        st.session_state["secret_key"]
    )
    
    # Initialize Session State for Spread Pairs
    if "spread_pairs" not in st.session_state:
        st.session_state.spread_pairs = [
            {"Pair": "GOLD Aug/Oct", "Leg 1 ID": "13327", "Leg 2 ID": "13328", "Status": "ACTIVE"}
        ]

    # --- TAB NAVIGATION FOR ALL FEATURES ---
    tab1, tab2, tab3 = st.tabs(["📊 Live Spreads & Ticker", "➕ Add Spread Pair", "🧠 Groq 3-Agent AI Inspector"])

    with tab1:
        st.subheader("Live MCX Spread Monitor")
        if st.button("Refresh Market Ticks"):
            st.rerun()
            
        display_list = []
        for pair in st.session_state.spread_pairs:
            l1_rate = client.get_live_market_data(pair["Leg 1 ID"])
            l2_rate = client.get_live_market_data(pair["Leg 2 ID"])
            display_list.append({
                "Spread Pair": pair["Pair"],
                "Leg 1 LTP": l1_rate,
                "Leg 2 LTP": l2_rate,
                "Status": pair["Status"]
            })
        st.dataframe(pd.DataFrame(display_list), use_container_width=True)

    with tab2:
        st.subheader("Add Custom MCX Spread Pair")
        with st.form("add_pair_form"):
            p_name = st.text_input("Spread Pair Name (e.g. SILVER Sep/Dec)", value="SILVER Sep/Dec")
            c1, c2 = st.columns(2)
            with c1:
                id1 = st.text_input("Leg 1 Security ID (e.g. 13348 for SILVER)", value="13348")
            with c2:
                id2 = st.text_input("Leg 2 Security ID (e.g. 13349 for SILVERM)", value="13349")
            
            submitted = st.form_submit_button("Save & Track Pair")
            if submitted:
                if p_name and id1 and id2:
                    st.session_state.spread_pairs.append({
                        "Pair": p_name,
                        "Leg 1 ID": id1.strip(),
                        "Leg 2 ID": id2.strip(),
                        "Status": "ACTIVE"
                    })
                    st.success(f"Successfully added {p_name} to tracking list!")
                else:
                    st.error("Please fill all details.")

    with tab3:
        st.subheader("Groq Multi-Agent AI Inspector & Result Dashboard")
        col_a, col_b = st.columns(2)
        with col_a:
            p_symbol = st.text_input("Pair Symbol", value="SILVER-SILVERM")
            spread_val = st.number_input("Spread Value", value=1450.0)
        with col_b:
            z_val = st.number_input("Z-Score", value=2.25)
            rsi_val = st.number_input("RSI", value=65.0)
            
        if st.button("Run 3-Agent AI Pipeline", type="primary"):
            try:
                result = run_real_multi_agent_pipeline(p_symbol, spread_val, z_val, rsi_val)
                st.markdown("#### 🎯 Execution Results")
                v_color = "green" if result["Agent_3_Verdict"] == "LIVE" else "orange"
                st.markdown(f"**Final Verdict:** :{v_color}[**{result['Agent_3_Verdict']}**]")
                
                t1, t2, t3 = st.tabs(["🔍 Agent 1 (Researcher)", "📈 Agent 2 (Technical)", "💡 Agent 3 (Expert Advisor)"])
                with t1:
                    st.write(result["Agent_1"])
                with t2:
                    st.write(result["Agent_2"])
                with t3:
                    st.write(result["Strategy_Note"])
            except Exception as ex:
                st.error(f"AI Execution Error: {str(ex)}")
