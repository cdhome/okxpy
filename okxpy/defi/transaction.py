from typing import Optional, Dict
from ..auth import OKXAuth

class DefiTransactionClient:
    """OKX DeFi Transaction API client"""
    
    BASE_URL = "https://www.okx.com/api/v5/defi/transaction"
    
    def __init__(self, auth: OKXAuth):
        self.auth = auth 