import streamlit as st
import datetime

def render_add_pair(client_id, access_token, secret_key):
    st.markdown("### ➕ Add MCX Spread Pair (Live Market Feed)")
    
    with st.form("clean_mcx_spread_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Leg 1 Contract")
            commodity = st.selectbox("Commodity", ["GOLD", "SILVER", "COPPER", "CRUDEOIL", "NATURALGAS", "ALUMINIUM", "ZINC", "LEAD"])
            leg1_symbol = st.text_input("Leg 1 Symbol", value="COPPER-31Aug2026-FUT")
            leg1_sec_id = st.text_input("Leg 1 Security ID (Dhan)", value="500123")
            
        with col2:
            st.markdown("#### Leg 2 Contract")
            st.markdown("&nbsp;") # Spacing alignment
            leg2_symbol = st.text_input("Leg 2 Symbol", value="COPPER-30Sep2026-FUT")
            leg2_sec_id = st.text_input("Leg 2 Security ID (Dhan)", value="500124")
            
        st.info("ℹ️ **Spread Logic:** Spread rate automatically live online API (Dhan LTP) se calculate hoga (`Leg 1 LTP - Leg 2 LTP`), koi manual ya fixed value use nahi hogi.")
        
        submitted = st.form_submit_button("Add Pair to Live Quant Desk")
        
        if submitted:
            pair_name = f"{commodity} ({leg1_symbol} vs {leg2_symbol})"
            
            new_row = {
                "Pair": pair_name,
                "Leg 1 Sec ID": leg1_sec_id.strip(),
                "Leg 2 Sec ID": leg2_sec_id.strip(),
                "Status": "LIVE",
                "Opened": datetime.date.today().strftime("%d %b %Y"),
                "Entry": 0.0, # Will be set on first live fetch
                "Target": 0.0,
                "Stop": 0.0,
                "C/F": "1/3",
                "Z_Score": 0.0,
                "RSI": 50,
                "OI_Delta": 10,
                "Expiry_Days": 30,
                "Pair Spread Value": "₹0.00",
                "Side": "LONG",
                "P/L": "—"
            }
            
            if "real_live_desk" not in st.session_state:
                st.session_state.real_live_desk = []
            st.session_state.real_live_desk.append(new_row)
            st.success(f"✅ Successfully added {pair_name}. Go to Dashboard and click 'Refresh Live Market Data' to fetch real online rates!")
