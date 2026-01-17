"""Execution Agent - Handles order placement and management"""

import asyncio
from typing import Dict, Optional, Any, List
from datetime import datetime
from .base_agent import BaseAgent
from ..core import MStockClient
from ..utils.config_manager import get_config
from ..utils.database import get_database
import uuid


class ExecutionAgent(BaseAgent):
    """Manages order execution and position management"""
    
    def __init__(self, mstock_client: Optional[MStockClient] = None):
        super().__init__("ExecutionAgent")
        self.client = mstock_client
        self.config = get_config()
        self.database = get_database()
        self.paper_trading = self.config.is_paper_trading()
        self.auto_trade = self.config.get('trading.auto_trade', False)
        
        # Paper trading state
        self.paper_positions: Dict[str, Dict[str, Any]] = {}
        self.paper_orders: Dict[str, Dict[str, Any]] = {}
        self.paper_balance = 100000.0  # Starting balance for paper trading
        
        # Risk management
        self.max_positions = self.config.get('trading.max_positions', 5)
        self.max_daily_loss = self.config.get('risk.max_daily_loss', 5000)
        self.daily_pnl = 0.0
    
    async def initialize(self) -> bool:
        """Initialize execution agent"""
        try:
            mode = "PAPER" if self.paper_trading else "LIVE"
            self.logger.info(f"ExecutionAgent initialized in {mode} mode")
            
            if not self.paper_trading and self.client is None:
                self.logger.error("Live trading requires mStock client")
                return False
            
            # Load existing positions
            if not self.paper_trading and self.client:
                positions = await self.client.get_positions()
                self.logger.info(f"Loaded {len(positions)} existing positions")
            
            return True
            
        except Exception as e:
            self.logger.exception(f"Failed to initialize ExecutionAgent: {e}")
            return False
    
    async def place_order(
        self,
        symbol: str,
        exchange: str,
        side: str,
        quantity: int,
        order_type: str = "MARKET",
        price: Optional[float] = None,
        strategy: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Optional[str]:
        """
        Place an order
        
        Args:
            symbol: Trading symbol
            exchange: Exchange (NSE, BSE, NFO, etc.)
            side: BUY or SELL
            quantity: Order quantity
            order_type: MARKET or LIMIT
            price: Price (required for LIMIT orders)
            strategy: Strategy name
            reason: Trade reason
        
        Returns:
            Order ID or None if failed
        """
        # Check auto-trade mode
        if not self.auto_trade:
            self.logger.info(f"Auto-trade disabled, order not placed: {side} {symbol}")
            return None
        
        # Risk checks
        if not self._risk_checks_pass():
            self.logger.warning("Risk checks failed, order not placed")
            return None
        
        # Check position limits
        if side == "BUY" and len(self.paper_positions) >= self.max_positions:
            self.logger.warning(f"Max positions ({self.max_positions}) reached")
            return None
        
        try:
            if self.paper_trading:
                return await self._place_paper_order(
                    symbol, exchange, side, quantity, order_type, price, strategy, reason
                )
            else:
                return await self._place_live_order(
                    symbol, exchange, side, quantity, order_type, price, strategy, reason
                )
        
        except Exception as e:
            self.logger.error(f"Failed to place order: {e}")
            return None
    
    async def _place_paper_order(
        self,
        symbol: str,
        exchange: str,
        side: str,
        quantity: int,
        order_type: str,
        price: Optional[float],
        strategy: Optional[str],
        reason: Optional[str]
    ) -> str:
        """Place order in paper trading mode"""
        order_id = f"PAPER_{uuid.uuid4().hex[:8]}"
        
        # Simulate order execution
        order = {
            "order_id": order_id,
            "symbol": symbol,
            "exchange": exchange,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "price": price,
            "status": "FILLED",  # Simulate immediate fill
            "filled_price": price if price else 1000.0,  # Mock price
            "filled_quantity": quantity,
            "timestamp": datetime.now().isoformat(),
            "strategy": strategy,
            "reason": reason
        }
        
        self.paper_orders[order_id] = order
        
        # Update positions
        self._update_paper_position(symbol, side, quantity, order['filled_price'])
        
        # Log to database
        self.database.insert_order(order)
        
        self.logger.info(f"Paper order placed: {order_id} - {side} {quantity} {symbol}")
        return order_id
    
    async def _place_live_order(
        self,
        symbol: str,
        exchange: str,
        side: str,
        quantity: int,
        order_type: str,
        price: Optional[float],
        strategy: Optional[str],
        reason: Optional[str]
    ) -> Optional[str]:
        """Place order in live trading mode"""
        if not self.client or not self.client.is_authenticated:
            self.logger.error("Cannot place live order: not authenticated")
            return None
        
        result = await self.client.place_order(
            symbol=symbol,
            exchange=exchange,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price
        )
        
        if result and 'order_id' in result:
            order_id = result['order_id']
            
            # Log to database
            order_data = {**result, "strategy": strategy, "reason": reason}
            self.database.insert_order(order_data)
            
            self.logger.info(f"Live order placed: {order_id} - {side} {quantity} {symbol}")
            return order_id
        
        return None
    
    def _update_paper_position(self, symbol: str, side: str, quantity: int, price: float) -> None:
        """Update paper trading position"""
        if symbol not in self.paper_positions:
            self.paper_positions[symbol] = {
                "symbol": symbol,
                "quantity": 0,
                "avg_price": 0,
                "realized_pnl": 0
            }
        
        position = self.paper_positions[symbol]
        
        if side == "BUY":
            total_cost = position['quantity'] * position['avg_price'] + quantity * price
            position['quantity'] += quantity
            position['avg_price'] = total_cost / position['quantity'] if position['quantity'] > 0 else 0
        else:  # SELL
            if position['quantity'] >= quantity:
                pnl = (price - position['avg_price']) * quantity
                position['realized_pnl'] += pnl
                position['quantity'] -= quantity
                self.daily_pnl += pnl
                
                if position['quantity'] == 0:
                    del self.paper_positions[symbol]
    
    def _risk_checks_pass(self) -> bool:
        """Perform risk management checks"""
        # Check daily loss limit
        if self.daily_pnl < -self.max_daily_loss:
            self.logger.error(f"Daily loss limit reached: {self.daily_pnl}")
            return False
        
        # Check circuit breaker
        if self.config.get('risk.circuit_breaker_enabled', True):
            if self.daily_pnl < -self.max_daily_loss * 0.8:
                self.logger.warning("Approaching daily loss limit")
        
        return True
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get current positions"""
        if self.paper_trading:
            return list(self.paper_positions.values())
        # Would fetch from client in live mode
        return []
    
    def get_pnl(self) -> Dict[str, Any]:
        """Get PnL summary"""
        if self.paper_trading:
            unrealized_pnl = sum(
                (1050.0 - pos['avg_price']) * pos['quantity']  # Mock current price
                for pos in self.paper_positions.values()
            )
            return {
                "realized_pnl": sum(pos.get('realized_pnl', 0) for pos in self.paper_positions.values()),
                "unrealized_pnl": unrealized_pnl,
                "total_pnl": self.daily_pnl + unrealized_pnl,
                "daily_pnl": self.daily_pnl
            }
        
        return {"total_pnl": 0, "daily_pnl": 0}
    
    async def run(self) -> None:
        """Main agent loop"""
        self.update_status("running")
        
        try:
            while self.is_running:
                # Monitor positions and risk
                await asyncio.sleep(10)
        
        except asyncio.CancelledError:
            self.logger.info("ExecutionAgent run loop cancelled")
        except Exception as e:
            self.logger.exception(f"Error in ExecutionAgent run loop: {e}")
        finally:
            self.update_status("stopped")
    
    async def stop(self) -> None:
        """Stop the agent"""
        self.logger.info("Stopping ExecutionAgent")
        self.is_running = False
        
        if self.task and not self.task.done():
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        self.update_status("stopped")
