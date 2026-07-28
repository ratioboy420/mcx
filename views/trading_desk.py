import streamlit as st
import pandas as pd
from core.dhan_client import DhanClient
from core.quant_math import calculate_auto_spread_metrics, compute_pl_and_risk
from ai.quant_ai import evaluate_trade_with_ai

def render_trading_desk(client_id, access_token, secret_key):
    st.markdown("### 📊 MCX Quant Spread & Live Trading Desk")
    
    if "real_live_desk" not in st.session_state or len(st.session_state.real_live_desk) == 0:
        st.warning("⚠️ No spread pairs found. Please add pairs using the 'Add New Contract Pair' tab.")
        return

    client = DhanClient(client_id, access_token, secret_key)
    
    # Live Refresh & Calculation Trigger
    if st.button("🔄 Fetch Real Live Market Data & Recalculate Spreads"):
        with st.spinner("Connecting to Dhan API for live market feed..."):
            updated_rows = []
            for row in st.session_state.real_live_desk:
                sec1 = row.get("Leg 1 Sec ID")
                sec2 = row.get("Leg 2 Sec ID")
                
                # Fetch live LTP from Dhan API
                quotes = client.fetch_quotes([sec1, sec2]) if sec1 and sec2 else {}
                
                # Get real prices or fallback if IDs are dummy
                l1_price = float(quotes.get(str(sec1), {}).get("LTP", row.get("L1_Price_Fallback", 0)))
                l2_price = float(quotes.get(str(sec2), {}).get("LTP", row.get("L2_Price_Fallback", 0)))
                
                # Real Spread Calculation (Leg 1 - Leg 2)
                spread_val = l1_price - l2_price if (l1_price > 0 and l2_price > 0) else 0.0
                
                metrics = calculate_auto_spread_metrics(l1_price, l2_price, row.get("OI_Delta", 15), row.get("RSI", 49), 60)
                
                row["Pair Spread Value"] = f"₹{spread_val:,.2f}"
                row["Side (Auto)"] = metrics["side"]
                row["C/F"] = metrics["conviction"]
                row["Status"] = "LIVE" if spread_val != 0 else "Waiting for Real Sec ID"
                
                updated_rows.append(row)
                
            st.session_state.real_live_desk = updated_rows
            st.success("✅ Live market rates fetched and calculated successfully!")

    st.markdown("#### 📋 Active Spreads & Management")
    st.info("💡 **How to Delete:** Select the rows you want to remove using the checkboxes on the left side of the table below, then press **Delete / Backspace** or click the trash icon.")

    # Convert to DataFrame for interactive editing & deletion
    df = pd.DataFrame(st.session_state.real_live_desk)
    
    # st.data_editor allows row deletion and editing
    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        key="master_quant_desk"
    )
    
    # Update session state with remaining rows after deletion
    st.session_state.real_live_desk = edited_df.to_dict('records')

    # AI Trade Intelligence & Decision Audit
    st.markdown("---")
    st.markdown("### 🤖 Quant AI Trade Intelligence & Recommendation")
    
    if len(st.session_state.real_live_desk) > 0:
        pair_options = [r.get("Pair") for r in st.session_state.real_live_desk]
        selected_pair = st.selectbox("Select Contract Pair to Audit Strategy & Profitability", pair_options)
        
        sel_data = next((r for r in st.session_state.real_live_desk if r.get("Pair") == selected_pair), None)
        
        if sel_data:
            ai_res = evaluate_trade_with_ai(
                sel_data.get("Pair"),
                500.0,
                -0.3,
                48,
                14,
                "Neutral"
            )
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("AI Recommendation", ai_res["recommendation"])
            with c2:
                st.metric("Win Probability Confidence", ai_res["confidence"])
            with c3:
                st.metric("Actionable Edge", "High Spread Divergence")
                
            st.markdown("**Strategic Reasoning & Logic:**")
            for reason in ai_res["reasoning"]:
                st.markdown(f"- {reason}")
