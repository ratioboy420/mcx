
import numpy as np

def calculate_spread_metrics(leg1_price, leg2_price, leg1_oi_change, leg2_oi_change, rsi_val, expiry_days, side="LONG"):
    # Real-time mathematical computations based on Winning Profile
    spread_value = abs(leg1_price - leg2_price) if side == "LONG" else abs(leg2_price - leg1_price)
    
    # Z-Score estimation based on price variance
    mean_val = (leg1_price + leg2_price) / 2
    z_score = round((spread_value - mean_val) / (mean_val * 0.05 + 1e-6), 2)
    
    # Conviction Rating (1/3, 2/3, 3/3)
    conviction = "2/3"
    if rsi_val > 45 and rsi_val < 55 and leg1_oi_change > 10:
        conviction = "1/3"
    elif z_score < -1.5 or z_score > 1.5:
        conviction = "3/3 (Red Flag)"
        
    # Recommended Holding Duration (Days) based on Winning Profile rules
    holding_days = 52 if (expiry_days >= 45 and expiry_days <= 60) else 35
    
    return {
        "spread_value": spread_value,
        "z_score": z_score,
        "conviction": conviction,
        "holding_days": holding_days
    }

def compute_pl_and_risk(entry_price, current_spread, side, lot_size=50):
    diff = (current_spread - entry_price) if side == "LONG" else (entry_price - current_spread)
    pnl = diff * lot_size
    target = entry_price * 1.04 if side == "LONG" else entry_price * 0.96
    stop_loss = entry_price * 0.98 if side == "LONG" else entry_price * 1.02
    return pnl, target, stop_loss
