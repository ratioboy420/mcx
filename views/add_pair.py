
import streamlit as st
import datetime

def render_add_pair(client_id, access_token, secret_key):
    st.markdown("### ➕ Add New MCX Contract Pair (All Commodities)")
    
    with st.form("add_contract_form"):
        col1, col2 = st.columns(2)
        with col1:
            commodity = st.selectbox("Commodity", ["GOLD", "SILVER", "COPPER", "ALUMINIUM", "CRUDEOIL", "ZINC", "NATURALGAS"])
            leg1_name = st.text_input("Leg 1 Symbol", value="COPPER-31Aug2026-FUT")
            leg1_sec_id = st.text_input("Leg 1 Security ID (Dhan)", value="568831")
            l1_fallback = st.number_input("Leg 1 Base Price Fallback", value=75000.0)
        with col2:
            side = st.selectbox("Trade Side", ["LONG", "SHORT"])
            leg2_name = st.text_input("Leg 2 Symbol", value="COPPER-30Sep2026-FUT")
            leg2_sec_id = st.text_input("Leg 2 Security ID (Dhan)", value="571298")
            l2_fallback = st.number_input("Leg 2 Base Price Fallback", value=75500.0)
            
        col3, col4, col5 = st.columns(3)
        with col3:
            entry_price = st.number_input("Entry Spread Price (₹)", value=500.0)
        with col4:
            status = st.selectbox("Initial Status", ["LIVE", "pending"])
        with col5:
            expiry_days = st.number_input("Expiry Distance (Days)", value=52)
            
        submitted = st.form_submit_button("Save Contract Pair to Desk")
        if submitted:
            pair_str = f"{commodity} ({leg1_name} vs {leg2_name})"
            new_row = {
                "Pair": pair_str,
                "Leg 1 Sec ID": leg1_sec_id,
                "Leg 2 Sec ID": leg2_sec_id,
                "L1_Price_Fallback": l1_fallback,
                "L2_Price_Fallback": l2_fallback,
                "Side": side,
                "Status": status,
                "Opened": datetime.date.today().strftime("%d %b %Y"),
                "Entry": entry_price,
                "Target": entry_price * 1.04,
                "Stop": entry_price * 0.98,
                "C/F": "1/3",
                "Z_Score": -0.3,
                "RSI": 48,
                "OI_Delta": 14,
                "Expiry_Days": expiry_days,
                "Pair Spread Value": f"₹{abs(l1_fallback - l2_fallback):,.2f}",
                "P/L": "—"
            }
            
            if "real_live_desk" not in st.session_state:
                st.session_state.real_live_desk = []
            st.session_state.real_live_desk.append(new_row)
            st.success(f"✅ Successfully added {pair_str} to your live MCX spread desk!")
