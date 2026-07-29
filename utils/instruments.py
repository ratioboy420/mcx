# Dhan MCX Instrument Mapping
MCX_INSTRUMENTS = {
    "GOLD (Current Expiry)": {"id": 252321, "seg": "MCX_COMM"},
    "GOLD (Next Expiry)": {"id": 252322, "seg": "MCX_COMM"},
    "GOLDM (Current Expiry)": {"id": 252323, "seg": "MCX_COMM"},
    "SILVER (Current Expiry)": {"id": 252350, "seg": "MCX_COMM"},
    "SILVER (Next Expiry)": {"id": 252351, "seg": "MCX_COMM"},
    "SILVERM (Current Expiry)": {"id": 252352, "seg": "MCX_COMM"},
    "COPPER": {"id": 252380, "seg": "MCX_COMM"},
    "ZINC": {"id": 252390, "seg": "MCX_COMM"},
    "CRUDEOIL (Current Expiry)": {"id": 252410, "seg": "MCX_COMM"},
    "NATURALGAS": {"id": 252420, "seg": "MCX_COMM"},
    "ALUMINIUM": {"id": 252430, "seg": "MCX_COMM"}
}

def get_instrument_mapping():
    return MCX_INSTRUMENTS

def get_instrument_names():
    return list(MCX_INSTRUMENTS.keys())
