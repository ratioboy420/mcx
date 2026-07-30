import pandas as pd
import time
from py_vollib.black_scholes_merton.greeks.analytical import delta, gamma, theta, vega

class DhanLiveEngine:
    def __init__(self, dhan_client):
        self.dhan = dhan_client
        
    def get_live_price(self, security_id, exchange="MCX"):
        """
        Fetches live LTP from Dhan API.
        (Replace this block with actual DhanHQ fetch logic based on their updated SDK)
        """
        try:
            # Simulated Dhan API Call
            # response = self.dhan.get_market_quote(exchange_segment=exchange, instrument_token=security_id)
            # return response['data']['LTP']
            return 72500.0  # Placeholder live price for testing
        except Exception as e:
            print(f"Error fetching live price: {e}")
            return None

    def calculate_greeks(self, flag, S, K, t, r, sigma, q=0.0):
        """
        Calculates Option Greeks using Black-Scholes-Merton model.
        flag: 'c' for call, 'p' for put
        S: Spot/Futures Price
        K: Strike Price
        t: Time to maturity (in years, e.g., DTE / 365)
        r: Risk-free rate (e.g., 0.05 for 5%)
        sigma: Implied Volatility (e.g., 0.20 for 20%)
        q: Dividend/Convenience yield (usually 0 for MCX futures)
        """
        try:
            # Ensure values are floats and handle near-zero DTE
            t = max(t, 0.001) 
            
            d = delta(flag, S, K, t, r, sigma, q)
            g = gamma(flag, S, K, t, r, sigma, q)
            th = theta(flag, S, K, t, r, sigma, q)
            v = vega(flag, S, K, t, r, sigma, q)
            
            return {"Delta": round(d, 4), "Gamma": round(g, 6), "Theta": round(th, 2), "Vega": round(v, 4)}
        except Exception as e:
            print(f"Greeks Calc Error: {e}")
            return {"Delta": 0, "Gamma": 0, "Theta": 0, "Vega": 0}
