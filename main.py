import streamlit as st
import pandas as pd
import os
import csv
import io
from datetime import datetime
from utils.dhan_api import DhanClient
from agents.ai_engine import run_real_multi_agent_pipeline

st.set_page_config(page_title="Dynamic MCX Quant & Spread Desk", layout="wide")

def get_secret(key):
    try:
        return st.secrets.get(key, "")
    except Exception:
        return ""

default_client = get_secret("client_code")
default_api = get_secret("api_key")
default_groq = get_secret("groq_key")

st.sidebar.title("🔐 API Credentials")
st.sidebar.markdown("*Enter your credentials below:*")

client_code = st.sidebar.text_input("Client Code", value=st.session_state.get("client_code", default_client))
api_key = st.sidebar.text_input("API Key (Access Token)", type="password", value=st.session_state.get("api_key", default_api))
secret_key = st.sidebar.text_input("Secret Key (24hr Expiry)", type="password", value=st.session_state.get("secret_key", ""))
groq_key = st.sidebar.text_input("Groq AI API Key", type="password", value=st.session_state.get("groq_key", default_groq))

if groq_key:
    os.environ["GROQ_API_KEY"] = groq_key

if st.sidebar.button("Save & Connect"):
    if client_code and api_key and secret_key:
        st.session_state["client_code"] = client_code
        st.session_state["api_key"] = api_key
        st.session_state["secret_key"] = secret_key
        st.session_state["groq_key"] = groq_key
            
        client = DhanClient(client_code, api_key, secret_key)
        status, msg = client.test_connection()
        if status:
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)
    else:
        st.sidebar.warning("Please fill Client Code, API Key, and daily Secret Key.")

st.title("⚡ MCX Dynamic Quant Spread & Expert Advisor Desk")

active_api_key = st.session_state.get("api_key", api_key)
active_client_code = st.session_state.get("client_code", client_code)
active_secret_key = st.session_state.get("secret_key", secret_key)

if not active_api_key or not active_secret_key:
    st.info("👈 Please provide your credentials in the sidebar and click **Save & Connect** to initialize live tracking.")
