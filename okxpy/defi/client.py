from typing import Optional, Dict
from .explore import ExploreClient
from .calculator import CalculatorClient
from .transaction import TransactionClient
from .user import UserClient
from ..auth import OKXAuth

class DefiClient:
    """OKX DeFi API client"""
    
    def __init__(self, auth: OKXAuth):
        self.auth = auth
        self.explore = ExploreClient(auth)
        self.calculator = CalculatorClient(auth)
        self.transaction = TransactionClient(auth)
        self.user = UserClient(auth) 