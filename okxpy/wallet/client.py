from typing import Optional, Dict
import requests
from ..auth import OKXAuth

class WalletClient:
    """OKX Wallet API client"""
    
    BASE_URL = "https://www.okx.com/api/v5/wallet"
    
    def __init__(self, auth: OKXAuth):
        self.auth = auth

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, body: Optional[Dict] = None) -> Dict:
        """Make authenticated request to API"""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self.auth.get_headers(method, f"/api/v5/wallet/{endpoint}", params, body)
        
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

    def get_sign_info(self, chain_index: str, from_addr: str, to_addr: str, 
                     tx_amount: str = "0", ext_json: Optional[Dict] = None) -> Dict:
        """
        Get signing information for transaction
        
        Args:
            chain_index: Chain index for the transaction
            from_addr: Sender address
            to_addr: Recipient address
            tx_amount: Transaction amount (default: "0")
            ext_json: Optional additional parameters
        """
        body = {
            "chainIndex": chain_index,
            "fromAddr": from_addr,
            "toAddr": to_addr,
            "txAmount": tx_amount
        }
        if ext_json:
            body["extJson"] = ext_json
            
        return self._request("POST", "pre-transaction/sign-info", body=body)

    def get_gas_price(self, chain_index: str) -> Dict:
        """
        Get gas price information
        
        Args:
            chain_index: Chain index to get gas price for
        """
        params = {"chainIndex": chain_index}
        return self._request("GET", "pre-transaction/gas-price", params=params)

    def get_gas_limit(self, chain_index: str, from_addr: str, to_addr: str,
                     tx_amount: str = "0", ext_json: Optional[Dict] = None) -> Dict:
        """
        Get gas limit estimation
        
        Args:
            chain_index: Chain index for the transaction
            from_addr: Sender address
            to_addr: Recipient address
            tx_amount: Transaction amount (default: "0")
            ext_json: Optional additional parameters
        """
        body = {
            "chainIndex": chain_index,
            "fromAddr": from_addr,
            "toAddr": to_addr,
            "txAmount": tx_amount
        }
        if ext_json:
            body["extJson"] = ext_json
            
        return self._request("POST", "pre-transaction/gas-limit", body=body)

    def get_nonce(self, chain_index: str, address: str) -> Dict:
        """
        Get nonce for address
        
        Args:
            chain_index: Chain index
            address: Wallet address to get nonce for
        """
        params = {
            "address": address,
            "chainIndex": chain_index
        }
        return self._request("GET", "pre-transaction/nonce", params=params)

    def get_sui_objects(self, chain_index: str, address: str, token_address: str,
                       limit: str = "50", cursor: Optional[str] = None) -> Dict:
        """
        Get SUI objects for address
        
        Args:
            chain_index: Chain index
            address: Wallet address
            token_address: Token contract address
            limit: Number of results per page (default: "50")
            cursor: Optional pagination cursor
        """
        body = {
            "chainIndex": chain_index,
            "address": address,
            "tokenAddress": token_address,
            "limit": limit
        }
        if cursor:
            body["cursor"] = cursor
            
        return self._request("POST", "pre-transaction/sui-object", body=body)

    def validate_address(self, chain_index: str, address: str) -> Dict:
        """
        Validate address format and check blacklist
        
        Args:
            chain_index: Chain index
            address: Address to validate
        """
        params = {
            "address": address,
            "chainIndex": chain_index
        }
        return self._request("GET", "pre-transaction/validate-address", params=params)

    def broadcast_transaction(self, signed_tx: str, chain_index: str, 
                            address: str, base_fee: Optional[str] = None, 
                            priority_fee: Optional[str] = None, 
                            recent_block_hash: Optional[str] = None,
                            last_valid_block_height: Optional[str] = None) -> Dict:
        """
        Broadcast signed transaction to network
        
        Args:
            signed_tx: Signed transaction data
            chain_index: Chain index
            address: Sender address
            base_fee: Optional base fee
            priority_fee: Optional priority fee
            recent_block_hash: Optional recent block hash
            last_valid_block_height: Optional last valid block height
        """
        body = {
            "signedTx": signed_tx,
            "chainIndex": chain_index,
            "address": address
        }
        
        if base_fee:
            body["baseFee"] = base_fee
        if priority_fee:
            body["priorityFee"] = priority_fee
        if recent_block_hash:
            body["recentBlockHash"] = recent_block_hash
        if last_valid_block_height:
            body["lastValidBlockHeight"] = last_valid_block_height
            
        return self._request("POST", "pre-transaction/broadcast-transaction", body=body)

    def get_transaction_list(self, address: Optional[str] = None, 
                           account_id: Optional[str] = None,
                           chain_index: Optional[str] = None, 
                           tx_status: Optional[str] = None,
                           order_id: Optional[str] = None, 
                           cursor: Optional[str] = None,
                           limit: str = "20") -> Dict:
        """
        Get list of broadcasted transactions
        
        Args:
            address: Optional wallet address
            account_id: Optional account ID
            chain_index: Optional chain index
            tx_status: Optional transaction status
            order_id: Optional order ID
            cursor: Optional pagination cursor
            limit: Number of results per page (default: "20")
        """
        params = {}
        
        # Add parameters in alphabetical order
        if account_id:
            params["accountId"] = account_id
        if address:
            params["address"] = address
        if chain_index:
            params["chainIndex"] = chain_index
        if cursor:
            params["cursor"] = cursor
        if limit:
            params["limit"] = limit
        if order_id:
            params["orderId"] = order_id
        if tx_status:
            params["txStatus"] = tx_status
            
        return self._request("GET", "post-transaction/orders", params=params) 