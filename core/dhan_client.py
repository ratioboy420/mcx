
import requests
import json
import streamlit as st

class DhanClient:
    def __init__(self, client_id, access_token, secret_key):
        self.client_id = client_id
        self.access_token = access_token
        self.secret_key = secret_key
        self.base_url = "https://api.dhan.co/v2"
        
    def get_headers(self):
        return {
            "access-token": self.access_token,
            "client-id": self.client_id,
            "secret-key": self.secret_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    def test_connection(self):
        try:
            url = f"{self.base_url}/fundlimit"
            response = requests.get(url, headers=self.get_headers(), timeout=10)
            if response.status_code == 200:
                return True, "Connected Successfully (Active)"
            else:
                return False, f"Authentication Failed: {response.status_code} - {response.text}"
        except Exception as e:
            return False, f"Connection Error: {str(e)}"

    def fetch_quotes(self, security_ids):
        # Fetch live quotes for multiple security IDs from Dhan API
        try:
            url = f"{self.base_url}/marketfeed/quote"
            payload = {"securityIdList": security_ids, "exchangeSegment": "MCX"}
            response = requests.post(url, headers=self.get_headers(), json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get("data", {})
            return {}
        except Exception:
            return {}
