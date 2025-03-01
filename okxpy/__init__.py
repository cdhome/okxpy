"""
OKX Web3 API Python SDK
~~~~~~~~~~~~~~~~~~~~~

A Python SDK for OKX Web3 API.

Basic usage:
    >>> from okxpy import OKXClient
    >>> client = OKXClient(api_key="your-api-key", secret_key="your-secret-key", 
    ...                    passphrase="your-passphrase", project_id="your-project-id")
    >>> chains = client.dex.get_supported_chains()
"""

from .client import OKXClient
from .auth import OKXAuth

__version__ = "0.1.0"
__author__ = "SunXin"
__email__ = "cd_home@163.com"

__all__ = ["OKXClient", "OKXAuth"] 