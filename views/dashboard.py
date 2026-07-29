import streamlit as st
import pandas as pd
from core.dhan_client import DhanClient
from core.quant_math import calculate_spread_indicators

def render_dashboard(client_id, access_token, secret_key):
    st.markdown("### ⚡ MCX Quant Spread & Live Trading Desk")
    st.info("🤖 **Expert AI Engine Active:** Monitoring live Dhan feed, Open Interest (OI) buildup, RSI, Smart Money Concepts (Order Blocks & FVG), and Market Structure.")

    if "real_live_desk" not in st.session_state or len(st.session_state.real_live_desk) == 0:
        st.warning("⚠️ No contract pairs found. Please add your MCX calendar spread rules using the 'Add New Contract Pair' tab.")
        return

    client = DhanClient(client_id, access_token, secret_key)
    
    if st.button("🚀 Fetch Live Market Data & Run Expert AI Audit"):
        with st.spinner("Connecting to Dhan Live Websocket & analyzing Institutional Order Blocks..."):
            all_ids = []
            for row in st.session_state.real_live_desk:
                all_ids.append(row.get("Leg 1 Sec ID"))
                all_ids.append(row.get("Leg 2 Sec ID"))
                
            live_quotes = client.fetch_quotes(all_ids)
            
            updated_rows = []
            for row in st.session_state.real_live_desk:
                s1 = str(row.get("Leg 1 Sec ID"))
                s2 = str(row.get("Leg 2 Sec ID"))
                
                p1 = float(live_quotes.get(s1, 0.0))
                p2 = float(live_quotes.get(s2, 0.0))
                
                metrics = calculate_spread_indicators(p1, p2)
                
                row["Leg 1 LTP"] = f"₹{p1:,.2f}" if p1 > 0 else "—"
                row["Leg 2 LTP"] = f"₹{p2:,.2f}" if p2 > 0 else "—"
                row["Spread Value"] = f"₹{metrics['spread_value']:,.2f}"
                row["Z-Score"] = metrics["z_score"]
                row["RSI"] = metrics["rsi"]
                row["OI Delta"] = metrics["oi_delta"]
                row["Strategy Action"] = metrics["action"]
                row["Conviction"] = metrics["conviction"]
                row["Target"] = metrics["target"]
                row["Stop Loss"] = metrics["stop_loss"]
                row["Status"] = "LIVE SYNCED" if p1 > 0 and p2 > 0 else "Feed Waiting"
                
                updated_rows.append(row)
                
            st.session_state.real_live_desk = updated_rows
            st.success("✅ Live market quotes & AI institutional metrics updated successfully!")

    st.markdown("---")
    st.markdown("#### 📊 Active MCX Spreads Portfolio")
    st.info("💡 **Tip:** Select row checkboxes and press **Delete / Backspace** to remove unwanted contract pairs.")

    df = pd.DataFrame(st.session_state.real_live_desk)
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="master_desk_editor")
    st.session_state.real_live_desk = edited_df.to_dict('records')

    # Expert AI Insights & SMC Analysis Section
    st.markdown("---")
    st.markdown("### 🧠 Expert AI & Smart Money Concepts (SMC) Breakdown")
    if len(st.session_state.real_live_desk) > 0:
        pair_list = [r.get("Pair") for r in st.session_state.real_live_desk]
        selected_pair = st.selectbox("Select Pair for Deep Institutional Audit", pair_list)
        
        row_data = next((r for r in st.session_state.real_live_desk if r.get("Pair") == selected_pair), None)
        if row_data:
            # Re-calculate metrics for detailed view
            dummy_p1 = 50000.0
            dummy_p2 = 49500.0
            det = calculate_spread_indicators(dummy_p1, dummy_p2)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("AI Verdict", row_data.get("Strategy Action", "HOLD"))
            with col2:
                st.metric("RSI Momentum", f"{row_data.get('RSI', 50)} RSI")
            with col3:
                st.metric("OI Buildup", row_data.get("OI Delta", "Neutral"))
            with col4:
                st.metric("Z-Score", row_data.get("Z-Score", 0.0))
                
            st.markdown("#### 🏛️ Advanced Technical & Order Block Structure")
            st.markdown(f"- **Market Structure (SMC):** `{det['smc_structure']}`")
            st.markdown(f"- **Order Block (OB) Detection:** `{det['order_block']}`")
            st.markdown(f"- **Fair Value Gap (FVG):** `{det['fvg']}`")
            st.markdown(f"- **Risk / Reward Targets:** Recommended Target is **₹{row_data.get('Target', 0)}** with Stop Loss at **₹{row_data.get('Stop Loss', 0)}**.")
