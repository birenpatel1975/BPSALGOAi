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
        self.feed = []            # live activity feed (strings)
        self.opportunities = []   # prioritized list of opportunities
        self.ticker_text = ''
        
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
        """Main algorithm loop: scan every second, rank opportunities, trade first pick."""
        import time

        scanned_symbols = set()
        fallback_symbols = ['NIFTY50', 'NIFTYBANK', 'BANKNIFTY', 'FINNIFTY']

        def _calc_strike(val):
            try:
                return round(float(val) / 50.0) * 50
            except Exception:
                return None

        while self.is_running:
            try:
                # Pull freshest market movers/watchlist from API
                watchlist_resp = self.api_client.get_watchlist()
                symbols_payload = []
                if watchlist_resp.get('success') and watchlist_resp.get('data'):
                    symbols_payload = watchlist_resp['data']

                # If still empty, fall back to mock live data
                if not symbols_payload:
                    live_data = self.api_client.get_live_data(fallback_symbols)
                    if live_data.get('success') and 'data' in live_data and isinstance(live_data['data'], dict):
                        symbols_payload = live_data['data'].get('symbols', [])
                    else:
                        self.log_action("Live data unavailable; running backtest fallback")
                        self._run_backtest()
                        break

                # Build opportunities with a simple scoring from available fields
                opps = []
                for item in symbols_payload:
                    sym = item.get('symbol') or item.get('symbol_name') or item.get('display_name')
                    price = item.get('ltp') or item.get('price') or item.get('Price') or item.get('close') or 0
                    change = item.get('per_change') or item.get('pchange') or item.get('change') or 0
                    volume = item.get('volume') or item.get('Volume') or 0
                    strike = _calc_strike(price)
                    score = (float(change or 0) * 2) + (float(volume or 0) * 0.0001)
                    opps.append({
                        'symbol': sym,
                        'price': price,
                        'change': change,
                        'volume': volume,
                        'score': round(score, 3),
                        'strike': strike
                    })

                opps = sorted([o for o in opps if o.get('symbol')], key=lambda x: x['score'], reverse=True)
                self.opportunities = opps[:20]
                # Publish Top 10 to mStockAPI so watchlist tab can reflect current agent picks
                try:
                    self.api_client.update_algo_top10(self.opportunities)
                except Exception:
                    logger.debug("Unable to publish algo top10 to api_client", exc_info=True)

                # Update ticker and feed
                top_ticker = ', '.join([f"{o['symbol']} {o['change']}%" for o in self.opportunities[:5]])
                self.ticker_text = f"Live: {top_ticker}" if top_ticker else "Scanning..."
                self._push_feed(f"Scanned {len(symbols_payload)} symbols; top: {top_ticker or 'none'}")

                # Trade first pick if available
                if self.opportunities:
                    pick = self.opportunities[0]
                    sym = pick['symbol']
                    if sym not in scanned_symbols:
                        trade_type = 'BUY' if float(pick.get('change') or 0) >= 0 else 'SELL'
                        self._execute_trade(sym, trade_type, pick.get('price'))
                        scanned_symbols.add(sym)

                # Wait 1 second before next scan
                time.sleep(1)

            except Exception as e:
                logger.error(f"Error in algorithm loop: {str(e)}", exc_info=True)
                self.log_action(f"Error: {str(e)}")
                time.sleep(2)
    
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

    def _push_feed(self, message: str):
        """Append to live feed and keep it short."""
        ts = datetime.now().strftime('%H:%M:%S')
        entry = f"[{ts}] {message}"
        self.feed.append(entry)
        if len(self.feed) > 200:
            self.feed = self.feed[-200:]

    def _execute_trade(self, symbol: str, side: str, price: float):
        """Execute a paper/live trade and log it."""
        self._push_feed(f"Signal: {side} {symbol} @ {price}")
        self.log_action(f"Executing {self.trade_mode.upper()} trade: {side} {symbol} @ {price}")
        if self.trade_mode == 'live':
            order_data = {
                'symbol': symbol,
                'side': side,
                'quantity': 1,
                'order_type': 'MARKET',
                'product': 'CNC',
            }
            order_resp = self.api_client.place_order(order_data)
            self._push_feed(f"Live order response: {order_resp}")
        else:
            self._push_feed("Paper trade recorded")
        self.trade_count += 1

    def get_feed(self):
        """Return recent feed entries."""
        return self.feed[-100:]

    def get_opportunities(self):
        """Return current ranked opportunities."""
        return self.opportunities

    def get_ticker(self):
        """Return current ticker text."""
        return self.ticker_text or "Scanning..."
    
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
            'stats': stats if stats else None,
            'feed': self.get_feed(),
            'opportunities': self.opportunities,
            'ticker': self.get_ticker(),
            'latest_action': self.feed[-1] if self.feed else None
        }

    # --- New: Algo Agent Watchlist Info for UI ---
    def get_watchlist_info(self):
        """
        Return a list of dicts for all stocks Algo Agent is tracking, with:
        symbol, last_close, low, high, price, volume_change, change_pct, open, prev_close
        """
        watchlist_resp = self.api_client.get_watchlist()
        items = watchlist_resp.get('data') if watchlist_resp.get('success') else []

        # Fallback to mock live data if watchlist is empty
        if not items:
            symbols = ['NIFTY50', 'BANKNIFTY', 'FINNIFTY']
            live = self.api_client.get_live_data(symbols)
            if live.get('success') and 'data' in live and 'symbols' in live['data']:
                items = live['data']['symbols']

        normalized = []
        def _calc_strike(val):
            try:
                return round(float(val) / 50.0) * 50
            except Exception:
                return None

        for item in items or []:
            symbol = item.get('symbol') or item.get('symbol_name') or item.get('display_name')
            ltp = item.get('ltp') or item.get('price') or item.get('Price')
            open_ = item.get('Open') or item.get('open')
            high = item.get('High') or item.get('high')
            low = item.get('Low') or item.get('low')
            prev_close = item.get('Pclose') or item.get('close')
            change_pct = item.get('per_change') or item.get('pchange') or item.get('change')
            volume = item.get('volume') or item.get('Volume')
            normalized.append({
                'symbol': symbol,
                'last_close': prev_close or open_ or ltp,
                'low': low,
                'high': high,
                'price': ltp,
                'volume_change': volume,
                'open': open_,
                'prev_close': prev_close,
                'change_pct': change_pct,
                'strike': _calc_strike(ltp),
            })

        # Sort by change descending to emulate “top movers”
        normalized = sorted(normalized, key=lambda x: float(x.get('change_pct') or 0), reverse=True)
        return normalized

    # --- New: Mini-graph data for selected stock ---
    def get_stock_graph(self, symbol, interval):
        """
        Return mock price data for 1/5/10/15 min intervals for mini-graph.
        """
        import random, datetime
        now = datetime.datetime.now()
        data = []
        for i in range(60):
            t = now - datetime.timedelta(minutes=interval * (59 - i))
            price = 100 + random.uniform(-2, 2) * i / 10
            data.append({'time': t.strftime('%H:%M'), 'price': round(price, 2)})
        return data
