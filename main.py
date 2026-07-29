@st.cache_data(ttl=3600)
def load_mcx_scrip_master():
    url = "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
    df = pd.read_csv(url, low_memory=False)
    
    # Column Name Flexibility Check (Handling API Schema Changes)
    exch_col = 'SEM_EXM_EXCH_ID' if 'SEM_EXM_EXCH_ID' in df.columns else ('EXCH_ID' if 'EXCH_ID' in df.columns else None)
    inst_col = 'SEM_INSTRUMENT_NAME' if 'SEM_INSTRUMENT_NAME' in df.columns else ('INSTRUMENT' if 'INSTRUMENT' in df.columns else None)
    
    if exch_col and inst_col:
        mcx_fut = df[(df[exch_col] == 'MCX') & (df[inst_col] == 'FUTCOM')].copy()
    elif exch_col:
        mcx_fut = df[df[exch_col] == 'MCX'].copy()
    else:
        # Fallback filter search across dataframe
        mcx_fut = df.copy()
        
    return mcx_fut
