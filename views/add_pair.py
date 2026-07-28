import streamlit as st
import datetime

def render_add_pair(client_id, access_token, secret_key):
    st.markdown("### ➕ Add Calendar Spread Rule (FUT / FUT)")
    st.info("💡 **Motive:** Yahan aap apne calendar spread pairs add karte hain taaki AI scanner unhe live track karke bata sake ki kisme profit banega.")
    
    with st.form("terminal_add_pair_form"):
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("#### 🔹 Leg 1 Contract")
            symbol_l1 = st.selectbox("Commodity Symbol", ["GOLD", "SILVER", "SILVERM", "COPPER", "CRUDEOIL", "NATURALGAS"], index=2)
            expiry_l1 = st.selectbox("Expiry Leg 1", [
                "31-Aug-2026", "05-Oct-2026", "30-Nov-2026", 
                "04-Dec-2026", "26-Feb-2027", "05-Apr-2027", "04-Jun-2027"
            ], index=2)
            sec_id_l1 = st.text_input("Leg 1 Security ID (Dhan)", value="500123")
            
        with col_c2:
            st.markdown("#### 🔸 Leg 2 Contract (Hedge)")
            st.markdown("&nbsp;")
            expiry_l2 = st.selectbox("Expiry Leg 2", [
                "31-Aug-2026", "05-Oct-2026", "30-Nov-2026", 
                "04-Dec-2026", "26-Feb-2027", "05-Apr-2027", "04-Jun-2027"
            ], index=4)
            sec_id_l2 = st.text_input("Leg 2 Security ID (Dhan)", value="500124")

        st.markdown("---")
        submitted = st.form_submit_button("💾 Add Spread Pair to AI Scanner Desk")
        
        if submitted:
            pair_label = f"{symbol_l1} ({expiry_l1} vs {expiry_l2})"
            
            new_row = {
                "Pair": pair_label,
                "Leg 1 Sec ID": sec_id_l1.strip(),
                "Leg 2 Sec ID": sec_id_l2.strip(),
                "Status": "Pending Scan",
                "Opened": datetime.date.today().strftime("%d %b %Y"),
                "Pair Spread Value": "₹0.00",
                "Side (Auto)": "LONG",
                "C/F (Conviction)": "Pending",
                "Target": 0.0,
                "Stop": 0.0,
                "Holding Time": "60 Days",
                "P/L": "—"
            }
            
            if "real_live_desk" not in st.session_state:
                st.session_state.real_live_desk = []
            st.session_state.real_live_desk.append(new_row)
            st.success(f"✅ Added **{pair_label}** successfully! Go to Trading Desk & AI Insights to scan it.")
