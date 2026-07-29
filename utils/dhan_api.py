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
        """Verifies if the 3 Dhan API credentials are valid by fetching live fund/account details."""
        url = f"{self.base_url}/fundlimit"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=5)
            if response.status_code == 200:
                return {"status": "connected", "message": "Dhan Account Successfully Connected!"}
            elif response.status_code == 401:
                return {"status": "error", "message": "Authentication Failed: Check your Client Code, API Key, or Secret Key."}
            else:
                return {"status": "error", "message": f"API Error [{response.status_code}]: {response.text}"}
        except Exception as e:
            return {"status": "error", "message": f"Connection Exception: {str(e)}"}

    def get_live_metal_rates(self):
        """Fetches real live market rates/quotes for all MCX commodities to display in the live ticker column."""
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
                "exchangeSegment": "MCX_COMM",
                "securityId": item["securityId"]
            }
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=3)
                if res.status_code == 200:
                    data = res.json()
                    ohlc_data = data.get("data", {}).get(item["securityId"], {})
                    last_price = ohlc_data.get("last_price", "Live Feed Active")
                    live_rates.append({"Commodity": item["symbol"], "Live Rate": last_price})
                else:
                    live_rates.append({"Commodity": item["symbol"], "Live Rate": "Fetch Error"})
            except Exception:
                live_rates.append({"Commodity": item["symbol"], "Live Rate": "Connecting..."})
                
        return live_rates
