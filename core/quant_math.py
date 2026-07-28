import numpy as np

def calculate_auto_spread_metrics(leg1_price, leg2_price, leg1_oi_change, rsi_val, expiry_days):
    # Automated Direction Detection based on Spread Value & Z-Score
    try:
        l1 = float(leg1_price)
        l2 = float(leg2_price)
    except:
        l1, l2 = 0.0, 0.0
        
    raw_diff = l1 - l2
    side = "LONG" if raw_diff >= 0 else "SHORT"
    spread_value = abs(raw_diff)
    
    # Z-Score estimation
    mean_val = (l1 + l2) / 2 if (l1 + l2) > 0 else 1.0
    z_score = round((spread_value - mean_val) / (mean_val * 0.05 + 1e-6), 2)
    
    # Conviction Rating
    conviction = "2/3"
    try:
        rsi_val = float(rsi_val)
        leg1_oi_change = float(leg1_oi_change)
    except:
        rsi_val = 50
        leg1_oi_change = 0

    if 45 <= rsi_val <= 55 and leg1_oi_change > 10:
        conviction = "1/3 (High Conviction)"
    elif z_score < -1.5 or z_score > 1.5:
        conviction = "3/3 (Red Flag / Mean Reversion Zone)"
        
    # Dynamic Holding Duration based on Expiry distance
    try:
        exp = int(expiry_days)
    except:
        exp = 52
        
    holding_days = exp if exp <= 90 else 87
    
    return {
        "side": side,
        "spread_value": spread_value,
        "z_score": z_score,
        "conviction": conviction,
        "holding_days": holding_days
    }

def compute_pl_and_risk(entry_price, current_spread, side, lot_size=50):
    try:
        e = float(entry_price)
        c = float(current_spread)
    except:
        e, c = 0.0, 0.0
        
    diff = (c - e) if side == "LONG" else (e - c)
    pnl = diff * lot_size
    target = e * 1.04 if side == "LONG" else e * 0.96
    stop_loss = e * 0.98 if side == "LONG" else e * 1.02
    return pnl, target, stop_loss
