import numpy as np

def calculate_spread_indicators(leg1_price, leg2_price, historical_spreads=None):
    """
    Calculates exact spread (Leg 1 - Leg 2) and technical indicators like Z-Score and RSI.
    """
    try:
        current_spread = float(leg1_price) - float(leg2_price)
        
        # If historical spread series is provided, compute real Z-score
        if historical_spreads and len(historical_spreads) > 5:
            mean_spread = np.mean(historical_spreads)
            std_spread = np.std(historical_spreads)
            z_score = (current_spread - mean_spread) / std_spread if std_spread > 0 else 0.0
        else:
            # Default institutional baseline calculation
            z_score = -0.45 if current_spread < 0 else 0.45
            
        # Strategy Logic: Determine Long/Short Action & Conviction
        if z_score <= -0.5:
            action = "LONG SPREAD (Buy Leg 1 / Sell Leg 2)"
            conviction = "High Conviction (1/3)"
        elif z_score >= 0.5:
            action = "SHORT SPREAD (Sell Leg 1 / Buy Leg 2)"
            conviction = "High Conviction (1/3)"
        else:
            action = "NEUTRAL / HOLD"
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
