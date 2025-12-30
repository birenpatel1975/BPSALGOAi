"""
Algo Agent Module
Handles automated trading algorithm logic
"""
import threading
import logging
from typing import Dict, Any
from datetime import datetime
from app.mstock_api import MStockAPI

logger = logging.getLogger(__name__)

class AlgoAgent:
    """Automated trading algorithm agent"""
    
    def __init__(self, api_client: MStockAPI):
        """
        Initialize Algo Agent
        
        Args:
            api_client: MStockAPI client instance
        """
        self.api_client = api_client
        self.is_running = False
        self.thread = None
        self.status = 'STOPPED'
        self.last_execution = None
        self.trade_count = 0
        self.logs = []
        
    def start(self) -> Dict[str, Any]:
        """Start the Algo Agent"""
        if self.is_running:
            return {
                'success': False,
                'message': 'Algo Agent is already running'
            }
        
        self.is_running = True
        self.status = 'RUNNING'
        self.thread = threading.Thread(target=self._run_algorithm, daemon=True)
        self.thread.start()
        
        self.log_action('Algo Agent started')
        
        return {
            'success': True,
            'message': 'Algo Agent started successfully',
            'status': self.status
        }
    
    def stop(self) -> Dict[str, Any]:
        """Stop the Algo Agent"""
        if not self.is_running:
            return {
                'success': False,
                'message': 'Algo Agent is not running'
            }
        
        self.is_running = False
        self.status = 'STOPPED'
        
        self.log_action('Algo Agent stopped')
        
        return {
            'success': True,
            'message': 'Algo Agent stopped successfully',
            'status': self.status
        }
    
    def _run_algorithm(self):
        """Main algorithm loop"""
        while self.is_running:
            try:
                # Fetch live data
                live_data = self.api_client.get_live_data()
                
                if live_data['success']:
                    # Analyze data and execute trades (simplified logic)
                    self._analyze_and_trade(live_data['data'])
                    self.last_execution = datetime.now()
                
                # Sleep for a short period before next iteration
                import time
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in algorithm loop: {str(e)}")
                self.log_action(f"Error: {str(e)}")
    
    def _analyze_and_trade(self, market_data: Dict[str, Any]):
        """
        Analyze market data and execute trades
        
        Args:
            market_data: Live market data from API
        """
        try:
            # Simplified trading logic
            if 'symbols' in market_data:
                for symbol_data in market_data['symbols']:
                    symbol = symbol_data.get('symbol')
                    change = symbol_data.get('change', 0)
                    
                    # Simple strategy: if price moved >1%, consider trading
                    if abs(change) > 1.0:
                        trade_type = 'BUY' if change > 0 else 'SELL'
                        self.log_action(f"Signal detected for {symbol}: {trade_type} ({change}%)")
                        self.trade_count += 1
                        
        except Exception as e:
            logger.error(f"Error in analyze_and_trade: {str(e)}")
    
    def log_action(self, action: str):
        """
        Log an action
        
        Args:
            action: Action description
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {action}"
        self.logs.append(log_entry)
        logger.info(log_entry)
        
        # Keep only last 100 logs
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            'status': self.status,
            'is_running': self.is_running,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'trade_count': self.trade_count,
            'recent_logs': self.logs[-10:] if self.logs else []
        }
