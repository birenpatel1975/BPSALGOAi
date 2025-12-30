"""
mStock API Module
Handles Type A/B API calls with proper authentication headers
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
    """Client for Type A/B API with proper authentication"""
    
    def __init__(self, base_url: str, api_key: str, auth=None):
        """
        Initialize mStock API client for Type A/B
        
        Args:
            base_url: API base URL (https://api.mstock.trade/openapi/typea or typeb)
            api_key: mStock API Key
            auth: MStockAuth instance for token management
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.auth = auth
        self.session = requests.Session()
        logger.info(f"MStockAPI initialized with base URL: {self.base_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Build request headers with proper authorization format"""
        headers = {
            'X-Mirae-Version': '1',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Add authorization if access token is available
        if self.auth and self.auth.access_token:
            # Format: token api_key:access_token (as per official docs)
            headers['Authorization'] = f'token {self.api_key}:{self.auth.access_token}'
        
        return headers
    
    def get_live_data(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get live market data for multiple symbols
        Uses Market Quotes and Instruments API endpoint
        
        Args:
            symbols: List of stock symbols (default: NIFTY50, BANKNIFTY, FINNIFTY)
            
        Returns:
            Dictionary with symbol data
        """
        if symbols is None:
            symbols = ['NIFTY50', 'BANKNIFTY', 'FINNIFTY']
        
        result = {
            'success': False,
            'data': [],
            'error': None,
            'mock': False
        }
        
        # Try to fetch from API if authenticated
        if self.auth and self.auth.is_token_valid():
            try:
                # Try multiple possible endpoints for market quotes
                endpoints = [
                    f"{self.base_url}/market/quotes",
                    f"{self.base_url}/marketquote",
                    f"{self.base_url}/quote",
                ]
                
                headers = self._get_headers()
                payload = {'symbols': symbols}
                
                for endpoint in endpoints:
                    try:
                        logger.debug(f"Fetching live data from: {endpoint}")
                        response = self.session.post(endpoint, json=payload, headers=headers, timeout=10)
                        
                        if response.ok:
                            data = response.json()
                            if data.get('status') == 'success':
                                result['success'] = True
                                result['data'] = data.get('data', [])
                                logger.info(f"Successfully fetched live data from {endpoint}")
                                return result
                    except Exception as e:
                        logger.debug(f"Endpoint {endpoint} failed: {e}")
                        continue
                
            except Exception as e:
                logger.warning(f"Error fetching live data: {str(e)}")
        else:
            logger.warning("Not authenticated. Access token missing or invalid.")
        
        # Fallback to mock data
        logger.info("Using mock data for market quotes")
        result['data'] = self._get_mock_quotes(symbols)
        result['mock'] = True
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
            if not self.auth or not self.auth.is_token_valid():
                logger.warning(f"Cannot fetch quote for {symbol}: not authenticated")
                return MOCK_MARKET_DATA.get(symbol, {'symbol': symbol, 'mock': True})
            
            endpoint = f"{self.base_url}/quote"
            headers = self._get_headers()
            params = {'symbol': symbol}
            
            logger.debug(f"Fetching quote for {symbol}")
            response = self.session.get(endpoint, params=params, headers=headers, timeout=10)
            
            if response.ok:
                data = response.json()
                if data.get('status') == 'success':
                    logger.info(f"Successfully fetched quote for {symbol}")
                    return data.get('data', {})
                
            logger.warning(f"Quote fetch failed for {symbol}: {response.status_code}")
            return MOCK_MARKET_DATA.get(symbol, {'symbol': symbol, 'mock': True})
        
        except Exception as e:
            logger.warning(f"Error fetching quote for {symbol}: {str(e)}")
            return MOCK_MARKET_DATA.get(symbol, {'symbol': symbol, 'mock': True})
    
    def get_fund_summary(self) -> Dict[str, Any]:
        """
        Get account fund summary
        Requires authentication
        
        Returns:
            Fund summary data
        """
        try:
            if not self.auth or not self.auth.is_token_valid():
                logger.warning("Cannot fetch fund summary: not authenticated")
                return {'success': False, 'error': 'Not authenticated', 'data': None}
            
            endpoint = f"{self.base_url}/user/fundsummary"
            headers = self._get_headers()
            
            logger.debug("Fetching fund summary")
            response = self.session.get(endpoint, headers=headers, timeout=10)
            
            if response.ok:
                data = response.json()
                if data.get('status') == 'success':
                    logger.info("Successfully fetched fund summary")
                    return {'success': True, 'data': data.get('data', [])}
                
            logger.warning(f"Fund summary fetch failed: {response.status_code}")
            return {'success': False, 'error': response.text, 'data': None}
        
        except Exception as e:
            logger.error(f"Error fetching fund summary: {str(e)}")
            return {'success': False, 'error': str(e), 'data': None}
    
    def place_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place a trading order
        Requires authentication
        
        Args:
            order_data: Order parameters
            
        Returns:
            Order response
        """
        try:
            if not self.auth or not self.auth.is_token_valid():
                logger.warning("Cannot place order: not authenticated")
                return {'success': False, 'error': 'Not authenticated'}
            
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
        Get account information (alias for fund summary)
        
        Returns:
            Account info dictionary
        """
        return self.get_fund_summary()
    
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
