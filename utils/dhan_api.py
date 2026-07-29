import requests

class DhanClient:
    def __init__(self, client_code, api_key, secret_key):
        self.client_code = client_code
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = "https://api.dhan.co/v2"

    def _headers(self):
        return {
            "access-token": self.secret_key,
            "client-id": self.client_code,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def test_connection(self):
        try:
            res = requests.get(f"{self.base_url}/fundlimit", headers=self._headers(), timeout=5)
            if res.status_code == 200:
                return True, "Dhan Account Connected Successfully!"
            else:
                try:
                    err_msg = res.json().get('errorMessage', res.text)
                except Exception:
                    err_msg = res.text
                return False, f"Auth Error [{res.status_code}]: {err_msg}"
        except Exception as e:
            return False, str(e)

    def get_market_quote(self, security_id, segment="MCX_COMM"):
        if not security_id or str(security_id) in ["0", "None", ""]:
            return {"last_price": 0.0}
            
        url = f"{self.base_url}/marketfeed/ltp"
        
        # Standardize segment name for Dhan API
        if segment in ["MCX", "MCX_COMM"]:
            segment_key = "MCX_COMM"
        else:
            segment_key = segment

        try:
            sec_id_int = int(security_id)
            payload = {
                segment_key: [sec_id_int]
            }

            res = requests.post(url, json=payload, headers=self._headers(), timeout=5)
            
            if res.status_code == 200:
                res_data = res.json()
                data_dict = res_data.get("data", {})
                
                # Check directly inside segment key
                if segment_key in data_dict:
                    seg_data = data_dict[segment_key]
                    sec_str = str(sec_id_int)
                    if sec_str in seg_data:
                        price = seg_data[sec_str].get("last_price", 0.0)
                        return {"last_price": float(price) if price else 0.0}
                        
                # Fallback check across root data dictionary
                for seg, content in data_dict.items():
                    if isinstance(content, dict) and str(sec_id_int) in content:
                        price = content[str(sec_id_int)].get("last_price", 0.0)
                        return {"last_price": float(price) if price else 0.0}

        except Exception as e:
            print(f"Error fetching LTP for ID {security_id}: {e}")

        return {"last_price": 0.0}
