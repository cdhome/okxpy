from typing import Optional, Dict
from ..auth import OKXAuth

class DefiCalculatorClient:
    """OKX DeFi Calculator API client"""
    
    BASE_URL = "https://www.okx.com/api/v5/defi/calculator"
    
    def __init__(self, auth: OKXAuth):
        self.auth = auth 