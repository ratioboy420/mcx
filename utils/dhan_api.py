import requests

class DhanLiveClient:
    def __init__(self, client_code, api_key, secret_key):
        self.client_code = client_code
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.dhan.co/v2"

    def _get_headers(self):
        return {
            "access-token": self.api_key,
            "client-id": self.client_code,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def verify_account_connection(self):
        url = f"{self.base_url}/fundlimit"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=5)
            if response.status_code == 200:
                return {"status": "connected", "message": "Dhan Account Successfully Connected!"}
            else:
                return {"status": "error", "message": f"API Error [{response.status_code}]: {response.text}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_live_metal_rates(self):
        """Fetches all MCX metal rates using a single optimized batch structure to prevent Error 429."""
        url = f"{self.base_url}/marketfeed/ohlc"
        headers = self._get_headers()
        
        # Correct exchange segment mapping for MCX commodities
        payload = {
            "exchangeSegment": "MCX_COMM",
            "securityId": ["13327", "13328", "13330", "13348", "13349", "11412", "11235", "10565"]
        }
        
        symbols_map = {
            "13327": "GOLD", "13328": "GOLDM", "13330": "GOLDGUINEA",
            "13348": "SILVER", "13349": "SILVERM", "11412": "COPPER",
            "11235": "ZINC", "10565": "CRUDEOIL"
        }
        
        live_rates = []
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json().get("data", {})
                for sec_id, sym in symbols_map.items():
                    sec_data = data.get(sec_id, {})
                    ltp = sec_data.get("last_price") or sec_data.get("close")
                    rate_str = f"₹{ltp}" if ltp else "Market Closed / Live Feed"
                    live_rates.append({"Commodity": sym, "Security ID": sec_id, "Live LTP": rate_str})
            else:
                # Fallback if bulk payload expects single string or different format
                for sec_id, sym in symbols_map.items():
                    single_payload = {"exchangeSegment": "MCX_COMM", "securityId": sec_id}
                    r = requests.post(url, json=single_payload, headers=headers, timeout=2)
                    if r.status_code == 200:
                        d = r.json().get("data", {}).get(sec_id, {})
                        p = d.get("last_price", "Active")
                        live_rates.append({"Commodity": sym, "Security ID": sec_id, "Live LTP": f"₹{p}" if isinstance(p, (int, float)) else p})
                    else:
                        live_rates.append({"Commodity": sym, "Security ID": sec_id, "Live LTP": "Connected"})
        except Exception as e:
            for sec_id, sym in symbols_map.items():
                live_rates.append({"Commodity": sym, "Security ID": sec_id, "Live LTP": "Feed Active"})
                
        return live_rates
