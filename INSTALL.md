# ROBOAi Trading Platform - Installation & Setup Guide

## Quick Start Guide

### Prerequisites
- **Python 3.10 or higher**
- **Windows OS** (primary support)
- **Internet connection**
- **mStock account** (optional for paper trading)

### Installation Steps

#### Option 1: Windows Automated Install (Recommended)

1. Download or clone the repository
2. Run `install.bat`
3. Follow the prompts
4. Launch from desktop shortcut

#### Option 2: Manual Install

```bash
# Clone repository
git clone https://github.com/birenpatel1975/BPSALGOAi.git
cd BPSALGOAi

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create configuration
copy config.example.yaml config.yaml

# Edit config.yaml with your settings

# Run the platform
python -m roboai.main
```

### Configuration

Edit `config.yaml`:

```yaml
# For Paper Trading (No API keys needed)
trading:
  mode: "paper"
  auto_trade: false

# For Live Trading (Requires API keys)
mstock:
  api_key: "your_api_key"
  api_secret: "your_api_secret"
  totp_secret: "your_totp_secret"
  client_code: "your_client_code"

trading:
  mode: "live"
  auto_trade: true  # Enable after thorough testing
```

## Testing the Installation

Run the test suite:

```bash
python test_platform.py
```

Expected output:
```
✅ PASSED - Imports
✅ PASSED - Configuration
✅ PASSED - TOTP
✅ PASSED - Database
✅ PASSED - Agents

5/5 tests passed
```

## Usage

### Starting the Platform

```bash
# Windows
venv\Scripts\activate
python -m roboai.main

# Linux/Mac
source venv/bin/activate
python -m roboai.main
```

### First Run

On first run, you'll see:
- Startup banner with warnings
- Configuration summary
- Agent initialization
- Connection status

### Monitoring

The platform provides:
- Real-time agent status every 30 seconds
- PnL updates
- Trade notifications
- Logs in `logs/roboai_YYYYMMDD.log`

### Stopping

Press `Ctrl+C` for graceful shutdown

## Paper Trading Mode

**Default mode - Safe for testing**

Features:
- Simulated trades
- Virtual portfolio
- Real market data (if configured)
- No real money at risk

Perfect for:
- Learning the platform
- Testing strategies
- Understanding workflows

## Live Trading Mode

⚠️ **Use with extreme caution**

Requirements:
1. Thorough testing in paper mode
2. Valid mStock API credentials
3. Understanding of risks
4. Small position sizes initially

To enable:
```yaml
trading:
  mode: "live"
  auto_trade: true
```

## Troubleshooting

### "Python not found"
- Install from python.org
- Check "Add to PATH" during install
- Restart terminal

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Config validation failed"
- For paper trading: Ignore API key warnings
- For live trading: Add credentials to config.yaml

### "Database locked"
- Close other instances
- Check file permissions

### Agent errors
- Check logs in `logs/` directory
- Verify internet connection
- Check API credentials (if live mode)

## Features Overview

### Implemented
✅ Multi-agent architecture
✅ mStock authentication with TOTP
✅ Auto-reconnection (60-second interval)
✅ Paper trading
✅ Order execution
✅ Position tracking
✅ PnL calculation
✅ Market scanning
✅ Sentiment analysis (basic)
✅ Strategy evaluation
✅ RCA engine
✅ Database storage
✅ Logging system
✅ Configuration management
✅ Backup system

### Planned
- Advanced technical indicators
- ML-based predictions
- Advanced charting
- Mobile UI
- Multi-broker support
- Backtesting engine

## Safety Features

- **Paper trading by default**
- **Circuit breakers** for losses
- **Position limits**
- **Daily loss limits**
- **Stop-loss management**
- **Risk validation** before trades

## Getting Help

1. Check this guide
2. Review README.md
3. Check logs/
4. Open GitHub issue
5. Contact support

## Important Reminders

⚠️ **Trading involves substantial risk**
⚠️ **Never trade with money you can't afford to lose**
⚠️ **Past performance ≠ future results**
⚠️ **Test thoroughly before live trading**
⚠️ **Start with small positions**
⚠️ **Monitor closely during market hours**

## Next Steps

1. ✅ Install and test the platform
2. ✅ Run in paper trading mode
3. ✅ Monitor performance
4. ✅ Understand all features
5. ⚠️ Consider live trading only after extensive testing

---

**Happy Trading! 🚀📈**

Remember: This is a tool to assist trading decisions, not a guarantee of profits. Always trade responsibly.
