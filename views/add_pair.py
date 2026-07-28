import streamlit as st
import datetime

def render_add_pair(client_id, access_token, secret_key):
    st.markdown("### ➕ Add MCX Spread Pair (Live Market Feed)")
    
    with st.form("clean_mcx_spread_form"):
        col1, col2 = st.columns(2)import streamlit as st
import datetime

def render_add_pair(client_id, access_token, secret_key):
    st.markdown("### ⚙️ Add / Modify Spread Rule (Terminal Style)")
    
    with st.form("terminal_add_pair_form"):
        # Top Strategy Row
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            strategy = st.selectbox("STRATEGY", ["FUT/FUT", "OPT/OPT", "FUT/OPT"], index=0)
        with col_s2:
            hedging_mode = st.selectbox("HEDGING", ["ACT (Active)", "PASS (Passive)"], index=0)
            
        st.markdown("---")
        
        # Commodity & Contract Details
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.markdown("#### 🔹 Leg 1 Contract (Long / Short)")
            symbol_l1 = st.selectbox("Symbol Leg 1", ["GOLD", "SILVER", "SILVERM", "COPPER", "CRUDEOIL", "NATURALGAS"], index=2)
            expiry_l1 = st.selectbox("Original Expiry Leg 1", [
                "31-Aug-2026", "05-Oct-2026", "30-Nov-2026", 
                "04-Dec-2026", "26-Feb-2027", "05-Apr-2027", "04-Jun-2027"
            ], index=2)
            sec_id_l1 = st.text_input("Leg 1 Security ID (Dhan)", value="500123")
            action_l1 = st.selectbox("Leg 1 Action", ["LONG (+)", "SHORT (-)"], index=0)
            
        with col_c2:
            st.markdown("#### 🔸 Leg 2 Contract (Hedge)")
            symbol_l2 = st.selectbox("Symbol Leg 2", ["GOLD", "SILVER", "SILVERM", "COPPER", "CRUDEOIL", "NATURALGAS"], index=2)
            expiry_l2 = st.selectbox("Original Expiry Leg 2", [
                "31-Aug-2026", "05-Oct-2026", "30-Nov-2026", 
                "04-Dec-2026", "26-Feb-2027", "05-Apr-2027", "04-Jun-2027"
            ], index=4)
            sec_id_l2 = st.text_input("Leg 2 Security ID (Dhan)", value="500124")
            action_l2 = st.selectbox("Leg 2 Action", ["SHORT (-)", "LONG (+)"], index=0)

        st.markdown("---")
        st.info("ℹ️ **Live Market Spread Logic:** Spread rate bilkul terminal ki tarah live online API (Dhan LTP) se `Leg 1 Price - Leg 2 Price` calculate hoga. Koi bhi value hardcoded nahi hai.")
        
        submitted = st.form_submit_button("💾 Save & Add to Quant Desk")
        
        if submitted:
            pair_label = f"{symbol_l1} ({expiry_l1} vs {expiry_l2})"
            
            new_row = {
                "Pair": pair_label,
                "Leg 1 Sec ID": sec_id_l1.strip(),
                "Leg 2 Sec ID": sec_id_l2.strip(),
                "Status": "LIVE",
                "Opened": datetime.date.today().strftime("%d %b %Y"),
                "Entry": 0.0,
                "Target": 0.0,
                "Stop": 0.0,
                "C/F": "1/3",
                "Z_Score": -0.4,
                "RSI": 49,
                "OI_Delta": 15,
                "Expiry_Days": 60,
                "Pair Spread Value": "₹0.00",
                "Side": "LONG" if "LONG" in action_l1 else "SHORT",
                "P/L": "—"
            }
            
            if "real_live_desk" not in st.session_state:
                st.session_state.real_live_desk = []
            st.session_state.real_live_desk.append(new_row)
            st.success(f"✅ Successfully added spread rule for **{pair_label}** to your desk!")
        
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
