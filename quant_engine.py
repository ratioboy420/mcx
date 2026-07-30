import pandas as pd

def analyze_calendar_spread(z_score, dte, rsi, oi_delta):
    """
    Based on Winning Profile Image rules
    """
    reasons = []
    is_tradable = True
    
    # Rule 1: DTE (Days to Expiry) should be 49-56 days
    if dte < 45:
        reasons.append("Reject: DTE is too low (Near Expiry).")
        is_tradable = False
        
    # Rule 2: RSI should not be oversold
    if rsi < 40:
        reasons.append("Reject: RSI too low (Falling knife).")
        is_tradable = False
        
    # Rule 3: Z-Score (Avoid extremes)
    if z_score <= -1.7:
        reasons.append("Reject: Extreme Negative Z-Score.")
        is_tradable = False
        
    # Rule 4: OI Delta must be positive (Fresh positions)
    if oi_delta < 0:
        reasons.append("Reject: Negative OI Delta.")
        is_tradable = False
        
    if is_tradable:
        return True, "Trade looks good based on Quant Rules."
    else:
        return False, " | ".join(reasons)
