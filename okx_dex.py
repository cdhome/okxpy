"""
OKX DEX API wrapper
Implements all endpoints from:
- Quote API: https://www.okx.com/zh-hans/web3/build/docs/waas/dex-get-quote
- Chain API: https://www.okx.com/zh-hans/web3/build/docs/waas/dex-get-aggregator-supported-chains
- Token API: https://www.okx.com/zh-hans/web3/build/docs/waas/dex-get-tokens
- Liquidity API: https://www.okx.com/zh-hans/web3/build/docs/waas/dex-get-liquidity
- Approve API: https://www.okx.com/zh-hans/web3/build/docs/waas/dex-approve-transaction
- Swap API: https://www.okx.com/zh-hans/web3/build/docs/waas/dex-swap
"""

import os
import time
import hmac
import json
import base64
import hashlib
import requests
from datetime import datetime, timezone
from typing import Dict, Optional, Union, List

CHAINS = {
    #https://solscan.io/leaderboard/token
    'Solana': {
        'chain_id': '501',
        'Addr':{
            'USDT_MINT_ADDR': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',
            'USDC_MINT_ADDR': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'BTC_MINT_ADDR': '9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtAeTH5YFeJ9E',
            'ETH_MINT_ADDR': '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs',
            'SOL_MINT_ADDR': 'So11111111111111111111111111111111111111112',  # 原生SOL
            'BONK_MINT_ADDR': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
            'RAY_MINT_ADDR': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',
            'MATIC_MINT_ADDR': 'Gz7VkD4MacbEB6yC5XD3HcumEiYx2EtDYYrfikGsvopG',
            'AVAX_MINT_ADDR': 'KgV1GvrHQmRBY8sHQQeUKwTm2r2h8t4C8qt12CHGwXB',
        }
    },
    # Ethereum Mainnet
    'Ethereum': {
        'chain_id': '1',
        'Addr': {
            'ETH_ADDR': '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE',  # Native ETH
            'WETH_ADDR': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',  # Wrapped ETH
            'USDT_ADDR': '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # Tether USD
            'USDC_ADDR': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',  # USD Coin
            'WBTC_ADDR': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599',  # Wrapped BTC
            'DAI_ADDR': '0x6B175474E89094C44Da98b954EedeAC495271d0F',   # Dai Stablecoin
            'UNI_ADDR': '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984',   # Uniswap
            'LINK_ADDR': '0x514910771AF9Ca656af840dff83E8264EcF986CA',  # Chainlink
            'AAVE_ADDR': '0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9',  # Aave
            'MATIC_ADDR': '0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0'  # Polygon
        }
    }
}

