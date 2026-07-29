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
                return True, "Dhan Account Successfully Connected!"
            return False, f"Auth Error [{res.status_code}]: {res.text}"
        except Exception as e:
            return False, str(e)

    def get_live_market_data(self, security_id, exchange_segment="MCX_COMM"):
        url = f"{self.base_url}/marketfeed/ohlc"
        payload = {
            "exchangeSegment": exchange_segment,
            "securityId": str(security_id)
        }
        try:
            response = requests.post(url, json=payload, headers=self._headers(), timeout=4)
            if response.status_code == 200:
                res_json = response.json()
                data = res_json.get("data", {}).get(str(security_id), {})
                return data.get("last_price", "Live Active")
            return "Feed Error"
        except Exception:
            return "Timeout"
