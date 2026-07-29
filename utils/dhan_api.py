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
        """Fetches real market quote/LTP directly using Dhan live market feed structure."""
        # MCX Commodity identifiers mapping for Dhan
        mcx_securities = [
            {"securityId": "13327", "symbol": "GOLD"},
            {"securityId": "13328", "symbol": "GOLDM"},
            {"securityId": "13330", "symbol": "GOLDGUINEA"},
            {"securityId": "13348", "symbol": "SILVER"},
            {"securityId": "13349", "symbol": "SILVERM"},
            {"securityId": "11412", "symbol": "COPPER"}
        ]
        
        url = f"{self.base_url}/marketfeed/ohlc"
        headers = self._get_headers()
        
        live_rates = []
        for item in mcx_securities:
            payload = {
                "exchangeSegment": "MCX",
                "securityId": str(item["securityId"])
            }
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    # Parsing response safely based on Dhan OHLC structure
                    market_data = data.get("data", {})
                    if item["securityId"] in market_data:
                        ltp = market_data[item["securityId"]].get("last_price", "No LTP")
                        live_rates.append({"Commodity": item["symbol"], "Live Rate": f"₹{ltp}"})
                    else:
                        live_rates.append({"Commodity": item["symbol"], "Live Rate": "Data Not Found"})
                else:
                    live_rates.append({"Commodity": item["symbol"], "Live Rate": f"Err {res.status_code}"})
            except Exception as e:
                live_rates.append({"Commodity": item["symbol"], "Live Rate": "Timeout"})
                
        return live_rates
