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
                return {"status": "connected", "message": "Dhan Account Connected Successfully"}
            else:
                return {"status": "error", "message": f"Auth Failed [{response.status_code}]: {response.text}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_live_market_data(self, security_id, exchange_segment="MCX_COMM"):
        url = f"{self.base_url}/marketfeed/ohlc"
        payload = {
            "exchangeSegment": exchange_segment,
            "securityId": str(security_id)
        }
        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=5)
            if response.status_code == 200:
                res_json = response.json()
                data = res_json.get("data", {})
                if str(security_id) in data:
                    return data[str(security_id)]
            return None
        except Exception:
            return None
