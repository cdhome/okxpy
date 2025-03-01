from typing import Optional, Dict, List
import requests
from ..auth import OKXAuth

class DefiExploreClient:
    """OKX DeFi Explore API client"""
    
    BASE_URL = "https://www.okx.com/api/v5/defi/explore"
    
    def __init__(self, auth: OKXAuth):
        self.auth = auth

    def _request(self, method: str, endpoint: str, params: Optional[Dict] = None, body: Optional[Dict] = None) -> Dict:
        """Make authenticated request to API"""
        url = f"{self.BASE_URL}/{endpoint}"
        headers = self.auth.get_headers(method, f"/api/v5/defi/explore/{endpoint}", params, body)
        
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

    def get_protocol_list(self, platform_id: Optional[str] = None, 
                         platform_name: Optional[str] = None) -> Dict:
        """
        Get protocol list
        
        Args:
            platform_id: Optional platform ID
            platform_name: Optional platform name
        """
        params = {}
        if platform_id:
            params["platformId"] = platform_id
        if platform_name:
            params["platformName"] = platform_name
            
        return self._request("GET", "protocol/list", params)

    def get_token_list(self, token_address: Optional[str] = None, 
                      chain_id: Optional[str] = None) -> Dict:
        """
        Get token list
        
        Args:
            token_address: Optional token contract address
            chain_id: Optional chain ID
        """
        params = {}
        if token_address:
            params["tokenAddress"] = token_address
        if chain_id:
            params["chainId"] = chain_id
            
        return self._request("GET", "token/list", params)

    def get_product_list(self, network: str, simplify_invest_type: str,
                        pool_version: Optional[str] = None,
                        platform_ids: Optional[List[str]] = None,
                        token_ids: Optional[List[str]] = None,
                        sort: Optional[Dict] = None,
                        offset: Optional[str] = None,
                        limit: str = "20") -> Dict:
        """
        Get product list
        
        Args:
            network: Network name
            simplify_invest_type: Investment type (100: Stablecoin, 101: Single token, etc.)
            pool_version: Optional pool version
            platform_ids: Optional list of platform IDs
            token_ids: Optional list of token IDs
            sort: Optional sorting parameters
            offset: Optional pagination offset
            limit: Number of results per page (default: "20")
        """
        body = {
            "network": network,
            "simplifyInvestType": simplify_invest_type,
            "limit": limit
        }
        
        if pool_version:
            body["poolVersion"] = pool_version
        if platform_ids:
            body["platformIds"] = platform_ids
        if token_ids:
            body["tokenIds"] = token_ids
        if sort:
            body["sort"] = sort
        if offset:
            body["offset"] = offset
            
        return self._request("POST", "product/list", body=body)

    def get_product_detail(self, investment_id: str, 
                          investment_category: Optional[str] = None) -> Dict:
        """
        Get product detail
        
        Args:
            investment_id: Investment product ID
            investment_category: Optional investment category
        """
        params = {"investmentId": investment_id}
        if investment_category:
            params["investmentCategory"] = investment_category
            
        return self._request("GET", "product/detail", params)

    def get_network_list(self, network: Optional[str] = None,
                        chain_id: Optional[str] = None) -> Dict:
        """
        Get network list
        
        Args:
            network: Optional network name
            chain_id: Optional chain ID
        """
        params = {}
        if network:
            params["network"] = network
        if chain_id:
            params["chainId"] = chain_id
            
        return self._request("GET", "network-list", params) 