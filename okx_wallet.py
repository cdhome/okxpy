"""
OKX Wallet API wrapper
Implements all endpoints from:
- Sign Info API
- Gas Price API
- Gas Limit API
- Nonce API
- SUI Object API
- Address Validation API
- Transaction Broadcasting API
- Transaction List API
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

class OkxWallet:
    """OKX Wallet API wrapper class"""
    
    BASE_URL = "https://www.okx.com"
    
    def __init__(self, credentials_path: str = "okx_credentials.json"):
        """Initialize with credentials from file or environment variables"""
        with open(credentials_path) as f:
            credentials = json.load(f)
            self.api_key = credentials["access_key"]
            self.passphrase = credentials["passphrase"] 
            self.project_id = credentials["access_project"]
            self.secret = credentials["secret_key"]
            self.solana_wallet_addr = credentials["solana_wallet_addr"]
            self.account_id = credentials.get("account_id")  # 可选的账户ID

        if not all([self.api_key, self.passphrase, self.project_id, self.secret]):
            raise ValueError("Missing required credentials")

    def _get_timestamp(self) -> str:
        """
        生成符合OKX API要求的ISO格式时间戳
        格式: YYYY-MM-DDThh:mm:ss.sssZ
        """
        return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

    def _sign(self, method: str, endpoint: str, params: dict = None, body: dict = None, ts: str = None) -> tuple:
        """Generate signature for request
        根据 OKX API 文档要求生成签名
        """
        if ts is None:
            ts = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
            
        # 构建签名字符串
        request_path = f"/api/v5/wallet/{endpoint}"
        
        # 确保方法是大写的
        method = method.upper()
        
        # 根据请求类型构建消息
        if method == "GET" and params:
            # 对参数按字母顺序排序
            sorted_params = sorted(params.items())
            query_string = "&".join([f"{key}={value}" for key, value in sorted_params])
            request_path = f"{request_path}?{query_string}"
            message = ts + method + request_path
        elif method == "POST" and body:
            # POST请求需要对body进行JSON序列化，且不能有空格
            body_str = json.dumps(body)  # 不使用 separators 参数
            message = ts + method + request_path + body_str
        else:
            message = ts + method + request_path
            
        print(f"\n=== 生成签名 ===")
        print(f"Method: {method}")
        print(f"Endpoint: {endpoint}")
        print(f"Timestamp: {ts}")
        print(f"Request path: {request_path}")
        print(f"Message to sign: {message}")
        
        try:
            # 使用HMAC-SHA256生成签名
            signature = base64.b64encode(
                hmac.new(
                    self.secret.encode('utf-8'),
                    message.encode('utf-8'),
                    hashlib.sha256
                ).digest()
            ).decode('utf-8')
            
            print(f"Generated signature: {signature}")
            return signature, ts
            
        except Exception as e:
            print(f"签名生成错误: {str(e)}")
            raise

    def _request(self, method: str, endpoint: str, params: dict = None, body: dict = None) -> dict:
        """Make authenticated request to API"""
        ts = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        signature, ts = self._sign(method, endpoint, params, body, ts)
        
        headers = {
            "Content-Type": "application/json",
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": ts,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "OK-ACCESS-PROJECT": self.project_id
        }

        url = f"{self.BASE_URL}/api/v5/wallet/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=body)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "code": str(response.status_code),
                    "msg": response.text
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "code": str(getattr(e.response, 'status_code', '500')),
                "msg": str(e)
            }

    def get_sign_info(self, chain_index: str, from_addr: str, to_addr: str, 
                     tx_amount: str = "0", ext_json: dict = None) -> dict:
        """Get signing information for transaction"""
        body = {
            "chainIndex": chain_index,
            "fromAddr": from_addr,
            "toAddr": to_addr,
            "txAmount": tx_amount
        }
        if ext_json:
            body["extJson"] = ext_json
            
        return self._request("POST", "pre-transaction/sign-info", body=body)

    def get_gas_price(self, chain_index: str) -> dict:
        """Get gas price information"""
        params = {"chainIndex": chain_index}
        return self._request("GET", "pre-transaction/gas-price", params=params)

    def get_gas_limit(self, chain_index: str, from_addr: str, to_addr: str,
                     tx_amount: str = "0", ext_json: dict = None) -> dict:
        """Get gas limit estimation"""
        body = {
            "chainIndex": chain_index,
            "fromAddr": from_addr,
            "toAddr": to_addr,
            "txAmount": tx_amount
        }
        if ext_json:
            body["extJson"] = ext_json
            
        return self._request("POST", "pre-transaction/gas-limit", body=body)

    def get_nonce(self, chain_index: str, address: str) -> dict:
        """Get nonce for address"""
        params = {
            "address": address,
            "chainIndex": chain_index
        }
        return self._request("GET", "pre-transaction/nonce", params=params)

    def get_sui_objects(self, chain_index: str, address: str, token_address: str,
                       limit: str = "50", cursor: str = None) -> dict:
        """Get SUI objects for address"""
        body = {
            "chainIndex": chain_index,
            "address": address,
            "tokenAddress": token_address,
            "limit": limit
        }
        if cursor:
            body["cursor"] = cursor
            
        return self._request("POST", "pre-transaction/sui-object", body=body)

    def validate_address(self, chain_index: str, address: str) -> dict:
        """Validate address format and check blacklist"""
        params = {
            "address": address,
            "chainIndex": chain_index
        }
        return self._request("GET", "pre-transaction/validate-address", params=params)

    def broadcast_transaction(self, signed_tx: str, chain_index: str, 
                            address: str, base_fee: str = None, 
                            priority_fee: str = None, recent_block_hash: str = None,
                            last_valid_block_height: str = None) -> dict:
        """Broadcast signed transaction to network"""
        body = {
            "signedTx": signed_tx,
            "chainIndex": chain_index,
            "address": address
        }
        
        # 添加可选参数
        if base_fee:
            body["baseFee"] = base_fee
        if priority_fee:
            body["priorityFee"] = priority_fee
        if recent_block_hash:
            body["recentBlockHash"] = recent_block_hash
        if last_valid_block_height:
            body["lastValidBlockHeight"] = last_valid_block_height
            
        return self._request("POST", "pre-transaction/broadcast-transaction", body=body)

    def get_transaction_list(self, address: str = None, account_id: str = None,
                           chain_index: str = None, tx_status: str = None,
                           order_id: str = None, cursor: str = None,
                           limit: str = "20") -> dict:
        """Get list of broadcasted transactions"""
        params = {}
        
        # 按字母顺序添加参数
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
