import streamlit as st
import datetime

def render_add_pair(client_id, access_token, secret_key):
    st.markdown("### ➕ Add Professional MCX Calendar Spread (FUT / FUT)")
    st.info("💡 **All MCX Support:** Track any commodity spread across Gold, Silver, Crude Oil, Natural Gas, Copper, and more.")
    
    with st.form("real_terminal_add_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔹 Leg 1 Contract")
            symbol_l1 = st.selectbox("Commodity", ["GOLD", "SILVER", "SILVERM", "COPPER", "CRUDEOIL", "NATURALGAS", "ALUMINIUM", "ZINC"], index=0)
            expiry_l1 = st.selectbox("Expiry Leg 1", [
                "31-Aug-2026", "05-Oct-2026", "30-Nov-2026", 
                "04-Dec-2026", "26-Feb-2027", "05-Apr-2027"
            ], index=0)
            sec_id_1 = st.text_input("Leg 1 Security ID (Dhan)", value="45123")
            
        with col2:
            st.markdown("#### 🔸 Leg 2 Contract (Hedge)")
            symbol_l2 = st.selectbox("Commodity (Hedge)", ["GOLD", "SILVER", "SILVERM", "COPPER", "CRUDEOIL", "NATURALGAS", "ALUMINIUM", "ZINC"], index=0)
            expiry_l2 = st.selectbox("Expiry Leg 2", [
                "31-Aug-2026", "05-Oct-2026", "30-Nov-2026", 
                "04-Dec-2026", "26-Feb-2027", "05-Apr-2027"
            ], index=2)
            sec_id_2 = st.text_input("Leg 2 Security ID (Dhan)", value="45124")

        st.markdown("---")
        submitted = st.form_submit_button("💾 Save Pair to Quant Desk")
        
        if submitted:
            pair_label = f"{symbol_l1} ({expiry_l1} vs {expiry_l2})"
            
            new_row = {
                "Pair": pair_label,
                "Leg 1 Sec ID": str(sec_id_1),
                "Leg 2 Sec ID": str(sec_id_2),
                "Status": "LIVE SYNC",
                "Opened": datetime.date.today().strftime("%d %b %Y"),
                "Spread Value": "₹0.00",
                "Side": "LONG",
                "Z-Score": 0.0,
                "RSI": 50.0,
                "OI Delta": "0.0%",
                "Target": 0.0,
                "Stop Loss": 0.0
            }
            
            if "real_live_desk" not in st.session_state:
                st.session_state.real_live_desk = []
            st.session_state.real_live_desk.append(new_row)
            st.success(f"✅ Successfully added **{pair_label}** to your Quant Desk!")