class OkxDEX:
    """OKX DEX API wrapper class"""
    
    BASE_URL = "https://www.okx.com/api/v5/dex/aggregator"
    
    def __init__(self, credentials_path: str = "okx_credentials.json"):
        """Initialize with credentials from file or environment variables"""
        with open(credentials_path) as f:
            credentials = json.load(f)
            self.api_key = credentials["access_key"]
            self.passphrase = credentials["passphrase"] 
            self.project_id = credentials["access_project"]
            self.secret = credentials["secret_key"]
            self.solana_wallet_addr = credentials["solana_wallet_addr"]

        if not all([self.api_key, self.passphrase, self.project_id, self.secret]):
            raise ValueError("Missing required credentials")

    def _sign(self, endpoint: str, params: dict, ts: str) -> str:
        """Generate signature for request"""
        query_string = "&".join([f"{key}={value}" for key, value in params.items()])
        message = f"{ts}GET/api/v5/dex/aggregator/{endpoint}?{query_string}"
        
        signature = base64.b64encode(
            hmac.new(self.secret.encode(), message.encode(), hashlib.sha256).digest()
        ).decode()
        return signature

    def _request(self, endpoint: str, params: dict = None) -> dict:
        """Make authenticated request to API"""
        if params is None:
            params = {}
            
        ts = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        signature = self._sign(endpoint, params, ts)
        
        headers = {
            "Content-Type": "application/json",
            "OK-ACCESS-PROJECT": self.project_id,
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "OK-ACCESS-TIMESTAMP": ts,
        }

        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "ErrorCode": response.status_code,
                "ErrorMsg": response.text
            }

    def get_supported_chains(self, chain_name: str = "") -> dict:
        """Get supported chains for single-chain swaps"""
        params = {}
        params["chainId"] = CHAINS[chain_name]["chain_id"] if chain_name else ""
        return self._request("supported/chain", params)

    def get_tokens(self, chain_name: str) -> dict:
        """Get list of supported tokens"""
        params = {"chainId": CHAINS[chain_name]["chain_id"]}
        return self._request("all-tokens", params)

    def get_liquidity(self, chain_name: str) -> dict:
        """Get list of supported liquidity pools"""
        params = {"chainId": CHAINS[chain_name]["chain_id"]}
        return self._request("get-liquidity", params)

    def get_quote(self, 
                 chain_name: str,
                 amount: str,
                 from_token: str,
                 to_token: str,
                 dex_ids: str = None,
                 fee_percent: str = None,
                 price_impact_protection: str = None) -> dict:
        """Get quote for token swap"""
        params = {
            "chainId": CHAINS[chain_name]["chain_id"],
            "amount": amount,
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token
        }
        
        if dex_ids:
            params["dexIds"] = dex_ids
        if fee_percent:
            params["feePercent"] = fee_percent
        if price_impact_protection:
            params["priceImpactProtectionPercentage"] = price_impact_protection
            
        return self._request("quote", params)

    def get_approve_transaction(self,
                              chain_name: str,
                              token_address: str,
                              approve_amount: str) -> dict:
        """Get approval transaction data"""
        params = {
            "chainId": CHAINS[chain_name]["chain_id"],
            "tokenContractAddress": token_address,
            "approveAmount": approve_amount
        }
        return self._request("approve-transaction", params)

    def get_swap_transaction(self,
                           chain_name: str,
                           amount: str,
                           from_token: str,
                           to_token: str,
                           slippage: str,
                           user_address: str = None,
                           receiver_address: str = None,
                           referrer_address: str = None,
                           dex_ids: str = None,
                           fee_percent: str = None,
                           gas_limit: str = None,
                           gas_level: str = "average",
                           price_impact_protection: str = None,
                           auto_slippage: str = None,
                           max_auto_slippage: str = None) -> dict:
        """Get swap transaction data"""
        params = {
            "chainId": CHAINS[chain_name]["chain_id"],
            "amount": amount,
            "fromTokenAddress": from_token,
            "toTokenAddress": to_token,
            "slippage": slippage,
            "userWalletAddress": user_address if user_address else self.solana_wallet_addr 
        }

        # Add optional parameters
        if receiver_address:
            params["swapReceiverAddress"] = receiver_address
        if referrer_address:
            params["referrerAddress"] = referrer_address
        if dex_ids:
            params["dexIds"] = dex_ids
        if fee_percent:
            params["feePercent"] = fee_percent
        if gas_limit:
            params["gaslimit"] = gas_limit
        if gas_level:
            params["gasLevel"] = gas_level
        if price_impact_protection:
            params["priceImpactProtectionPercentage"] = price_impact_protection
        if auto_slippage:
            params["autoSlippage"] = auto_slippage
        if max_auto_slippage:
            params["maxAutoSlippage"] = max_auto_slippage

        return self._request("swap", params)

    def buy_token_by_usdt(self, chain_name: str, token_addr: str, amount: str) -> dict:
        """Convenience method to get quote for buying token with USDT"""
        return self.get_quote(
            chain_name=chain_name,
            amount=amount,
            from_token=token_addr,  
            to_token=CHAINS[chain_name]['Addr']['USDT_MINT_ADDR']  # USDT address
        )

    def sell_token_to_usdt(self, chain_name: str, token_addr: str, amount: str) -> dict:
        """Convenience method to get quote for selling token to USDT"""
        return self.get_quote(
            chain_name=chain_name,
            amount=amount,
            from_token=CHAINS[chain_name]['Addr']['USDT_MINT_ADDR'],  # USDT address
            to_token=token_addr
        ) 
    
