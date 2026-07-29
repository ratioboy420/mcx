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
                return True, "Connected Successfully"
            return False, f"Error {res.status_code}: {res.text}"
        except Exception as e:
            return False, str(e)

    def get_all_mcx_spreads(self):
        mcx_tokens = [
            {"Symbol": "GOLD", "SecID": "13327", "Segment": "MCX_COMM"},
            {"Symbol": "GOLDM", "SecID": "13328", "Segment": "MCX_COMM"},
            {"Symbol": "SILVER", "SecID": "13348", "Segment": "MCX_COMM"},
            {"Symbol": "SILVERM", "SecID": "13349", "Segment": "MCX_COMM"},
            {"Symbol": "COPPER", "SecID": "11412", "Segment": "MCX_COMM"},
            {"Symbol": "ZINC", "SecID": "11235", "Segment": "MCX_COMM"},
            {"Symbol": "CRUDEOIL", "SecID": "10565", "Segment": "MCX_COMM"}
        ]
        
        url = f"{self.base_url}/marketfeed/ohlc"
        spread_results = []
        
        for item in mcx_tokens:
            payload = {
                "exchangeSegment": item["Segment"],
                "securityId": item["SecID"]
            }
            try:
                response = requests.post(url, json=payload, headers=self._headers(), timeout=3)
                if response.status_code == 200:
                    res_json = response.json()
                    data = res_json.get("data", {}).get(item["SecID"], {}) if isinstance(res_json, dict) else {}
                    ltp = data.get("last_price", "N/A") if isinstance(data, dict) else "N/A"
                    spread_results.append({
                        "Commodity": item["Symbol"],
                        "Security ID": item["SecID"],
                        "LTP": ltp if ltp else "Awaiting Tick"
                    })
                else:
                    spread_results.append({
                        "Commodity": item["Symbol"],
                        "Security ID": item["SecID"],
                        "LTP": f"Error {response.status_code}"
                    })
            except Exception:
                spread_results.append({
                    "Commodity": item["Symbol"],
                    "Security ID": item["SecID"],
                    "LTP": "Timeout"
                })
        return spread_results
