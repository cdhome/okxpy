import base64
import hmac
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Tuple

class OKXAuth:
    def __init__(self, api_key: str, secret_key: str, passphrase: str, project_id: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.project_id = project_id

    def get_timestamp(self) -> str:
        """Generate ISO format timestamp required by OKX API"""
        return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

    def sign(self, method: str, path: str, params: Optional[Dict] = None, body: Optional[Dict] = None) -> Tuple[str, str]:
        """
        Generate signature for OKX API request
        Returns: (signature, timestamp)
        """
        timestamp = self.get_timestamp()
        
        # Build message to sign
        if method == "GET" and params:
            sorted_params = sorted(params.items())
            query_string = "&".join([f"{key}={value}" for key, value in sorted_params])
            message = f"{timestamp}{method}{path}?{query_string}"
        elif method == "POST" and body:
            body_str = str(body)  # Convert dict to string
            message = f"{timestamp}{method}{path}{body_str}"
        else:
            message = f"{timestamp}{method}{path}"

        # Generate signature
        signature = base64.b64encode(
            hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')

        return signature, timestamp

    def get_headers(self, method: str, path: str, params: Optional[Dict] = None, body: Optional[Dict] = None) -> Dict:
        """Generate headers for OKX API request"""
        signature, timestamp = self.sign(method, path, params, body)
        
        return {
            "Content-Type": "application/json",
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "OK-ACCESS-PROJECT": self.project_id
        } 