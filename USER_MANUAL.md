# ROBOAi Trading Platform - User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Configuration Guide](#configuration-guide)
4. [Using the Platform](#using-the-platform)
5. [Trading Modes](#trading-modes)
6. [Dynamic Commands](#dynamic-commands)
7. [Risk Management](#risk-management)
8. [Monitoring & Alerts](#monitoring--alerts)
9. [Troubleshooting](#troubleshooting)

## Introduction

ROBOAi is an AI-powered algorithmic trading platform designed for NSE F&O markets. It uses a multi-agent architecture to automate trading decisions, execute orders, and analyze performance.

### Key Features
- **Multi-Agent System**: 8 specialized agents working together
- **Paper Trading**: Risk-free testing environment
- **Live Trading**: Real order execution with mStock integration
- **Dynamic Commands**: Real-time strategy adjustments
- **Risk Management**: Built-in safeguards and circuit breakers
- **Technical Analysis**: RSI, MACD, Bollinger Bands, and more
- **Multiple Strategies**: Breakout, Mean Reversion, Options strategies

## Getting Started

### Installation

#### Windows
1. Download and install Python 3.10 or higher from [python.org](https://python.org)
2. Clone the repository:
   ```batch
   git clone https://github.com/birenpatel1975/BPSALGOAi.git
   cd BPSALGOAi
   ```
3. Run the installer:
   ```batch
   install.bat
   ```
4. The installer will:
   - Check Python version
   - Create virtual environment
   - Install dependencies
   - Create configuration file
   - Offer to create desktop shortcuts

#### Linux/Mac
```bash
git clone https://github.com/birenpatel1975/BPSALGOAi.git
cd BPSALGOAi
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp config.example.yaml config.yaml
```

### First Run

1. **Start the platform**:
   - Double-click "ROBOAi Trading" desktop shortcut, OR
   - Run: `python -m roboai.main`

2. **What you'll see**:
   ```
   ╔══════════════════════════════════════════════════════════════╗
   ║              ROBOAi Trading Platform v1.0.0                  ║
   ║         AI-Powered Algorithmic Trading for NSE F&O           ║
   ║                   ⚠️  IMPORTANT NOTICE ⚠️                     ║
   ║  • This platform is currently in PAPER TRADING mode          ║
   ╚══════════════════════════════════════════════════════════════╝
   ```

3. **Agent initialization**: All 8 agents will start:
   - AuthAgent
   - DataAgent
   - MarketScannerAgent
   - SentimentAgent
   - StrategyAgent
   - ExecutionAgent
   - RCAAgent
   - PromptAgent

## Configuration Guide

Edit `config.yaml` to customize your setup:

### Trading Configuration

```yaml
trading:
  mode: "paper"              # "paper" or "live"
  auto_trade: false          # Enable/disable auto-trading
  min_gain_target: 1000      # Minimum profit target (₹)
  max_positions: 5           # Maximum concurrent positions
  stop_loss_percent: 2       # Stop loss percentage
  target_profit_percent: 5   # Target profit percentage
```

**Important**: Always start with `mode: "paper"` and `auto_trade: false`!

### mStock API Configuration

For live trading, add your mStock credentials:

```yaml
mstock:
  api_key: "your_api_key"
  api_secret: "your_api_secret"
  totp_secret: "your_totp_secret"
  client_code: "your_client_code"
```

**How to get TOTP secret**:
1. In mStock app, go to Settings → Two-Factor Authentication
2. Click "Show QR Code"
3. Extract the secret key from the QR code URL

### Risk Management

```yaml
risk:
  max_daily_loss: 5000           # Maximum daily loss (₹)
  max_position_size: 10000       # Maximum position size (₹)
  circuit_breaker_enabled: true  # Emergency stop
```

### Market Configuration

```yaml
markets:
  nse_enabled: true
  global_enabled: true
  indices:
    - NIFTY50
    - BANKNIFTY
    - NIFTYAUTO
    - NIFTYPHARMA
    - NIFTYMETAL
    - CRUDEOIL
```

### Technical Indicators

```yaml
technical:
  rsi_period: 14
  rsi_overbought: 70
  rsi_oversold: 30
  macd_fast: 12
  macd_slow: 26
  macd_signal: 9
  bb_period: 20
  bb_std: 2
```

## Using the Platform

### Web Dashboard (Recommended)

1. **Start the dashboard**:
   ```batch
   start_dashboard.bat
   ```
   Or double-click "📊 ROBOAi - Dashboard" shortcut

2. **Open in browser**:
   - Navigate to http://localhost:5000
   - Or double-click "🌐 ROBOAi - Open Dashboard" shortcut

3. **Dashboard features**:
   - Real-time P&L tracking
   - Agent status monitoring
   - Position management
   - Order history
   - Configuration controls
   - Dynamic command interface

### Console Mode

Run the platform in console mode for lightweight operation:

```batch
start_roboai.bat
```

You'll see real-time updates:
```
16:30:00 - MarketScannerAgent - INFO - Scanning NIFTY50...
16:30:05 - StrategyAgent - INFO - Found opportunity: NIFTY 18000 CE
16:30:10 - ExecutionAgent - INFO - Order placed: BUY NIFTY 18000 CE
```

## Trading Modes

### Paper Trading (Safe)

**Purpose**: Test strategies without risking real money

**Configuration**:
```yaml
trading:
  mode: "paper"
  auto_trade: true  # Can be enabled safely
```

**What happens**:
- All trades are simulated
- Virtual portfolio management
- Real market data used
- Same risk management rules apply
- Perfect for learning

**When to use**:
- Learning the platform
- Testing new strategies
- Backtesting ideas
- Building confidence

### Live Trading (Advanced)

**Purpose**: Execute real trades with real money

**Configuration**:
```yaml
trading:
  mode: "live"
  auto_trade: true
mstock:
  api_key: "your_key"
  # ... other credentials
```

**Before enabling**:
- [ ] Tested in paper mode for at least 2 weeks
- [ ] Understand all features
- [ ] Set conservative risk limits
- [ ] Added mStock credentials
- [ ] Verified TOTP works
- [ ] Prepared to monitor actively
- [ ] Start with small position sizes

**Safety features**:
- Circuit breaker on excessive losses
- Daily loss limits
- Position size limits
- Automatic stop losses
- Real-time alerts

## Dynamic Commands

The Prompt Agent allows real-time strategy adjustments via natural language commands.

### How to Use

**Web Dashboard**:
1. Go to "Commands" section
2. Type your command
3. System analyzes and shows preview
4. Click "Apply" or "Ignore"

**Console Mode**:
Commands are processed from the database. Use the web dashboard to inject commands.

### Supported Commands

#### Position Size Adjustment
```
"Increase position size by 20%"
"Decrease position size by 15%"
```

#### Add Filters
```
"Add RSI > 70 filter"
"Add MACD < 0 filter for all trades"
```

#### Sector Exclusion
```
"Avoid banking stocks today"
"Avoid pharma sector"
```

#### Risk Parameters
```
"Set max daily loss to 3000"
"Set min gain target to 1500"
"Change stop loss percent to 1.5"
```

#### Feature Toggle
```
"Enable auto_trade"
"Disable sentiment analysis"
"Enable alerts"
```

### Command Examples

**Example 1**: Increase risk during trending market
```
Command: "Increase position size by 25%"
Impact: Position size changes from ₹10,000 to ₹12,500
Risk: Higher potential profit AND loss
```

**Example 2**: Add momentum filter
```
Command: "Add RSI > 60 filter"
Impact: Only trades with RSI above 60 will be taken
Risk: Fewer trade opportunities, but better quality
```

**Example 3**: Emergency risk reduction
```
Command: "Set max daily loss to 2000"
Impact: Trading stops if daily loss reaches ₹2,000
Risk: Protection against large losses
```

## Risk Management

### Circuit Breaker

Automatically stops trading when:
- Daily loss limit reached
- 3 consecutive losing trades
- Connection issues persist
- Abnormal market conditions detected

**Recovery**:
1. Review what went wrong
2. Adjust parameters
3. Manually restart trading
4. Monitor closely

### Position Limits

```yaml
risk:
  max_positions: 5           # Maximum concurrent trades
  max_position_size: 10000   # Maximum per position
```

**Why it matters**:
- Prevents over-leverage
- Ensures diversification
- Limits total exposure

### Stop Loss

Every position has automatic stop loss:
```yaml
trading:
  stop_loss_percent: 2  # Exit if loss > 2%
```

**Example**:
- Buy NIFTY 18000 CE at ₹100
- Stop loss: ₹98 (2% below)
- Maximum loss: ₹2 per lot

### Trailing Stop Loss

```yaml
strategy:
  profit_lock_threshold: 500   # Activate at ₹500 profit
  trailing_sl_percent: 20      # Trail by 20% of peak
```

**How it works**:
1. Position reaches ₹500 profit → Safety mode activated
2. Profit grows to ₹1000
3. Stop loss trails at ₹800 (20% below peak)
4. If price drops to ₹800, position closes
5. Minimum locked profit: ₹300

## Monitoring & Alerts

### Desktop Notifications

**Windows**: Toast notifications (requires win10toast)
**Linux**: notify-send
**macOS**: osascript

**Types of alerts**:
- Trade signals
- Order fills
- Stop loss hits
- Target reached
- Daily P&L summary
- Circuit breaker activation
- Errors

**Enable/Disable**:
```yaml
alerts:
  enabled: true
  notification_enabled: true
```

### Logs

All activity logged to `logs/roboai_YYYYMMDD.log`

**Log levels**:
- DEBUG: Detailed information
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Errors occurred
- CRITICAL: Serious problems

**Viewing logs**:
```bash
# Latest log
tail -f logs/roboai_*.log

# Search for errors
grep ERROR logs/roboai_*.log
```

### P&L Tracking

**Real-time**: Updated every 30 seconds
**Daily summary**: At market close
**Database**: All trades stored in `data/roboai.db`

## Troubleshooting

### Platform Won't Start

**Problem**: "Python not found"
**Solution**: 
1. Install Python 3.10+
2. Check "Add Python to PATH" during installation
3. Restart terminal

**Problem**: "Import errors"
**Solution**:
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Reinstall dependencies
pip install -r requirements.txt
```

### Authentication Issues

**Problem**: "Failed to authenticate"
**Solution**:
1. Verify API credentials in config.yaml
2. Check TOTP secret is correct
3. Test TOTP manually:
   ```python
   from roboai.core import TOTPHandler
   totp = TOTPHandler("YOUR_SECRET")
   print(totp.generate_token())
   ```

### No Trades Executing

**Problem**: Platform running but no trades
**Possible causes**:
1. `auto_trade: false` in config
2. No opportunities meeting criteria
3. Position limit reached
4. Daily loss limit hit
5. Market closed

**Solutions**:
1. Check config: `trading.auto_trade: true`
2. Review strategy parameters (may be too strict)
3. Check logs for reasons
4. Verify market hours

### Orders Rejected

**Problem**: Orders placed but rejected by broker
**Possible causes**:
1. Insufficient funds
2. Invalid strike/symbol
3. Market orders outside hours
4. Risk management limits

**Solutions**:
1. Check account balance
2. Verify symbol format
3. Use limit orders
4. Review broker risk settings

### High CPU/Memory Usage

**Problem**: Platform using too much resources
**Solutions**:
1. Increase scan interval:
   ```yaml
   scanning:
     scan_interval: 120  # From 60 to 120 seconds
   ```
2. Reduce concurrent agents
3. Limit indices:
   ```yaml
   markets:
     indices:
       - NIFTY50  # Only one index
   ```

### Database Locked

**Problem**: "Database is locked"
**Solutions**:
1. Close other instances
2. Check file permissions
3. Restart platform
4. If persists, backup and recreate database

## Advanced Topics

### Custom Strategies

Edit `roboai/strategies/` to add your own:

```python
from roboai.strategies.breakout import BreakoutStrategy

class MyStrategy:
    def analyze(self, data):
        # Your logic here
        return signal
```

### Backtesting

```python
# Coming in v1.1
from roboai.backtest import Backtester

backtester = Backtester()
results = backtester.run(strategy, start_date, end_date)
```

### API Access

```python
# Access platform programmatically
from roboai.api import get_positions, place_order

positions = get_positions()
order_id = place_order(symbol="NIFTY 18000 CE", qty=50)
```

## Best Practices

1. **Start Small**: Begin with minimum position sizes
2. **Test First**: Use paper trading for at least 2 weeks
3. **Monitor Daily**: Check platform during market hours
4. **Review Logs**: Read logs daily to understand behavior
5. **Adjust Gradually**: Make small parameter changes
6. **Keep Records**: Note what works and what doesn't
7. **Stay Updated**: Check for platform updates regularly
8. **Risk Management**: Never risk more than 2% per trade
9. **Diversify**: Don't put all capital in one trade
10. **Learn Continuously**: Understand each strategy

## Support

- **Documentation**: README.md, INSTALL.md
- **Logs**: Check `logs/` directory
- **Test Suite**: Run `python test_platform.py`
- **GitHub Issues**: Report bugs and request features
- **Email**: birenpatel1975@example.com

## Disclaimer

Trading involves substantial risk of loss. This software is provided for educational purposes. Past performance is not indicative of future results. The developers are not responsible for any financial losses. Always consult with a qualified financial advisor.

---

**Happy Trading! 🚀📈**
