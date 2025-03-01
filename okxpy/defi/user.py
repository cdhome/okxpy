from typing import Optional, Dict
from ..auth import OKXAuth

class DefiUserClient:
    """OKX DeFi User API client"""
    
    BASE_URL = "https://www.okx.com/api/v5/defi/user"
    
    def __init__(self, auth: OKXAuth):
        self.auth = auth 