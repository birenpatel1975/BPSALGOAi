"""
mStock API Module
Handles Type A/B API calls with proper authentication headers
"""
import requests
import logging
import random
from typing import Dict, List, Any, Optional
import urllib.parse
from config import MSTOCK_WS_ENDPOINT

logger = logging.getLogger(__name__)

# Mock market data for development/fallback
MOCK_MARKET_DATA = {
    'NIFTY50': {'symbol': 'NIFTY50', 'ltp': 23500.00, 'open': 23400.00, 'high': 23650.00, 'low': 23350.00, 'volume': 150000000},
    'BANKNIFTY': {'symbol': 'BANKNIFTY', 'ltp': 47800.00, 'open': 47600.00, 'high': 48100.00, 'low': 47500.00, 'volume': 80000000},
    'FINNIFTY': {'symbol': 'FINNIFTY', 'ltp': 21450.00, 'open': 21350.00, 'high': 21600.00, 'low': 21300.00, 'volume': 50000000},
}

class MStockAPI:
    # Watchlist tab definitions
    WATCHLIST_TABS = [
        'algo_top10',    # Tab 1: Algo Agent's Top 10
        'auto',          # Tab 2: Auto Sector
        'finance',       # Tab 3: Finance/Banking
        'pharma',        # Tab 4: Pharma
        'metal',         # Tab 5: Metal
        'power',         # Tab 6: Power
        'penny'          # Tab 7: Penny Stocks
    ]

    # Example sector stock lists (replace with real symbols as needed)
    SECTOR_STOCKS = {
        'auto': ['MARUTI', 'TATAMOTORS', 'M&M', 'HEROMOTOCO', 'BAJAJ-AUTO'],
        'finance': ['HDFCBANK', 'ICICIBANK', 'KOTAKBANK', 'AXISBANK', 'SBIN'],
        'pharma': ['SUNPHARMA', 'CIPLA', 'DIVISLAB', 'DRREDDY', 'AUROPHARMA'],
        'metal': ['TATASTEEL', 'JSWSTEEL', 'HINDALCO', 'COALINDIA', 'VEDL'],
        'power': ['NTPC', 'POWERGRID', 'TATAPOWER', 'ADANIGREEN', 'RELIANCE'],
        'penny': ['SUZLON', 'YESBANK', 'IRFC', 'IDEA', 'PNB']
    }

    # Tab 1: Algo Agent's Top 10 (dynamic, updated by agent)
    algo_top10 = []

    def get_watchlist_tab(self, tab: str) -> Dict[str, Any]:
        """
        Fetch stocks for a specific watchlist tab.
        Args:
            tab: Tab name (algo_top10, auto, finance, pharma, metal, power, penny)
        Returns:
            Dictionary with tab stocks
        """
        if tab == 'algo_top10':
            # Return Algo Agent's top 10 selections
            return {'success': True, 'data': self.algo_top10, 'tab': tab}
        elif tab in self.SECTOR_STOCKS:
            # Return sector stocks
            stocks = self.SECTOR_STOCKS[tab]
            quotes = self._get_mock_quotes(stocks)
            return {'success': True, 'data': quotes, 'tab': tab}
        else:
            return {'success': False, 'data': [], 'error': 'Invalid tab', 'tab': tab}

    def update_algo_top10(self, selections: List[Dict[str, Any]]):
        """
        Update Algo Agent's Top 10 selections (Tab 1)
        Args:
            selections: List of top 10 stock dicts
        """
        self.algo_top10 = selections[:10]

    def get_historical_data(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """
        Return mock historical OHLCV data for a symbol for backtesting.
        Args:
            symbol: Stock symbol
            days: Number of days to return
        Returns:
            Dict with 'success' and 'data' (list of dicts with ohlcv)
        """
        import datetime
        base = MOCK_MARKET_DATA.get(symbol, {'ltp': 100.0, 'open': 99.0, 'high': 101.0, 'low': 98.0, 'volume': 1000000})
        today = datetime.date.today()
        data = []
        price = base['ltp']
        for i in range(days):
            date = today - datetime.timedelta(days=i)
            daily_price_change = random.uniform(-2, 2)
            open_ = round(price + random.uniform(-1, 1), 2)
            close = round(open_ + daily_price_change, 2)
            high = round(max(open_, close) + random.uniform(0, 1), 2)
            low = round(min(open_, close) - random.uniform(0, 1), 2)
            volume = int(base['volume'] * random.uniform(0.8, 1.2))
            data.append({
                'date': date.isoformat(),
                'open': open_,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
            price = close
        return {'success': True, 'data': list(reversed(data)), 'mock': True}

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
        if self.auth:
            token = self.auth.get_token()
            if token:
                # Format: token api_key:access_token (as per official docs)
                headers['Authorization'] = f'token {self.api_key}:{token}'
                logger.debug(f"Using access token in headers: {token[:20]}...")
        
        return headers

    def get_ws_url(self) -> Optional[str]:
        """
        WebSocket endpoint is not supported in REST API flow. Please refer to mStock WebSocket documentation for real-time data.
        """
        logger.error("WebSocket endpoint is not supported in REST API flow. Please refer to mStock WebSocket documentation.")
        return None
    
    def get_live_data(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get live market data for multiple symbols
        Uses Market Quotes and Instruments API endpoint
        Returns mock data if real endpoint is not available or not authenticated.
        """
        if symbols is None:
            symbols = ['NIFTY50', 'BANKNIFTY', 'FINNIFTY']
        # Always return mock data for demo/testing
        data = [MOCK_MARKET_DATA.get(sym, {'symbol': sym, 'ltp': 100.0, 'open': 99.0, 'high': 101.0, 'low': 98.0, 'volume': 1000000}) for sym in symbols]
        # Add a fake percent change for demo
        import random
        for d in data:
            d['change'] = round(random.uniform(-2, 2), 2)
            d['price'] = d.get('ltp', 100.0)
        return {
            'success': True,
            'data': {'symbols': data},
            'mock': True
        }
    
    def get_symbol_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get full quote for a single symbol
        Returns mock data for demo/testing.
        """
        try:
            d = MOCK_MARKET_DATA.get(symbol, {'symbol': symbol, 'ltp': 100.0, 'open': 99.0, 'high': 101.0, 'low': 98.0, 'volume': 1000000})
            d['change'] = round(random.uniform(-2, 2), 2)
            d['price'] = d.get('ltp', 100.0)
            return d
        except Exception as e:
            logger.warning(f"Error fetching quote for {symbol}: {str(e)}")
            return {'symbol': symbol, 'mock': True, 'error': str(e)}
    
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
    
    def get_watchlist(self) -> Dict[str, Any]:
        """
        Fetch live top gainers/losers as a watchlist replacement (Type A API).
        Uses the official endpoint for market movers.
        Returns:
            Dictionary with watchlist data and symbols
        """
        try:
            if not self.auth or not self.auth.is_token_valid():
                logger.warning("Cannot fetch watchlist: not authenticated")
                return {'success': False, 'data': [], 'error': 'Not authenticated'}

            # Use the official Top Gainers/Losers endpoint (POST /losergainer)
            endpoint = f"{self.base_url}/losergainer"
            headers = self._get_headers()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            # Example payload for NSE (Exchange=1, SecurityIdCode=13, segment=1, TypeFlag=G for gainers, L for losers)
            payload = {
                'Exchange': '1',
                'SecurityIdCode': '13',
                'segment': '1',
                'TypeFlag': 'G'  # 'G' for gainers, 'L' for losers
            }
            response = self.session.post(endpoint, data=payload, headers=headers, timeout=10)
            logger.info(f"Gainers/Losers raw response: {response.text}")
            if response.ok:
                data = response.json()
                # Try to find the array of stocks in the response
                watchlist_data = []
                if isinstance(data, list):
                    watchlist_data = data
                elif 'data' in data and isinstance(data['data'], list):
                    watchlist_data = data['data']
                elif 'gainers' in data and isinstance(data['gainers'], list):
                    watchlist_data = data['gainers']
                elif 'losers' in data and isinstance(data['losers'], list):
                    watchlist_data = data['losers']
                else:
                    # Try to find any list in the response
                    for k, v in data.items():
                        if isinstance(v, list):
                            watchlist_data = v
                            break
                if not watchlist_data:
                    logger.warning(f"No stocks found in gainers/losers response: {data}")
                return {'success': True, 'data': watchlist_data, 'raw': data}
            else:
                logger.warning(f"Gainers/Losers endpoint failed: {response.status_code} {response.text}")
                return {'success': False, 'data': [], 'error': f"Gainers/Losers endpoint failed: {response.status_code}", 'raw': response.text}
        except Exception as e:
            logger.error(f"Error fetching gainers/losers: {str(e)}")
            return {'success': False, 'data': [], 'error': str(e)}
    
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
