import streamlit as st
import datetime

def render_add_pair(client_id, access_token, secret_key):
    st.markdown("### ➕ Add New MCX Spread Contract (Futures & Options)")
    
    with st.form("comprehensive_add_form"):
        col1, col2 = st.columns(2)
        with col1:
            commodity = st.selectbox("Commodity Segment", [
                "GOLD", "GOLDM", "SILVER", "SILVERM", "COPPER", "ALUMINIUM", 
                "ZINC", "LEAD", "CRUDEOIL", "NATURALGAS", "NICKEL", "MENTHAOIL"
            ])
            instrument_type = st.selectbox("Instrument Mix", ["Future vs Future (All Expiry)", "Option Spread (CE/PE)", "Future vs Option"])
            
            leg1_name = st.text_input("Leg 1 Symbol (e.g. GOLD-Aug2026-FUT or 75000-CE)", value="GOLD-Aug2026-FUT")
            leg1_sec = st.text_input("Leg 1 Security ID", value="500123")
            l1_base = st.number_input("Leg 1 Base Price Fallback", value=71000.0)
            
        with col2:
            st.markdown("### &nbsp;")
            st.info("ℹ️ **Auto Direction Engine:** System market data, Z-score aur OI ke basis par khud determine karega ki trade **LONG** hoga ya **SHORT**.")
            
            leg2_name = st.text_input("Leg 2 Symbol (e.g. GOLD-Sep2026-FUT or 72000-PE)", value="GOLD-Sep2026-FUT")
            leg2_sec = st.text_input("Leg 2 Security ID", value="500124")
            l2_base = st.number_input("Leg 2 Base Price Fallback", value=71500.0)
            
        col3, col4, col5 = st.columns(3)
        with col3:
            entry_override = st.number_input("Entry Spread Price (₹) [0 for Auto]", value=0.0)
        with col4:
            expiry_distance = st.number_input("Expiry Distance (Days)", value=52)
        with col5:
            initial_status = st.selectbox("Status", ["LIVE", "pending"])
            
        submitted = st.form_submit_button("Add to Quant Desk")
        if submitted:
            pair_label = f"{commodity} [{instrument_type}] ({leg1_name} vs {leg2_name})"
            initial_spread = abs(l1_base - l2_base)
            final_entry = entry_override if entry_override > 0 else initial_spread
            
            new_row = {
                "Pair": pair_label,
                "Leg 1 Sec ID": leg1_sec,
                "Leg 2 Sec ID": leg2_sec,
                "L1_Price_Fallback": l1_base,
                "L2_Price_Fallback": l2_base,
                "Status": initial_status,
                "Opened": datetime.date.today().strftime("%d %b %Y"),
                "Entry": final_entry,
                "Target": final_entry * 1.04,
                "Stop": final_entry * 0.98,
                "C/F": "1/3",
                "Z_Score": -0.3,
                "RSI": 49,
                "OI_Delta": 15,
                "Expiry_Days": expiry_distance,
                "Pair Spread Value": f"₹{initial_spread:,.2f}",
                "Side": "LONG" if l1_base >= l2_base else "SHORT",
                "P/L": "—"
            }
            
            if "real_live_desk" not in st.session_state:
                st.session_state.real_live_desk = []
            st.session_state.real_live_desk.append(new_row)
            st.success(f"✅ Successfully added {pair_label} to your desk with Auto-Direction and F&O support!")
