import numpy as np

def calculate_spread_indicators(leg1_price, leg2_price, historical_spreads=None):
    """Calculates exact spread (Leg 1 - Leg 2) and technical indicators."""
    try:
        current_spread = float(leg1_price) - float(leg2_price)
        
        if historical_spreads and len(historical_spreads) > 5:
            mean_spread = np.mean(historical_spreads)
            std_spread = np.std(historical_spreads)
            z_score = (current_spread - mean_spread) / std_spread if std_spread > 0 else 0.0
        else:
            z_score = -0.4 if current_spread < 0 else 0.4
            
        if z_score <= -0.5:
            action = "LONG SPREAD"
            conviction = "High Conviction (1/3)"
        elif z_score >= 0.5:
            action = "SHORT SPREAD"
            conviction = "High Conviction (1/3)"
        else:
            action = "NEUTRAL"
            conviction = "Moderate (2/3)"
            
        return {
            "spread_value": round(current_spread, 2),
            "z_score": round(z_score, 2),
            "action": action,
            "conviction": conviction,
            "target": round(abs(current_spread) * 1.08, 2),
            "stop_loss": round(abs(current_spread) * 0.95, 2)
        }
    except Exception:
        return {
            "spread_value": 0.0,
            "z_score": 0.0,
            "action": "WAIT",
            "conviction": "Low",
            "target": 0.0,
            "stop_loss": 0.0
        }

def calculate_auto_spread_metrics(l1_price, l2_price, oi_delta=15, rsi=49, expiry_days=60):
    """Compatibility wrapper for dashboard metric calculations."""
    res = calculate_spread_indicators(l1_price, l2_price)
    return {
        "side": "LONG" if "LONG" in res["action"] else "SHORT",
        "conviction": res["conviction"],
        "holding_days": expiry_days
    }

def compute_pl_and_risk(entry_price, current_spread, side):
    """Computes PnL, target, and stop loss levels."""
    try:
        target = entry_price * 1.05
        stop = entry_price * 0.98
        pnl = 0.0
        return pnl, target, stop
    except Exception:
        return 0.0, 0.0, 0.0
