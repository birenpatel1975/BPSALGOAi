"""
mStock Market Data API Module
Implements Type M API for live market data (LTP, quotes, depth)
"""
import requests
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Mock market data for development/fallback
MOCK_MARKET_DATA = {
    'NIFTY50': {'symbol': 'NIFTY50', 'ltp': 23500.00, 'open': 23400.00, 'high': 23650.00, 'low': 23350.00, 'volume': 150000000},
    'BANKNIFTY': {'symbol': 'BANKNIFTY', 'ltp': 47800.00, 'open': 47600.00, 'high': 48100.00, 'low': 47500.00, 'volume': 80000000},
    'FINNIFTY': {'symbol': 'FINNIFTY', 'ltp': 21450.00, 'open': 21350.00, 'high': 21600.00, 'low': 21300.00, 'volume': 50000000},
}

class MStockAPI:
    """Client for Type M API (market data)"""
    
    def __init__(self, base_url: str, jwt_token: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize MStock API client for Type M (market data)
        
        Args:
            base_url: Type M API base URL (e.g., https://api.mstock.trade/openapi/market)
            jwt_token: JWT token from Type A authentication
            api_key: API key as fallback
        """
        self.base_url = base_url.rstrip('/')
        self.jwt_token = jwt_token
        self.api_key = api_key
        self.session = requests.Session()
        logger.info(f"MStockAPI initialized with Type M base URL: {self.base_url}")
    
    def set_jwt_token(self, token: str):
        """Update JWT token from Type A auth"""
        self.jwt_token = token
        logger.debug("JWT token updated in MStockAPI client")
    
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers with JWT token"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add JWT token if available
        if self.jwt_token:
            headers['Authorization'] = f'Bearer {self.jwt_token}'
        elif self.api_key:
            headers['X-API-Key'] = self.api_key
        
        return headers
    
    def get_live_data(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get live market data for multiple symbols
        
        Args:
            symbols: List of stock symbols (default: NIFTY50, BANKNIFTY, FINNIFTY)
            
        Returns:
            Dictionary with symbol data and quotes
        """
        if symbols is None:
            symbols = ['NIFTY50', 'BANKNIFTY', 'FINNIFTY']
        
        result = {
            'success': False,
            'data': [],
            'error': None
        }
        
        try:
            # Try to fetch live quotes from Type M API
            endpoint = f"{self.base_url}/quotes"
            headers = self._get_headers()
            
            payload = {
                'mode': 'LTP',  # Last Traded Price
                'symbols': symbols
            }
            
            logger.debug(f"Fetching live data from Type M API: {endpoint}")
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=10)
            
            if response.ok:
                data = response.json()
                result['success'] = True
                result['data'] = data.get('quotes', [])
                logger.info(f"Successfully fetched live data for {len(result['data'])} symbols")
                return result
            else:
                logger.warning(f"Type M /quotes failed with status {response.status_code}: {response.text}")
                # Fall back to mock data
                result['data'] = self._get_mock_quotes(symbols)
                return result
        
        except requests.exceptions.Timeout:
            logger.warning("Type M API request timeout, using mock data")
            result['data'] = self._get_mock_quotes(symbols)
            return result
        except requests.exceptions.ConnectionError:
            logger.warning(f"Failed to connect to Type M API at {self.base_url}, using mock data")
            result['data'] = self._get_mock_quotes(symbols)
            return result
        except Exception as e:
            logger.error(f"Error fetching live data: {str(e)}")
            result['data'] = self._get_mock_quotes(symbols)
            return result
    
    def get_symbol_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get full quote for a single symbol
        
        Args:
            symbol: Stock symbol (e.g., 'NIFTY50')
            
        Returns:
            Quote data dictionary
        """
        try:
            endpoint = f"{self.base_url}/quote"
            headers = self._get_headers()
            
            params = {'symbol': symbol}
            
            logger.debug(f"Fetching quote for {symbol} from Type M API")
            response = self.session.get(endpoint, params=params, headers=headers, timeout=10)
            
            if response.ok:
                data = response.json()
                logger.info(f"Successfully fetched quote for {symbol}")
                return data.get('quote', {})
            else:
                logger.warning(f"Type M /quote failed for {symbol}: {response.status_code}")
                return MOCK_MARKET_DATA.get(symbol, {})
        
        except Exception as e:
            logger.warning(f"Error fetching quote for {symbol}: {str(e)}")
            return MOCK_MARKET_DATA.get(symbol, {})
    
    def get_market_depth(self, symbol: str) -> Dict[str, Any]:
        """
        Get market depth (bid/ask) for a symbol
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Market depth data
        """
        try:
            endpoint = f"{self.base_url}/depth"
            headers = self._get_headers()
            
            params = {'symbol': symbol}
            
            logger.debug(f"Fetching depth for {symbol} from Type M API")
            response = self.session.get(endpoint, params=params, headers=headers, timeout=10)
            
            if response.ok:
                data = response.json()
                logger.info(f"Successfully fetched depth for {symbol}")
                return data.get('depth', {})
            else:
                logger.warning(f"Type M /depth failed for {symbol}: {response.status_code}")
                return {'bids': [], 'asks': []}
        
        except Exception as e:
            logger.warning(f"Error fetching depth for {symbol}: {str(e)}")
            return {'bids': [], 'asks': []}
    
    def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place an order (requires Type A API, but making request from here)
        
        Args:
            order_data: Order parameters
            
        Returns:
            Order response
        """
        try:
            # Note: Orders might require Type A API endpoint
            endpoint = f"{self.base_url}/order/place"
            headers = self._get_headers()
            
            logger.debug(f"Placing order: {order_data}")
            response = self.session.post(endpoint, json=order_data, headers=headers, timeout=10)
            
            if response.ok:
                return response.json()
            else:
                return {'success': False, 'error': response.text}
        
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information (requires Type A API)
        
        Returns:
            Account info dictionary
        """
        try:
            endpoint = f"{self.base_url}/account/info"
            headers = self._get_headers()
            
            logger.debug("Fetching account info")
            response = self.session.get(endpoint, headers=headers, timeout=10)
            
            if response.ok:
                return response.json()
            else:
                return {'success': False, 'error': response.text}
        
        except Exception as e:
            logger.error(f"Error fetching account info: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_mock_quotes(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """
        Get mock quote data for fallback
        
        Args:
            symbols: List of symbols
            
        Returns:
            List of mock quote dictionaries
        """
        return [
            {**MOCK_MARKET_DATA.get(symbol, {'symbol': symbol}), 'mock': True}
            for symbol in symbols
        ]
