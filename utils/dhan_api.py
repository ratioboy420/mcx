import requests

class DhanClient:
    def __init__(self, client_code, api_key, secret_key):
        self.client_code = client_code
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.dhan.co/v2"

    def _headers(self):
        return {
            "access-token": self.api_key,
            "client-id": self.client_code,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def test_connection(self):
        try:
            res = requests.get(f"{self.base_url}/fundlimit", headers=self._headers(), timeout=5)
            if res.status_code == 200:
                return True, "Dhan Account Connected Successfully!"
            return False, f"Auth Error [{res.status_code}]: {res.text}"
        except Exception as e:
            return False, str(e)

    def get_market_quote(self, security_id, segment="MCX"):
        # Dhan API v2 marketfeed OHLC endpoint format
        url = f"{self.base_url}/marketfeed/ohlc"
        payload = {
            "exchangeSegment": segment,
            "securityId": str(security_id)
        }
        try:
            res = requests.post(url, json=payload, headers=self._headers(), timeout=4)
            if res.status_code == 200:
                res_data = res.json()
                # Parsing market feed response safely
                data_dict = res_data.get("data", {})
                if str(security_id) in data_dict:
                    item_data = data_dict[str(security_id)]
                    last_price = item_data.get("last_price", 0.0)
                    return {"last_price": float(last_price) if last_price else 0.0}
        except Exception:
            pass
        return {"last_price": 0.0}
