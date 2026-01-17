"""Data Agent - Handles real-time data fetching and caching"""

import asyncio
import random
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from ..core import MStockClient
from ..utils.database import get_database


class DataAgent(BaseAgent):
    """Manages real-time market data fetching and caching"""
    
    def __init__(self, mstock_client: Optional[MStockClient] = None):
        super().__init__("DataAgent")
        self.client = mstock_client
        self.database = get_database()
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 5  # Cache TTL in seconds
        self.subscribed_symbols: List[str] = []
    
    async def initialize(self) -> bool:
        """Initialize data agent"""
        try:
            if self.client is None:
                self.logger.warning("No mStock client provided, operating in mock mode")
            
            self.logger.info("DataAgent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize DataAgent: {e}")
            return False
    
    def subscribe(self, symbol: str, exchange: str = "NSE") -> None:
        """
        Subscribe to a symbol for real-time updates
        
        Args:
            symbol: Symbol to subscribe
            exchange: Exchange
        """
        symbol_key = f"{exchange}:{symbol}"
        if symbol_key not in self.subscribed_symbols:
            self.subscribed_symbols.append(symbol_key)
            self.logger.info(f"Subscribed to {symbol_key}")
    
    def unsubscribe(self, symbol: str, exchange: str = "NSE") -> None:
        """
        Unsubscribe from a symbol
        
        Args:
            symbol: Symbol to unsubscribe
            exchange: Exchange
        """
        symbol_key = f"{exchange}:{symbol}"
        if symbol_key in self.subscribed_symbols:
            self.subscribed_symbols.remove(symbol_key)
            self.logger.info(f"Unsubscribed from {symbol_key}")
    
    async def get_quote(self, symbol: str, exchange: str = "NSE", use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get quote for a symbol
        
        Args:
            symbol: Symbol
            exchange: Exchange
            use_cache: Whether to use cached data
        
        Returns:
            Quote data or None
        """
        symbol_key = f"{exchange}:{symbol}"
        
        # Check cache first
        if use_cache and symbol_key in self.cache:
            cached_data = self.cache[symbol_key]
            cache_time = cached_data.get('_cached_at')
            
            if cache_time and (datetime.now() - cache_time).total_seconds() < self.cache_ttl:
                return cached_data
        
        # Fetch from API
        try:
            if self.client and self.client.is_authenticated:
                quote = await self.client.get_quote(symbol, exchange)
            else:
                # Mock data when no client
                quote = self._generate_mock_quote(symbol, exchange)
            
            # Update cache
            quote['_cached_at'] = datetime.now()
            self.cache[symbol_key] = quote
            
            # Store in database
            self.database.insert_market_data(symbol, quote)
            
            return quote
            
        except Exception as e:
            self.logger.error(f"Failed to get quote for {symbol_key}: {e}")
            return None
    
    def _generate_mock_quote(self, symbol: str, exchange: str) -> Dict[str, Any]:
        """Generate mock quote data for testing"""
        base_price = 1000.0
        
        return {
            "symbol": symbol,
            "exchange": exchange,
            "ltp": base_price + random.uniform(-50, 50),
            "open": base_price,
            "high": base_price + random.uniform(0, 100),
            "low": base_price - random.uniform(0, 100),
            "close": base_price + random.uniform(-20, 20),
            "volume": random.randint(100000, 1000000),
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_bulk_quotes(self, symbols: List[str], exchange: str = "NSE") -> Dict[str, Dict[str, Any]]:
        """
        Get quotes for multiple symbols
        
        Args:
            symbols: List of symbols
            exchange: Exchange
        
        Returns:
            Dictionary mapping symbols to quote data
        """
        quotes = {}
        
        # Fetch all quotes concurrently
        tasks = [self.get_quote(symbol, exchange) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                self.logger.error(f"Error fetching {symbol}: {result}")
            elif result is not None:
                quotes[symbol] = result
        
        return quotes
    
    async def run(self) -> None:
        """Main agent loop"""
        self.update_status("running")
        
        try:
            while self.is_running:
                # Update subscribed symbols
                if self.subscribed_symbols:
                    symbols = [s.split(':')[1] for s in self.subscribed_symbols]
                    await self.get_bulk_quotes(symbols)
                
                await asyncio.sleep(5)  # Update every 5 seconds
        
        except asyncio.CancelledError:
            self.logger.info("DataAgent run loop cancelled")
        except Exception as e:
            self.logger.exception(f"Error in DataAgent run loop: {e}")
        finally:
            self.update_status("stopped")
    
    async def stop(self) -> None:
        """Stop the agent"""
        self.logger.info("Stopping DataAgent")
        self.is_running = False
        
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        self.update_status("stopped")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cached_symbols": len(self.cache),
            "subscribed_symbols": len(self.subscribed_symbols),
            "cache_ttl": self.cache_ttl
        }
