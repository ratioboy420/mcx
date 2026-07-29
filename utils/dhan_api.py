import requests

class DhanClient:
    def __init__(self, client_code, api_key, secret_key):
        self.client_code = client_code
        self.api_key = api_key
        # Dhan me 'access-token' hi aapka Secret Key / Auth token hota hai
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
                    err_data = res.json()
                    err_msg = err_data.get('errorMessage', res.text)
                except Exception:
                    err_msg = res.text
                return False, f"Auth Error [{res.status_code}]: {err_msg}"
        except Exception as e:
            return False, str(e)

    def get_market_quote(self, security_id, segment="MCX_COMM"):
        """
        Fetch Last Traded Price (LTP) from Dhan v2 Market Feed API
        """
        if not security_id or str(security_id) in ["0", "None", ""]:
            return {"last_price": 0.0}
            
        # 1. Correct Endpoint for LTP in Dhan API v2
        url = f"{self.base_url}/marketfeed/ltp"
        
        # 2. Correct Segment Mapping (MCX -> MCX_COMM)
        if segment == "MCX":
            segment = "MCX_COMM"

        # 3. Correct Payload Format for Dhan Market Feed
        payload = {
            segment: [str(security_id)]
        }

        try:
            res = requests.post(url, json=payload, headers=self._headers(), timeout=5)
            if res.status_code == 200:
                res_data = res.json()
                data_dict = res_data.get("data", {})
                
                # Check inside Segment and Security ID response
                segment_data = data_dict.get(segment, {})
                if str(security_id) in segment_data:
                    item_data = segment_data[str(security_id)]
                    last_price = item_data.get("last_price", 0.0)
                    return {"last_price": float(last_price) if last_price else 0.0}
                    
                # Direct key fall-back search
                elif str(security_id) in data_dict:
                    item_data = data_dict[str(security_id)]
                    last_price = item_data.get("last_price", 0.0)
                    return {"last_price": float(last_price) if last_price else 0.0}

        except Exception as e:
            print(f"Error fetching quote for {security_id}: {e}")

        return {"last_price": 0.0}
