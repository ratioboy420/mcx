import streamlit as st
import datetime

def render_add_pair(client_id, access_token, secret_key):
    st.markdown("### ➕ Add Professional Calendar Spread (FUT / FUT)")
    st.info("💡 **Instructions:** Enter actual MCX Security IDs from your terminal/broker for real-time spread tracking.")
    
    with st.form("real_terminal_add_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔹 Leg 1 Contract")
            symbol_l1 = st.selectbox("Commodity", ["GOLD", "SILVER", "SILVERM", "COPPER", "CRUDEOIL", "NATURALGAS"], index=2)
            expiry_l1 = st.selectbox("Expiry Leg 1", [
                "31-Aug-2026", "05-Oct-2026", "30-Nov-2026", 
                "04-Dec-2026", "26-Feb-2027", "05-Apr-2027", "04-Jun-2027"
            ], index=2)
            sec_id_l1 = st.text_input("Leg 1 Security ID (Dhan)", value="")
            
        with col2:
            st.markdown("#### 🔸 Leg 2 Contract (Hedge)")
            st.markdown("&nbsp;")
            expiry_l2 = st.selectbox("Expiry Leg 2", [
                "31-Aug-2026", "05-Oct-2026", "30-Nov-2026", 
                "04-Dec-2026", "26-Feb-2027", "05-Apr-2027", "04-Jun-2027"
            ], index=4)
            sec_id_l2 = st.text_input("Leg 2 Security ID (Dhan)", value="")

        st.markdown("---")
        submitted = st.form_submit_button("💾 Save Pair to Quant Desk")
        
        if submitted:
            if not sec_id_l1 or not sec_id_l2:
                st.error("❌ Please enter valid Security IDs for both legs.")
                return
                
            pair_label = f"{symbol_l1} ({expiry_l1} vs {expiry_l2})"
            
            new_row = {
                "Pair": pair_label,
                "Leg 1 Sec ID": sec_id_l1.strip(),
                "Leg 2 Sec ID": sec_id_l2.strip(),
                "Status": "Ready",
                "Opened": datetime.date.today().strftime("%d %b %Y"),
                "Spread Value": "₹0.00",
                "Side": "LONG",
                "Z-Score": -0.4,
                "RSI": 50,
                "Target": 0.0,
                "Stop Loss": 0.0
            }
            
            if "real_live_desk" not in st.session_state:
                st.session_state.real_live_desk = []
            st.session_state.real_live_desk.append(new_row)
            st.success(f"✅ Successfully added **{pair_label}**!")
