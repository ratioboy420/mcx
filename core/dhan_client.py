import requests

class DhanClient:
    def __init__(self, client_id, access_token, secret_key):
        self.client_id = client_id.strip()
        self.access_token = access_token.strip()
        self.secret_key = secret_key.strip()
        self.base_url = "https://api.dhan.co/v2"

    def verify_credentials(self):
        """Validates the 3 required credentials against Dhan API"""
        if not self.client_id or not self.access_token or not self.secret_key:
            return False, "All 3 credentials (Client Code, Access Token, Secret Key) are required."
            
        headers = {
            "access-token": self.access_token,
            "client-id": self.client_id,
            "Content-Type": "application/json"
        }
        
        try:
            # Test endpoint for holdings or profile to verify authentication
            response = requests.get(f"{self.base_url}/fundlimit", headers=headers, timeout=5)
            if response.status_code == 200:
                return True, "API Connection Successful with Dhan HQ!"
            else:
                return False, f"Authentication Failed (HTTP {response.status_code}): Check your credentials."
        except Exception as e:
            return False, f"Connection Error: {str(e)}"

    def fetch_quotes(self, security_ids):
        """Fetches live market LTP data for given MCX Security IDs from Dhan API"""
        if not security_ids or not self.access_token:
            return {}
            
        headers = {
            "access-token": self.access_token,
            "client-id": self.client_id,
            "Content-Type": "application/json"
        }
        
        # Dhan Market Feed / Quotes Payload structure for MCX
        payload = {
            "MCX": [str(sid) for sid in security_ids if sid]
        }
        
        try:
            response = requests.post(f"{self.base_url}/marketfeed/ltp", json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Parse LTP response from Dhan API structure
                formatted_quotes = {}
                market_data = data.get("data", {})
                for sec_id, details in market_data.items():
                    if "ltp" in details:
                        formatted_quotes[str(sec_id)] = {"LTP": float(details["ltp"])}
                return formatted_quotes
            else:
                return {}
        except Exception:
            return {}
