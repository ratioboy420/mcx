import pandas as pd

# Dhan Scrip Master se Real-Time MCX Security IDs auto-fetch karne ka function
@st.cache_data(ttl=3600)  # Har 1 ghante me master file re-fetch hogi
def get_live_dhan_mcx_instruments():
    try:
        url = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
        df = pd.read_csv(url)
        
        # MCX Futures filter karein
        mcx_fut = df[(df['SEM_EXM_EXCH_ID'] == 'MCX') & (df['SEM_INSTRUMENT_NAME'] == 'FUTCOM')]
        
        instruments_dict = {}
        for _, row in mcx_fut.iterrows():
            # Trading symbol or custom symbol format
            symbol_name = str(row.get('SEM_CUSTOM_SYMBOL', row.get('SM_SYMBOL_NAME', '')))
            sec_id = int(row['SEM_SMST_SECURITY_ID'])
            
            if symbol_name:
                instruments_dict[symbol_name] = {"id": sec_id, "seg": "MCX_COMM"}
                
        return instruments_dict
    except Exception as e:
        st.error(f"Error loading Dhan Scrip Master: {e}")
        return {}

# Live Dynamic Instruments Load karein
metal_map = get_live_dhan_mcx_instruments()