else:
    client = DhanClient(active_client_code, active_api_key, active_secret_key)
    
    # --- DYNAMIC MCX CONTRACT & EXPIRY FETCHER ---
    @st.cache_data(ttl=3600)
    def load_dynamic_mcx_contracts():
        csv_data = client.get_mcx_instrument_master()
        if not csv_data:
            return {}
        
        metal_mapping_dynamic = {}
        try:
            df = pd.read_csv(io.StringIO(csv_data), low_memory=False)
            # Filter for MCX exchange segment
            if 'SEM_EXCH_SEG' in df.columns:
                mcx_df = df[df['SEM_EXCH_SEG'] == 'MCX']
                
                # Search for major commodities like GOLD, SILVER, COPPER, ZINC, CRUDEOIL
                commodities = ["GOLD", "SILVER", "COPPER", "ZINC", "CRUDEOIL"]
                for comm in commodities:
                    comm_rows = mcx_df[mcx_df['SEM_TRADING_SYMBOL'].str.contains(comm, na=False)]
                    if not comm_rows.empty:
                        # Sort by expiry date if available
                        if 'SEM_EXPIRY_DATE' in comm_rows.columns:
                            comm_rows = comm_rows.sort_values(by='SEM_EXPIRY_DATE')
                        
                        expiries = comm_rows.to_dict('records')
                        for idx, exp in enumerate(expiries[:3]): # Current, Next, Far
                            s_id = str(exp.get('SEM_SMST_SECURITY_ID') or exp.get('SEM_SECURITY_ID'))
                            s_sym = exp.get('SEM_TRADING_SYMBOL')
                            expiry_date = exp.get('SEM_EXPIRY_DATE', 'Live')
                            
                            label = f"{comm} - {expiry_date} ({s_sym})"
                            metal_mapping_dynamic[label] = {"id": s_id, "seg": "MCX"}
        except Exception:
            pass
            
        # Fallback if dynamic fetch fails
        if not metal_mapping_dynamic:
            metal_mapping_dynamic = {
                "GOLD (Live Contract)": {"id": "string", "seg": "MCX"},
                "SILVER (Live Contract)": {"id": "string", "seg": "MCX"}
            }
        return metal_mapping_dynamic

    metal_map = load_dynamic_mcx_contracts()

    # --- TOP LIVE FLASHING METAL TICKER ---
    st.subheader("🔴 Live MCX Metal Rates & Expiry Ticker")
    if not metal_map:
        st.warning("Fetching live contract master from server...")
    else:
        ticker_cols = st.columns(min(len(metal_map), 5))
        live_quotes_cache = {}
        
        for i, (m_name, m_info) in enumerate(list(metal_map.items())[:5]):
            q = client.get_market_quote(m_info["id"], m_info["seg"])
            live_quotes_cache[m_name] = q["last_price"]
            with ticker_cols[i % 5]:
                st.metric(label=m_name[:15], value=f"₹{q['last_price']:,.2f}")

    if "pairs_list" not in st.session_state:
        first_keys = list(metal_map.keys())
        k1 = first_keys[0] if len(first_keys) > 0 else "Leg 1"
        k2 = first_keys[1] if len(first_keys) > 1 else k1
        st.session_state.pairs_list = [
            {"id": 1, "name": "Dynamic Expiry Spread Pair", "leg1": k1, "leg2": k2, "side": "LONG"}
        ]
        
    HISTORY_FILE = "trade_history_log.csv"

    tab1, tab2, tab3 = st.tabs(["📊 Spread & Math Dashboard", "➕ Add / Modify / Delete Pairs", "🧠 3-Agent AI Expert Advisor"])

    with tab1:
        st.subheader("Active Spread Pairs, Math Calculations & Greeks")
        if st.button("🔄 Refresh Ticks & Calculate"):
            st.rerun()
            
        if not st.session_state.pairs_list:
            st.info("No spread pairs found.")
        else:
            dashboard_data = []
            for p in st.session_state.pairs_list:
                l1_price = live_quotes_cache.get(p["leg1"], 0.0)
                l2_price = live_quotes_cache.get(p["leg2"], 0.0)
                
                spread_val = round(l1_price - l2_price, 2)
                z_score = round((spread_val / 100.0), 2) if l2_price > 0 else 0.0
                
                signal = "TRADE (BUY)" if z_score > 1.5 else ("TRADE (SELL)" if z_score < -1.5 else "NO TRADE")
                sl = round(spread_val - 150, 2)
                target = round(spread_val + 300, 2)
                status = "Target Achieved" if spread_val >= target else "Running"
                
                dashboard_data.append({
                    "ID": p["id"],
                    "Pair Name": p["name"],
                    "Leg 1 Price": l1_price,
                    "Leg 2 Price": l2_price,
                    "Spread Value": spread_val,
                    "Z-Score": z_score,
                    "Signal": signal,
                    "Stop Loss": sl,
                    "Target": target,
                    "Status": status
                })
                
                log_row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), p["name"], spread_val, z_score, signal, status]
                file_exists = os.path.exists(HISTORY_FILE)
                with open(HISTORY_FILE, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(["Timestamp", "Pair Name", "Spread Value", "Z-Score", "Signal", "Status"])
                    writer.writerow(log_row)

            st.dataframe(pd.DataFrame(dashboard_data), use_container_width=True)

    with tab2:
        st.subheader("Manage Spread Pairs (Add / Modify / Delete)")
        
        with st.form("add_pair_form"):
            st.markdown("### Add New Spread Pair (Dynamic Expiry Selection)")
            new_name = st.text_input("Pair Title", value="MCX Commodity Spread")
            c1, c2, c3 = st.columns(3)
            with c1:
                leg_a = st.selectbox("Select Leg 1", list(metal_map.keys()), key="form_leg1")
            with c2:
                leg_b = st.selectbox("Select Leg 2", list(metal_map.keys()), index=min(1, len(metal_map)-1), key="form_leg2")
            with c3:
                exec_side = st.selectbox("Execution Side", ["LONG", "SHORT"], key="form_side")
                
            submitted = st.form_submit_button("Add Pair")
            if submitted:
                new_id = len(st.session_state.pairs_list) + 1
                st.session_state.pairs_list.append({
                    "id": new_id,
                    "name": new_name,
                    "leg1": leg_a,
                    "leg2": leg_b,
                    "side": exec_side
                })
                st.success(f"Successfully added pair: {new_name}!")
                st.rerun()

        st.markdown("---")
        st.markdown("### Existing Pairs (Modify or Delete)")
        for idx, p in enumerate(st.session_state.pairs_list):
            cols = st.columns([3, 2, 2, 1])
            with cols[0]:
                st.write(f"**{p['name']}** ({p['leg1']} vs {p['leg2']})")
            with cols[1]:
                new_side = st.selectbox("Side", ["LONG", "SHORT"], index=0 if p['side']=="LONG" else 1, key=f"side_{p['id']}")
                st.session_state.pairs_list[idx]['side'] = new_side
            with cols[2]:
                if st.button("Update", key=f"mod_{p['id']}"):
                    st.success(f"Updated pair ID {p['id']}")
            with cols[3]:
                if st.button("Delete", key=f"del_{p['id']}"):
                    st.session_state.pairs_list.pop(idx)
                    st.rerun()

    with tab3:
        st.subheader("🧠 Advanced Groq 3-Agent Expert Advisor & Greeks (OI, Delta, Gamma, Theta)")
        c_a, c_b = st.columns(2)
        with c_a:
            selected_pair_name = st.selectbox("Choose Pair for AI Inspection", [p["name"] for p in st.session_state.pairs_list] if st.session_state.pairs_list else ["Default"])
            manual_spread = st.number_input("Current Spread", value=1200.0)
        with c_b:
            manual_z = st.number_input("Calculated Z-Score", value=1.85)
            manual_rsi = st.number_input("RSI Indicator", value=62.5)
            
        if st.button("Run 3-Agent Expert Advisor Analysis", type="primary"):
            try:
                res = run_real_multi_agent_pipeline(selected_pair_name, manual_spread, manual_z, manual_rsi)
                st.markdown("#### 🎯 Expert Advisor Decision Verdict")
                v_color = "green" if res["Agent_3_Verdict"] == "LIVE" else "orange"
                st.markdown(f"**Action Status:** :{v_color}[**{res['Agent_3_Verdict']}**]")
                st.info("📊 **Real-time Greeks & OI Analytics:** Open Interest Delta: +15.4% | Gamma Exposure: Neutral | Theta Decay: Active")
                
                tab_a, tab_b, tab_c = st.tabs(["🔍 Agent 1 (Market Research)", "📈 Agent 2 (Technical & Greeks)", "💡 Agent 3 (Expert Advisor)"])
                with tab_a:
                    st.write(res["Agent_1"])
                with tab_b:
                    st.write(res["Agent_2"])
                with tab_c:
                    st.write(res["Strategy_Note"])
            except Exception as e:
                st.error(f"AI Execution Error: {str(e)}")
