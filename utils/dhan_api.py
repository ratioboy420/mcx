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
        
        if segment == "MCX":
            segment = "MCX_COMM"

        try:
            sec_id_int = int(security_id)
            # Dhan Payload requires integer list inside market feed
            payload = {
                segment: [sec_id_int]
            }

            res = requests.post(url, json=payload, headers=self._headers(), timeout=5)
            
            if res.status_code == 200:
                res_data = res.json()
                data_dict = res_data.get("data", {})
                
                # Check segment map
                segment_data = data_dict.get(segment, {})
                sec_key = str(sec_id_int)
                
                if sec_key in segment_data:
                    last_p = segment_data[sec_key].get("last_price", 0.0)
                    return {"last_price": float(last_p) if last_p else 0.0}
                elif sec_key in data_dict:
                    last_p = data_dict[sec_key].get("last_price", 0.0)
                    return {"last_price": float(last_p) if last_p else 0.0}

        except Exception as e:
            print(f"Error fetching quote for {security_id}: {e}")

        return {"last_price": 0.0}
