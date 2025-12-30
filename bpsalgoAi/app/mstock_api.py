"""
mStock API Integration Module
Handles Type A API calls for fetching live market data
"""
import requests
import json
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class MStockAPI:
    """Class to handle mStock Type A API requests"""
    
    def __init__(self, api_key: str, api_type: str = 'A', totp_enabled: bool = False, base_url: str = None, live_path: str = None, api_key_header: str = None, api_key_prefix: str = None):
        """
        Initialize MStock API client
        
        Args:
            api_key: API key for Type A API
            api_type: Type of API (A)
            totp_enabled: Whether TOTP is enabled (disabled in this case)
            base_url: Base URL for the mStock API (optional)
        """
        self.api_key = api_key
        self.api_type = api_type
        self.totp_enabled = totp_enabled
        self.base_url = base_url or "https://api.mstock.com"
        self.live_path = live_path or '/v1/market/live'
        self.api_key_header = api_key_header or 'Authorization'
        self.api_key_prefix = api_key_prefix or 'Bearer '

        self.session = requests.Session()
        # Build authorization header according to config
        auth_value = (self.api_key_prefix or '') + self.api_key
        headers = {
            self.api_key_header: auth_value,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        # Remove possible None keys
        headers = {k: v for k, v in headers.items() if k and v is not None}
        self.session.headers.update(headers)
        logger.info(f"MStockAPI initialized with base URL: {self.base_url} and live path: {self.live_path}")
        
    def get_live_data(self, symbol: str = None) -> Dict[str, Any]:
        """
        Fetch live market data from mStock API
        
        Args:
            symbol: Stock symbol (optional, fetches multiple if not specified)
            
        Returns:
            Dictionary containing live market data
        """
        try:
            # Placeholder endpoint - replace with actual mStock API endpoint
            endpoint = f"{self.base_url.rstrip('/')}{self.live_path}"

            params = {
                'type': self.api_type,
                'totp': str(self.totp_enabled).lower()
            }
            
            if symbol:
                params['symbol'] = symbol
                
            response = self.session.get(endpoint, params=params, timeout=10)
            # If the endpoint returns non-2xx, capture details for diagnostics
            if not response.ok:
                text = None
                try:
                    text = response.text
                except Exception:
                    text = '<unable to read response text>'
                logger.error(f"Live data endpoint returned {response.status_code}: {text}")
                return {
                    'success': False,
                    'error': f'{response.status_code} {response.reason}',
                    'status_code': response.status_code,
                    'raw': text
                }

            data = response.json()
            logger.info(f"Successfully fetched live data for {symbol if symbol else 'all symbols'}")
            return {
                'success': True,
                'data': data,
                'status': 'Live data fetched successfully'
            }
            
        except requests.exceptions.Timeout:
            logger.error("API request timeout")
            # Return mock data but indicate it's a fallback
            return {
                'success': True,
                'used_mock': True,
                'warning': 'API request timeout - showing mock data',
                'data': self._get_mock_data()
            }
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to API")
            return {
                'success': True,
                'used_mock': True,
                'warning': 'Failed to connect to API - showing mock data',
                'data': self._get_mock_data()
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {
                'success': True,
                'used_mock': True,
                'warning': f'API request failed: {str(e)} - showing mock data',
                'data': self._get_mock_data()
            }
    
    def get_symbol_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get quote for a specific symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Quote data for the symbol
        """
        try:
            endpoint = f"{self.base_url}/v1/market/quote/{symbol}"
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            
            return {
                'success': True,
                'data': response.json()
            }
        except Exception as e:
            logger.error(f"Failed to get quote for {symbol}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': self._get_mock_quote(symbol)
            }
    
    def place_order(self, symbol: str, quantity: int, price: float, order_type: str = 'BUY') -> Dict[str, Any]:
        """
        Place an order (for Algo Agent)
        
        Args:
            symbol: Stock symbol
            quantity: Quantity to buy/sell
            price: Price per share
            order_type: BUY or SELL
            
        Returns:
            Order placement response
        """
        try:
            endpoint = f"{self.base_url}/v1/orders/place"
            payload = {
                'symbol': symbol,
                'quantity': quantity,
                'price': price,
                'order_type': order_type,
                'api_type': self.api_type
            }
            
            response = self.session.post(endpoint, json=payload, timeout=10)
            response.raise_for_status()
            
            return {
                'success': True,
                'data': response.json(),
                'message': f"Order placed successfully for {symbol}"
            }
        except Exception as e:
            logger.error(f"Failed to place order: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get mStock account information
        
        Returns:
            Account info data
        """
        try:
            endpoint = f"{self.base_url}/v1/account/info"
            response = self.session.get(endpoint, timeout=10)
            response.raise_for_status()
            
            return {
                'success': True,
                'data': response.json()
            }
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': self._get_mock_account_info()
            }
    
    @staticmethod
    def _get_mock_data() -> Dict[str, Any]:
        """Return mock data for testing"""
        return {
            'symbols': [
                {'symbol': 'AAPL', 'price': 150.25, 'change': 2.5, 'timestamp': 'Live'},
                {'symbol': 'GOOGL', 'price': 140.50, 'change': -1.2, 'timestamp': 'Live'},
                {'symbol': 'MSFT', 'price': 380.75, 'change': 3.1, 'timestamp': 'Live'}
            ]
        }
    
    @staticmethod
    def _get_mock_quote(symbol: str) -> Dict[str, Any]:
        """Return mock quote for a symbol"""
        return {
            'symbol': symbol,
            'price': 150.00,
            'bid': 149.95,
            'ask': 150.05,
            'timestamp': 'Live'
        }
    
    @staticmethod
    def _get_mock_account_info() -> Dict[str, Any]:
        """Return mock account info"""
        return {
            'account_id': 'default',
            'balance': 100000.00,
            'buying_power': 200000.00,
            'api_type': 'A',
            'totp_enabled': False
        }
