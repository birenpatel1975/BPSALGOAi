# ROBOAi Web Dashboard - User Guide

## Overview

The ROBOAi Web Dashboard provides a modern, user-friendly interface to monitor and control your algorithmic trading platform. Access it through any web browser for real-time insights and control.

## Starting the Dashboard

### Quick Start

**Windows:**
```batch
start_dashboard.bat
```

**Linux/Mac:**
```bash
./start_dashboard.sh
```

**Direct Python:**
```bash
python start_dashboard.py
```

The dashboard will be available at: **http://localhost:5000**

## Features

### 1. Control Panel

#### Platform Control
- **Start Platform**: Launches the trading engine with all agents
- **Stop Platform**: Gracefully shuts down all trading operations

#### Trading Mode Toggle
- **Paper Trading** (Default): Safe testing environment, no real money at risk
- **Live Trading**: Real order execution with actual funds (⚠️ Use with caution!)

#### Strategy Mode Toggle
- **Algo AI**: Fully automated trading using AI-powered strategies
- **Manual**: You control all trading decisions

### 2. Profit & Loss Monitor

Real-time P&L tracking with four key metrics:
- **Daily P&L**: Today's profit/loss
- **Total P&L**: Overall profit/loss
- **Realized P&L**: Closed position profits/losses
- **Unrealized P&L**: Open position profits/losses

Includes a live chart showing P&L trends over time.

### 3. Agent Status

Monitor the health of all 8 trading agents:
- AgentManager
- AuthAgent  
- DataAgent
- MarketScannerAgent
- SentimentAgent
- StrategyAgent
- ExecutionAgent
- RCAAgent

Each agent shows its current status (running/stopped) with visual indicators.

### 4. Active Positions

View all open trading positions with:
- Symbol name
- Quantity held
- Average entry price
- Current market price
- Unrealized P&L
- Position status

### 5. Recent Trades

Historical view of completed trades showing:
- Entry and exit times
- Symbol and side (BUY/SELL)
- Entry and exit prices
- Realized P&L
- Trade status

### 6. Strategy Configuration

Configure advanced trading parameters:

#### Profit Locking (High-Precision Strategy)
- **Profit Lock Threshold**: ₹500 (default) - Activates "Safety Mode"
- **Trailing Stop Loss**: 20% (default) - Dynamic risk management

When profit reaches the threshold (₹500), the system:
1. Activates Safety Mode
2. Calculates a trailing stop loss at 20% of current profit
3. As profit grows (e.g., ₹500 → ₹2,000), the stop loss trails up
4. Never loses more than 20% of the day's peak gain

#### Position Management
- **Min Gain Target**: Minimum profit per trade (₹1000 default)
- **Max Positions**: Maximum concurrent open positions (5 default)

## High-Precision Trading Strategies

The platform implements multiple professional algo strategies:

### 1. VWAP Pullback
- Entry when price returns to VWAP in a strong trend
- Best for: High-precision trending days
- Indicators: VWAP + Volume confirmation

### 2. EMA Cloud Scalp
- Fast EMA (5/8) crosses Slow EMA (21) with volume
- Best for: Capturing micro-momentum
- Indicators: 5, 8, 13, 21 EMAs

### 3. Opening Range Breakout (ORB)
- Breakout of first 15-minute candle range
- Best for: Early morning volatility
- Confirmation: 1-minute candle close

### 4. CE/PE Entry Logic

**For Call Options (CE)**:
- Price > VWAP
- 9 EMA > 21 EMA  
- RSI (9-period) > 60

**For Put Options (PE)**:
- Price < VWAP
- 9 EMA < 21 EMA
- RSI (9-period) < 40

**Strike Selection**: Weekly ATM (At-the-money) for maximum liquidity

## Real-Time Updates

The dashboard uses WebSocket technology for live updates:
- Status refreshes every 5 seconds
- P&L updates in real-time
- Agent health monitoring
- Instant configuration changes

## Safety Features

### Built-in Protections
1. **Paper Trading Default**: Always starts in safe mode
2. **Mode Confirmation**: Visual warnings when switching to live trading
3. **Circuit Breaker**: Auto-stops on excessive losses
4. **Position Limits**: Prevents over-exposure
5. **Trailing Stop Loss**: Protects profits dynamically

### Warning Indicators
- 🟢 Green: Safe/Paper trading
- 🔴 Red: Live trading with real money
- ⚠️ Yellow: Caution/limits approaching

## Troubleshooting

### Dashboard won't start
1. Ensure virtual environment is activated
2. Check if port 5000 is available
3. Install required dependencies: `pip install flask flask-cors flask-socketio`

### Can't connect to dashboard
1. Check the server is running
2. Try http://127.0.0.1:5000 instead of localhost
3. Check firewall settings

### Data not updating
1. Verify WebSocket connection (green indicator in header)
2. Check platform is running (Start Platform button)
3. Refresh the browser page

### Configuration not saving
1. Ensure you have write permissions to config.yaml
2. Check platform is not running (stop it first)
3. Review browser console for errors (F12)

## Advanced Usage

### Running on Different Port
```bash
export FLASK_RUN_PORT=8080
python start_dashboard.py
```

### Accessing from Another Device
The dashboard binds to 0.0.0.0, making it accessible on your local network:
```
http://YOUR_IP_ADDRESS:5000
```

Find your IP:
- Windows: `ipconfig`
- Linux/Mac: `ifconfig` or `ip addr`

### Background Mode
Run the dashboard in the background (Linux/Mac):
```bash
nohup python start_dashboard.py > dashboard.log 2>&1 &
```

## Best Practices

1. **Always Test in Paper Mode First**
   - Run strategies for at least 2 weeks in paper mode
   - Analyze results before considering live trading

2. **Monitor Regularly**
   - Keep the dashboard open during trading hours
   - Check agent status frequently
   - Review P&L trends

3. **Set Conservative Limits**
   - Start with lower position sizes
   - Use tight stop losses (20% or less)
   - Limit max positions to 3-5 initially

4. **Review Strategy Performance**
   - Check Recent Trades daily
   - Analyze win/loss ratio
   - Adjust parameters based on results

5. **Risk Management**
   - Never risk more than 2% per trade
   - Keep daily loss limits reasonable
   - Use the circuit breaker feature

## Keyboard Shortcuts

- `Ctrl+R`: Refresh dashboard
- `F5`: Reload page
- `F12`: Open browser developer tools (for debugging)

## Integration with Console Mode

The web dashboard and console mode (`python -m roboai.main`) can run simultaneously:
- Console: For logs and detailed debugging
- Dashboard: For visual monitoring and control

## Security Notes

- Dashboard runs on localhost by default (secure)
- No authentication required for local access
- For remote access, use SSH tunneling or VPN
- Never expose dashboard directly to the internet

## Support

For issues or questions:
1. Check logs in `logs/roboai_*.log`
2. Review browser console (F12)
3. See README.md for general troubleshooting
4. Open GitHub issue with details

---

**Remember**: Always start in Paper Trading mode and test thoroughly before enabling live trading!
