import requests

class DhanClient:
    def __init__(self, client_id, access_token, secret_key=""):
        self.client_id = client_id
        self.access_token = access_token
        self.secret_key = secret_key
        self.base_url = "https://api.dhan.co/v2"

    def test_connection(self):
        """Validates all 3 credentials with Dhan API."""
        if not self.client_id or not self.access_token:
            return False, "Client ID and Access Token are required."
            
        headers = {
            "access-token": self.access_token,
            "client-id": self.client_id,
            "Content-Type": "application/json"
        }
        try:
            res = requests.get(f"{self.base_url}/fundlimit", headers=headers, timeout=5)
            if res.status_code == 200:
                return True, "Successfully connected to Dhan Live API!"
            else:
                return False, f"Authentication Failed (Code {res.status_code}): Check your credentials."
        except Exception as e:
            return False, f"Connection Error: {str(e)}"

    def fetch_market_quotes(self, security_ids):
        """Fetches real-time LTP for given MCX security IDs."""
        if not self.client_id or not self.access_token or not security_ids:
            return {}
            
        headers = {
            "access-token": self.access_token,
            "client-id": self.client_id,
            "Content-Type": "application/json"
        }
        
        body = {
            "MCX": [str(sid) for sid in security_ids if sid]
        }
        
        try:
            res = requests.post(f"{self.base_url}/marketfeed/ltp", json=body, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                prices = {}
                market_data = data.get("data", {}).get("MCX", {})
                for sec_id, info in market_data.items():
                    prices[str(sec_id)] = float(info.get("last_price", 0.0))
                return prices
            return {}
        except Exception:
            return {}

    def fetch_quotes(self, security_ids):
        """Alias method to prevent AttributeError when dashboard calls fetch_quotes."""
        return self.fetch_market_quotes(security_ids)
