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
    'NIFTYBANK': {'symbol': 'NIFTYBANK', 'ltp': 47800.00, 'open': 47600.00, 'high': 48100.00, 'low': 47500.00, 'volume': 80000000},
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
            # Return sector stocks; prefer live quotes when authenticated
            stocks = self.SECTOR_STOCKS[tab]
            quotes = self._get_live_or_mock_quotes(stocks)
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
            symbols = ['NIFTY50', 'NIFTYBANK', 'FINNIFTY']

        # Try real API first if authenticated
        if self.auth and self.auth.is_token_valid():
            headers = self._get_headers()
            quotes = []
            for sym in symbols:
                try:
                    endpoint = f"{self.base_url}/market/quote/{urllib.parse.quote(sym)}"
                    resp = self.session.get(endpoint, headers=headers, timeout=8)
                    if resp.ok:
                        payload = resp.json()
                        # Type A typically returns {'status':'success','data':{...}}
                        row = payload.get('data') or payload
                        if row:
                            row['symbol'] = row.get('symbol') or sym
                            quotes.append(row)
                            continue
                except Exception as e:
                    logger.debug(f"Quote fetch failed for {sym}: {e}")
                # fallback per symbol mock if this one fails
                quotes.append({**MOCK_MARKET_DATA.get(sym, {'symbol': sym}), 'mock': True})

            # Normalize to expected shape
            norm = []
            for q in quotes:
                norm.append({
                    'symbol': q.get('symbol') or q.get('trading_symbol') or q.get('symbol_name') or q.get('display_name') or 'N/A',
                    'ltp': q.get('ltp') or q.get('price') or q.get('last_price') or q.get('last') or q.get('LTP'),
                    'open': q.get('open') or q.get('Open'),
                    'high': q.get('high') or q.get('High'),
                    'low': q.get('low') or q.get('Low'),
                    'volume': q.get('volume') or q.get('Volume'),
                    'change': q.get('change') or q.get('per_change') or q.get('pchange'),
                    'pchange': q.get('per_change') or q.get('pchange') or q.get('change'),
                    'price': q.get('ltp') or q.get('price') or q.get('last_price')
                })
            return {'success': True, 'data': {'symbols': norm}, 'mock': False}

        # Fallback to mock data when not authenticated
        data = [MOCK_MARKET_DATA.get(sym, {'symbol': sym, 'ltp': 100.0, 'open': 99.0, 'high': 101.0, 'low': 98.0, 'volume': 1000000}) for sym in symbols]
        import random
        for d in data:
            d['change'] = round(random.uniform(-2, 2), 2)
            d['price'] = d.get('ltp', 100.0)
        return {'success': True, 'data': {'symbols': data}, 'mock': True}
    
    def get_symbol_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get full quote for a single symbol
        Returns mock data for demo/testing.
        """
        # Try real API first if authenticated
        if self.auth and self.auth.is_token_valid():
            try:
                endpoint = f"{self.base_url}/market/quote/{urllib.parse.quote(symbol)}"
                resp = self.session.get(endpoint, headers=self._get_headers(), timeout=8)
                if resp.ok:
                    payload = resp.json()
                    data = payload.get('data') or payload
                    if data:
                        data['symbol'] = data.get('symbol') or symbol
                        return {**data, 'success': True, 'mock': False}
            except Exception as e:
                logger.warning(f"Live quote fetch failed for {symbol}: {e}")

        # Fallback to mock
        try:
            d = MOCK_MARKET_DATA.get(symbol, {'symbol': symbol, 'ltp': 100.0, 'open': 99.0, 'high': 101.0, 'low': 98.0, 'volume': 1000000})
            d['change'] = round(random.uniform(-2, 2), 2)
            d['price'] = d.get('ltp', 100.0)
            d['mock'] = True
            d['success'] = True
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
            # If authenticated, fetch fresh quotes for indices as a proxy watchlist
            if self.auth and self.auth.is_token_valid():
                live = self.get_live_data(list(MOCK_MARKET_DATA.keys()))
                if live.get('success') and live.get('data'):
                    symbols = live['data'].get('symbols', [])
                    return {'success': True, 'data': symbols, 'mock': live.get('mock', False)}

            movers = []
            for sym, d in MOCK_MARKET_DATA.items():
                movers.append({
                    'symbol': sym,
                    'ltp': d['ltp'],
                    'open': d['open'],
                    'high': d['high'],
                    'low': d['low'],
                    'volume': d['volume'],
                    'per_change': round((d['ltp'] - d['open']) / d['open'] * 100, 2)
                })
            random.shuffle(movers)
            return {'success': True, 'data': movers, 'mock': True}
        except Exception as e:
            logger.error(f"Error fetching watchlist: {str(e)}")
            return {'success': False, 'error': str(e), 'data': []}

    def _get_live_or_mock_quotes(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Helper: prefer live quotes via get_live_data, else mock fallback."""
        try:
            live = self.get_live_data(symbols)
            if live.get('success') and live.get('data'):
                return live['data'].get('symbols', [])
        except Exception:
            logger.debug("Falling back to mock quotes", exc_info=True)
        return self._get_mock_quotes(symbols)

    # --- Option Chain (stub/mock) ---
    def get_option_chain_master(self, exch: str) -> Dict[str, Any]:
        """Return mock option chain master data until real API is wired."""
        try:
            data = {
                'dctExp': {
                    '1': 1795876200,
                    '2': 1429972200,
                },
                'OPTIDX': [
                    'BANKNIFTY,26009,2,3,4,5',
                    'FINNIFTY,26037,2,3,4',
                    'NIFTY,26000,2,3,4,5',
                ]
            }
            return {'success': True, 'data': data, 'mock': True}
        except Exception as e:
            logger.error(f"Error fetching option chain master: {e}")
            return {'success': False, 'error': str(e), 'data': None}

    def get_option_chain(self, exch: str, expiry: str, token: str, ltp: float = None) -> Dict[str, Any]:
        """Return mock option chain data with ITM/ATM/OTM buckets."""
        try:
            strikes = []
            base = float(ltp) if ltp else 23500
            # Add slight variation by token hash to avoid identical curves
            base += (abs(hash(token)) % 5) * 10
            for i in range(-3, 4):
                strike = base + i * 100
                strikes.append({
                    'strike': strike,
                    'type': 'CALL',
                    'ltp': round(120 - abs(i) * 10 + random.uniform(-2, 2), 2),
                    'oi': random.randint(5000, 20000),
                    'iv': round(12 + abs(i), 2),
                    'pchange': round(random.uniform(-3, 3), 2)
                })
                strikes.append({
                    'strike': strike,
                    'type': 'PUT',
                    'ltp': round(110 - abs(i) * 9 + random.uniform(-2, 2), 2),
                    'oi': random.randint(5000, 20000),
                    'iv': round(13 + abs(i), 2),
                    'pchange': round(random.uniform(-3, 3), 2)
                })
            # classify
            atm = [s for s in strikes if s['strike'] == base]
            itm = [s for s in strikes if s['strike'] < base][:6]
            otm = [s for s in strikes if s['strike'] > base][:6]
            return {
                'success': True,
                'data': {
                    'atm': atm,
                    'itm': itm,
                    'otm': otm
                },
                'mock': True,
                'exch': exch,
                'expiry': expiry,
                'token': token
            }
        except Exception as e:
            logger.error(f"Error fetching option chain: {e}")
            return {'success': False, 'error': str(e), 'data': None}
    
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
