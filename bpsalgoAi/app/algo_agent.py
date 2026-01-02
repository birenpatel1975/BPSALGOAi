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
        self.trade_mode = 'paper'  # 'paper' or 'live'
        
    def start(self, trade_mode: str = None) -> Dict[str, Any]:
        """Start the Algo Agent, optionally setting trade mode ('paper', 'live', or 'backtest')"""
        if self.is_running:
            return {
                'success': False,
                'message': 'Algo Agent is already running'
            }
        if trade_mode in ('paper', 'live', 'backtest'):
            self.trade_mode = trade_mode
        else:
            self.trade_mode = 'paper'
        self.is_running = True
        self.status = 'RUNNING'
        if self.trade_mode == 'backtest':
            self.thread = threading.Thread(target=self._run_backtest, daemon=True)
        else:
            self.thread = threading.Thread(target=self._run_algorithm, daemon=True)
        self.thread.start()
        self.log_action(f"Algo Agent started in {self.trade_mode.upper()} mode")
        return {
            'success': True,
            'message': f'Algo Agent started successfully in {self.trade_mode.upper()} mode',
            'status': self.status,
            'trade_mode': self.trade_mode
        }

    def _run_backtest(self):
        """Run Algo Agent in backtest mode using historical data and pick best performer."""
        import time
        import random
        self.log_action("Starting backtest using historical data...")
        # For demo: use NIFTY50, BANKNIFTY, FINNIFTY
        symbols = ['NIFTY50', 'BANKNIFTY', 'FINNIFTY']
        best_symbol = None
        best_return = float('-inf')
        stats = {'trades': 0, 'pnl': 0.0, 'best_symbol': '', 'best_return': 0.0}
        for symbol in symbols:
            hist = self.api_client.get_historical_data(symbol, days=30)
            if not hist['success'] or not hist['data']:
                continue
            prices = [d['close'] for d in hist['data']]
            if len(prices) < 2:
                continue
            ret = (prices[-1] - prices[0]) / prices[0] * 100
            self.log_action(f"Backtest: {symbol} return={ret:.2f}%")
            if ret > best_return:
                best_return = ret
                best_symbol = symbol
        if best_symbol:
            self.log_action(f"Best performer: {best_symbol} ({best_return:.2f}%)")
            # Simulate trades: buy at start, sell at end
            hist = self.api_client.get_historical_data(best_symbol, days=30)
            buy_price = hist['data'][0]['close']
            sell_price = hist['data'][-1]['close']
            pnl = sell_price - buy_price
            stats['trades'] = 2
            stats['pnl'] = round(pnl, 2)
            stats['best_symbol'] = best_symbol
            stats['best_return'] = round(best_return, 2)
            self.log_action(f"Backtest trade: BUY {best_symbol} at {buy_price}, SELL at {sell_price}, P&L={pnl:.2f}")
        else:
            self.log_action("No valid symbol for backtest.")
        self.last_execution = datetime.now()
        self.trade_count = stats['trades']
        self.stats = stats
        self.is_running = False
        self.status = 'STOPPED'
        self.log_action("Backtest completed.")
    
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
        """Main algorithm loop: scan watchlist, execute trade, rescan after close."""
        import time
        scanned_symbols = set()
        while self.is_running:
            try:
                # Step 1: Fetch watchlist
                self.log_action("Fetching watchlist for scan...")
                watchlist_resp = self.api_client.get_watchlist()
                if not watchlist_resp['success'] or not watchlist_resp['data']:
                    self.log_action(f"Failed to fetch watchlist: {watchlist_resp.get('error')}")
                    time.sleep(10)
                    continue
                watchlist = watchlist_resp['data']
                # Step 2: Find best performer (highest % change)
                best_stock = None
                best_change = float('-inf')
                for item in watchlist:
                    change = float(item.get('change', item.get('pchange', 0)))
                    if item.get('symbol') and change > best_change and item['symbol'] not in scanned_symbols:
                        best_stock = item
                        best_change = change
                if not best_stock:
                    self.log_action("No new rallying stock found in watchlist.")
                    time.sleep(10)
                    continue
                symbol = best_stock['symbol']
                price = best_stock.get('price', best_stock.get('ltp', 0))
                self.log_action(f"Selected for trade: {symbol} with change {best_change}% at price {price}")
                scanned_symbols.add(symbol)
                # Step 3: Execute trade (paper/live)
                trade_type = 'BUY' if best_change > 0 else 'SELL'
                strike_price = price
                self.log_action(f"Executing {self.trade_mode.upper()} trade: {trade_type} {symbol} at {strike_price}")
                if self.trade_mode == 'live':
                    order_data = {
                        'symbol': symbol,
                        'side': trade_type,
                        'quantity': 1,
                        'order_type': 'MARKET',
                        'product': 'CNC',
                    }
                    order_resp = self.api_client.place_order(order_data)
                    self.log_action(f"LIVE TRADE: {trade_type} {symbol} resp={order_resp}")
                else:
                    self.log_action(f"PAPER TRADE: {trade_type} {symbol} at {strike_price}")
                self.trade_count += 1
                # Step 4: Simulate/monitor trade close, then rescan
                self.log_action(f"Monitoring trade for {symbol}...")
                time.sleep(10)  # Simulate holding period
                # For demo, close trade after wait
                close_price = price + (price * 0.01 if trade_type == 'BUY' else -price * 0.01)
                pnl = close_price - strike_price if trade_type == 'BUY' else strike_price - close_price
                self.log_action(f"Trade closed for {symbol}. Close price: {close_price}, P&L: {pnl:.2f}")
                # Step 5: Rescan for new stock
                self.log_action("Rescanning watchlist for new opportunities...")
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error in algorithm loop: {str(e)}")
                self.log_action(f"Error: {str(e)}")
    
    def _analyze_and_trade(self, market_data: Dict[str, Any]):
        """
        Analyze market data and execute trades (paper or live)
        Args:
            market_data: Live market data from API
        """
        try:
            # Example: Custom strategy logic (user can expand this)
            if 'symbols' in market_data:
                for symbol_data in market_data['symbols']:
                    symbol = symbol_data.get('symbol')
                    change = symbol_data.get('change', 0)
                    price = symbol_data.get('price') or symbol_data.get('ltp')
                    # Log research/decision
                    self.log_action(f"Research: {symbol} change={change}, price={price}")
                    # Example rule: if price moved >1%, consider trading
                    if abs(change) > 1.0:
                        trade_type = 'BUY' if change > 0 else 'SELL'
                        self.log_action(f"Signal: {trade_type} {symbol} ({change}%)")
                        if self.trade_mode == 'live':
                            order_data = {
                                'symbol': symbol,
                                'side': trade_type,
                                'quantity': 1,
                                'order_type': 'MARKET',
                                'product': 'CNC',
                            }
                            order_resp = self.api_client.place_order(order_data)
                            self.log_action(f"LIVE TRADE: {trade_type} {symbol} resp={order_resp}")
                        else:
                            self.log_action(f"PAPER TRADE: {trade_type} {symbol} ({change}%)")
                        self.trade_count += 1
        except Exception as e:
            logger.error(f"Error in analyze_and_trade: {str(e)}")
            self.log_action(f"Error in analyze_and_trade: {str(e)}")
    
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
        stats = getattr(self, 'stats', None)
        return {
            'status': self.status,
            'is_running': self.is_running,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'trade_count': self.trade_count,
            'trade_mode': self.trade_mode,
            'logs': self.logs[-50:],  # last 50 log entries
            'stats': stats if stats else None
        }
