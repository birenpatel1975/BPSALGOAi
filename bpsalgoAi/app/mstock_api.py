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



class MStockAPI:
    # ...existing code...

    def update_algo_top10(self, selections: List[Dict[str, Any]]):
        """
        Update Algo Agent's Top 10 selections (Tab 1)
        Args:
            selections: List of top 10 stock dicts
        """
        self.algo_top10 = selections[:10]

    def get_historical_data(self, exchange: str, instrument_token: str, interval: str, from_dt: str, to_dt: str) -> Dict[str, Any]:
        """
        Fetch historical OHLCV data for an instrument from mStock API.
        Args:
            exchange: Exchange segment (NSE, NFO, BSE, BFO)
            instrument_token: Instrument token
            interval: Interval frame (minute, day, etc.)
            from_dt: Start datetime (YYYY-MM-DD+HH:MM:SS)
            to_dt: End datetime (YYYY-MM-DD+HH:MM:SS)
        Returns:
            Dict with 'success' and 'data' (list of candles)
        """
        endpoint = f"{self.base_url}/instruments/historical/{exchange}/{instrument_token}/{interval}?from={urllib.parse.quote(from_dt)}&to={urllib.parse.quote(to_dt)}"
        headers = self._get_headers()
        try:
            resp = self.session.get(endpoint, headers=headers, timeout=10)
            if resp.ok:
                payload = resp.json()
                if payload.get('status') == 'success' and 'data' in payload and 'candles' in payload['data']:
                    # Convert API candle format to dicts
                    candles = payload['data']['candles']
                    data = []
                    for c in candles:
                        # [datetime, open, high, low, close, volume]
                        data.append({
                            'date': c[0],
                            'open': c[1],
                            'high': c[2],
                            'low': c[3],
                            'close': c[4],
                            'volume': c[5]
                        })
                    return {'success': True, 'data': data, 'mock': False}
                else:
                    return {'success': False, 'error': payload.get('message', 'No data'), 'data': []}
            else:
                return {'success': False, 'error': resp.text, 'data': []}
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return {'success': False, 'error': str(e), 'data': []}

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
    
    def get_live_data(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Get live market data for multiple symbols using mStock market fetch endpoints.
        Args:
            symbols: List of tradingsymbols (e.g., ['NIFTY50', 'BANKNIFTY', 'GIFTNIFTY', ...])
        Returns:
            Dict with 'success' and 'data' (list of quote dicts)
        """
        if not symbols:
            return {'success': False, 'error': 'No symbols provided', 'data': []}
        headers = self._get_headers()
        # Use market OHLC endpoint for batch fetch
        instruments = [f'NSE:{sym}' for sym in symbols]
        params = '&'.join([f'i={urllib.parse.quote(i)}' for i in instruments])
        endpoint = f"{self.base_url}/instruments/quote/ohlc?{params}"
        try:
            resp = self.session.get(endpoint, headers=headers, timeout=10)
            if resp.ok:
                payload = resp.json()
                if payload.get('status') == 'success' and 'data' in payload:
                    # Flatten to list of dicts for UI
                    data = []
                    for k, v in payload['data'].items():
                        v['symbol'] = k.split(':')[1] if ':' in k else k
                        v['exchange'] = k.split(':')[0] if ':' in k else 'NSE'
                        data.append(v)
                    return {'success': True, 'data': {'symbols': data}, 'mock': False}
                else:
                    return {'success': False, 'error': payload.get('message', 'No data'), 'data': []}
            else:
                return {'success': False, 'error': resp.text, 'data': []}
        except Exception as e:
            logger.error(f"Error fetching live data: {e}")
            return {'success': False, 'error': str(e), 'data': []}
    
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
            # Use a default set of indices as a proxy watchlist
            default_symbols = ['NIFTY50', 'BANKNIFTY', 'FINNIFTY', 'GIFTNIFTY', 'SENSEX']
            live = self.get_live_data(default_symbols)
            if live.get('success') and live.get('data'):
                symbols = live['data'].get('symbols', [])
                return {'success': True, 'data': symbols, 'mock': False}
            return {'success': False, 'data': [], 'mock': False}
        except Exception as e:
            logger.error(f"Error fetching watchlist: {str(e)}")
            return {'success': False, 'error': str(e), 'data': []}



    # --- Option Chain (stub/mock) ---
    def get_option_chain_master(self, exch: str) -> Dict[str, Any]:
        """Return mock option chain master data until real API is wired."""
        # Only fetch live data for a default set of indices as a proxy option chain master (stub)
        try:
            default_symbols = ['NIFTY50', 'BANKNIFTY', 'FINNIFTY', 'GIFTNIFTY', 'SENSEX']
            live = self.get_live_data(default_symbols)
            if live.get('success') and live.get('data'):
                symbols = live['data'].get('symbols', [])
                return {'success': True, 'data': symbols, 'mock': False}
            return {'success': False, 'data': [], 'mock': False}
        except Exception as e:
            logger.error(f"Error fetching option chain master: {e}")
            return {'success': False, 'error': str(e), 'mock': False}

    
