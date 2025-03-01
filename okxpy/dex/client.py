from typing import Optional, Dict
import requests
from ..auth import OKXAuth

class DexClient:
    """OKX DEX API client"""
    
    BASE_URL = "https://www.okx.com/api/v5/dex/aggregator"
    
    def __init__(self, auth: OKXAuth):
        self.auth = auth

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, body: Optional[Dict] = None) -> Dict:
        """Make authenticated request to API"""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self.auth.get_headers(method, f"/api/v5/dex/aggregator/{endpoint}", params, body)
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                return response.json()
            return {
                "code": str(response.status_code),
                "msg": response.text
            }
        except requests.exceptions.RequestException as e:
            return {
                "code": "500",
                "msg": str(e)
            }

    def get_supported_chains(self, chain_id: Optional[str] = None) -> Dict:
        """
        Get supported chains for single-chain swaps
        
        Args:
            chain_id: Optional chain ID to filter results
        """
        params = {}
        if chain_id:
            params["chainId"] = chain_id
        return self._request("GET", "supported/chain", params)

    def get_tokens(self, chain_id: str) -> Dict:
        """
        Get list of supported tokens for a specific chain
        
        Args:
            chain_id: Chain ID to get tokens for
        """
        params = {"chainId": chain_id}
        return self._request("GET", "all-tokens", params)

    def get_liquidity(self, chain_id: str) -> Dict:
        """
        Get list of supported liquidity pools for a specific chain
        
        Args:
            chain_id: Chain ID to get liquidity pools for
        """
        params = {"chainId": chain_id}
        return self._request("GET", "get-liquidity", params)

    def get_quote(self, 
                 chain_id: str,
                 amount: str,
                 from_token_address: str,
                 to_token_address: str,
                 dex_ids: Optional[str] = None,
                 fee_percent: Optional[str] = None,
                 price_impact_protection: Optional[str] = None) -> Dict:
        """
        Get quote for token swap
        
        Args:
            chain_id: Chain ID for the swap
            amount: Amount to swap
            from_token_address: Address of token to swap from
            to_token_address: Address of token to swap to
            dex_ids: Optional comma-separated list of DEX IDs
            fee_percent: Optional fee percentage
            price_impact_protection: Optional price impact protection percentage
        """
        params = {
            "chainId": chain_id,
            "amount": amount,
            "fromTokenAddress": from_token_address,
            "toTokenAddress": to_token_address
        }
        
        if dex_ids:
            params["dexIds"] = dex_ids
        if fee_percent:
            params["feePercent"] = fee_percent
        if price_impact_protection:
            params["priceImpactProtectionPercentage"] = price_impact_protection
            
        return self._request("GET", "quote", params)

    def get_approve_transaction(self,
                              chain_id: str,
                              token_address: str,
                              approve_amount: str) -> Dict:
        """
        Get approval transaction data
        
        Args:
            chain_id: Chain ID for the approval
            token_address: Address of token to approve
            approve_amount: Amount to approve
        """
        params = {
            "chainId": chain_id,
            "tokenContractAddress": token_address,
            "approveAmount": approve_amount
        }
        return self._request("GET", "approve-transaction", params)

    def get_swap_transaction(self,
                           chain_id: str,
                           amount: str,
                           from_token_address: str,
                           to_token_address: str,
                           slippage: str,
                           user_address: str,
                           receiver_address: Optional[str] = None,
                           referrer_address: Optional[str] = None,
                           dex_ids: Optional[str] = None,
                           fee_percent: Optional[str] = None,
                           gas_limit: Optional[str] = None,
                           gas_level: str = "average",
                           price_impact_protection: Optional[str] = None,
                           auto_slippage: Optional[str] = None,
                           max_auto_slippage: Optional[str] = None) -> Dict:
        """
        Get swap transaction data
        
        Args:
            chain_id: Chain ID for the swap
            amount: Amount to swap
            from_token_address: Address of token to swap from
            to_token_address: Address of token to swap to
            slippage: Slippage tolerance percentage
            user_address: User's wallet address
            receiver_address: Optional receiver address
            referrer_address: Optional referrer address
            dex_ids: Optional comma-separated list of DEX IDs
            fee_percent: Optional fee percentage
            gas_limit: Optional gas limit
            gas_level: Gas price level (default: "average")
            price_impact_protection: Optional price impact protection percentage
            auto_slippage: Optional auto slippage flag
            max_auto_slippage: Optional maximum auto slippage percentage
        """
        params = {
            "chainId": chain_id,
            "amount": amount,
            "fromTokenAddress": from_token_address,
            "toTokenAddress": to_token_address,
            "slippage": slippage,
            "userWalletAddress": user_address
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

        return self._request("GET", "swap", params) 