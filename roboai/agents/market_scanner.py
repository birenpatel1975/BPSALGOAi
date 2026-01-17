"""Market Scanner Agent - Scans NSE and global markets"""

import asyncio
from typing import Dict, List, Optional, Any
from .base_agent import BaseAgent
from .data_agent import DataAgent
from ..utils.config_manager import get_config


class MarketScannerAgent(BaseAgent):
    """Scans markets for trading opportunities"""
    
    def __init__(self, data_agent: Optional[DataAgent] = None):
        super().__init__("MarketScannerAgent")
        self.data_agent = data_agent
        self.config = get_config()
        self.scan_interval = self.config.get('scanning.scan_interval', 60)
        self.indices = self.config.get_indices()
    
    async def initialize(self) -> bool:
        """Initialize market scanner agent"""
        try:
            if self.data_agent is None:
                self.logger.warning("No data agent provided")
            
            self.logger.info(f"MarketScannerAgent initialized. Monitoring {len(self.indices)} indices")
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize MarketScannerAgent: {e}")
            return False
    
    async def scan_market(self) -> Dict[str, Any]:
        """
        Scan market for opportunities
        
        Returns:
            Scan results
        """
        results = {
            "timestamp": asyncio.get_event_loop().time(),
            "indices": {},
            "opportunities": []
        }
        
        if self.data_agent:
            # Get quotes for all indices
            quotes = await self.data_agent.get_bulk_quotes(self.indices, "NSE")
            results["indices"] = quotes
            
            # Analyze for opportunities
            for symbol, quote in quotes.items():
                opportunity = self._analyze_opportunity(symbol, quote)
                if opportunity:
                    results["opportunities"].append(opportunity)
        
        return results
    
    def _analyze_opportunity(self, symbol: str, quote: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze if there's a trading opportunity
        
        Args:
            symbol: Symbol
            quote: Quote data
        
        Returns:
            Opportunity details or None
        """
        # Simple example - would be more sophisticated in production
        ltp = quote.get('ltp', 0)
        high = quote.get('high', 0)
        low = quote.get('low', 0)
        
        if ltp > 0 and high > 0 and low > 0:
            range_percent = ((high - low) / low) * 100
            
            # Look for high volatility
            if range_percent > 2.0:
                return {
                    "symbol": symbol,
                    "type": "HIGH_VOLATILITY",
                    "ltp": ltp,
                    "range_percent": range_percent,
                    "score": range_percent / 5.0  # Simple scoring
                }
        
        return None
    
    async def run(self) -> None:
        """Main agent loop"""
        self.update_status("running")
        
        try:
            while self.is_running:
                # Scan market
                results = await self.scan_market()
                
                if results["opportunities"]:
                    self.logger.info(f"Found {len(results['opportunities'])} opportunities")
                
                await asyncio.sleep(self.scan_interval)
        
        except asyncio.CancelledError:
            self.logger.info("MarketScannerAgent run loop cancelled")
        except Exception as e:
            self.logger.exception(f"Error in MarketScannerAgent run loop: {e}")
        finally:
            self.update_status("stopped")
    
    async def stop(self) -> None:
        """Stop the agent"""
        self.logger.info("Stopping MarketScannerAgent")
        self.is_running = False
        
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        self.update_status("stopped")
