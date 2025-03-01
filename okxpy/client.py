import json
from typing import Optional
from .auth import OKXAuth
from .wallet.client import WalletClient
from .dex.client import DexClient
from .marketplace.client import MarketplaceClient
from .defi.client import DefiClient

class OKXClient:
    """Main client class for OKX API"""
    
    def __init__(self, credentials_path: Optional[str] = None, 
                 api_key: Optional[str] = None,
                 secret_key: Optional[str] = None,
                 passphrase: Optional[str] = None,
                 project_id: Optional[str] = None):
        """
        Initialize with either credentials file or direct parameters
        """
        if credentials_path:
            with open(credentials_path) as f:
                credentials = json.load(f)
                self.api_key = credentials["access_key"]
                self.secret_key = credentials["secret_key"]
                self.passphrase = credentials["passphrase"]
                self.project_id = credentials["access_project"]
        else:
            self.api_key = api_key
            self.secret_key = secret_key
            self.passphrase = passphrase
            self.project_id = project_id

        if not all([self.api_key, self.secret_key, self.passphrase, self.project_id]):
            raise ValueError("Missing required credentials")

        # Initialize auth
        self.auth = OKXAuth(
            api_key=self.api_key,
            secret_key=self.secret_key,
            passphrase=self.passphrase,
            project_id=self.project_id
        )

        # Initialize service clients
        self.wallet = WalletClient(self.auth)
        self.dex = DexClient(self.auth)
        self.marketplace = MarketplaceClient(self.auth)
        self.defi = DefiClient(self.auth) 