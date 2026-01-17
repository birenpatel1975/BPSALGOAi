# ROBOAi Trading Platform 🤖📈

**AI-Powered Algorithmic Trading Platform for NSE F&O Markets**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Trading Mode](https://img.shields.io/badge/mode-PAPER%20TRADING-yellow)](config.example.yaml)

## ⚠️ IMPORTANT DISCLAIMER

**PLEASE READ CAREFULLY BEFORE USING THIS PLATFORM:**

- This software is provided for **educational and research purposes only**
- Trading involves **substantial risk of loss** and is not suitable for all investors
- **Past performance is NOT indicative of future results**
- The platform starts in **PAPER TRADING mode by default** for your safety
- **Never trade with money you cannot afford to lose**
- The developers are **not responsible for any financial losses**
- Always perform thorough **testing and backtesting** before live trading
- Consult with a **qualified financial advisor** before making trading decisions

## 🌟 Features

### Multi-Agent Architecture
- **Agent Manager**: Orchestrates all specialized trading agents
- **Authentication Agent**: Handles mStock API authentication with TOTP
- **Market Scanner Agent**: Scans NSE indices and global markets
- **Sentiment Analysis Agent**: Analyzes market sentiment from multiple sources
- **Strategy Agent**: Identifies F&O trading opportunities
- **Execution Agent**: Manages order placement and position tracking
- **RCA Agent**: Post-trade analysis and strategy refinement
- **Data Agent**: Real-time data fetching with intelligent caching

### Market Coverage
**Indian Markets (NSE):**
- Nifty 50
- Bank Nifty
- Nifty Auto
- Nifty Pharma
- Nifty Metal
- Crude Oil

**Global Markets:**
- Major indices monitoring
- Sector impact analysis
- Correlation tracking

### Trading Features
- **Paper Trading**: Risk-free testing environment
- **Live Trading**: Real order execution (use with caution)
- **Auto-Trading**: Automated order placement based on signals
- **Risk Management**: Stop-loss, position limits, circuit breakers
- **PnL Tracking**: Real-time profit/loss monitoring
- **Order Management**: View, modify, cancel orders

### F&O Scanning
- Volume buildup tracking
- Strike price movement analysis
- Technical indicators (RSI, MACD, Bollinger Bands)
- Support/Resistance levels
- Open Interest analysis
- Put-Call Ratio (PCR)

### Advanced Features
- **Reconnection Management**: Auto-reconnect every 60 seconds
- **Network Optimization**: 5G preference handling
- **Sentiment Analysis**: News and social media sentiment
- **Root Cause Analysis**: Learn from past trades
- **Dynamic Prompts**: Natural language command processing

## 📋 Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows (primary), Linux/Android (future)
- **mStock Account**: For live trading (optional for paper trading)
- **Internet Connection**: Stable connection required

## 🚀 Quick Start

### Windows Installation

1. **Download the repository**:
   ```batch
   git clone https://github.com/birenpatel1975/BPSALGOAi.git
   cd BPSALGOAi
   ```

2. **Run the installer**:
   ```batch
   install.bat
   ```
   
   The installer will:
   - Check Python installation
   - Create virtual environment
   - Install dependencies
   - Create configuration file
   - Create desktop shortcut
   - Optionally create backup

3. **Configure the platform**:
   - Edit `config.yaml` and add your API credentials (optional for paper trading)
   - Review and adjust trading parameters

4. **Start the platform**:
   - Double-click "ROBOAi Trading" on your desktop, OR
   - Run: `venv\Scripts\activate && python -m roboai.main`

### Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create configuration
cp config.example.yaml config.yaml

# Edit config.yaml with your settings

# Run the platform
python -m roboai.main
```

## ⚙️ Configuration

Edit `config.yaml` to configure the platform:

### mStock API Credentials
```yaml
mstock:
  api_key: "your_api_key"
  api_secret: "your_api_secret"
  totp_secret: "your_totp_secret"
  client_code: "your_client_code"
```

### Trading Settings
```yaml
trading:
  mode: "paper"  # "paper" or "live" - ALWAYS START WITH PAPER!
  auto_trade: false  # Enable/disable auto-trading
  min_gain_target: 1000  # Minimum gain target in INR
  max_positions: 5  # Maximum concurrent positions
  stop_loss_percent: 2  # Stop loss percentage
```

### Risk Management
```yaml
risk:
  max_daily_loss: 5000  # Maximum daily loss in INR
  max_position_size: 10000  # Maximum position size in INR
  circuit_breaker_enabled: true  # Stop on excessive losses
```

## 📖 Usage

### Starting the Web Dashboard (Recommended)

The easiest way to use ROBOAi is through the web dashboard:

**Windows:**
```batch
start_dashboard.bat
```

**Linux/Mac:**
```bash
./start_dashboard.sh
```

Then open your browser to: **http://localhost:5000**

The web dashboard provides:
- 🎛️ **Easy Controls**: Toggle between paper/live mode and algo/manual trading
- 📊 **Real-time P&L**: Live profit/loss monitoring with charts
- 👁️ **Agent Status**: Monitor all 8 trading agents
- 📈 **Positions & Trades**: View active positions and trade history
- ⚙️ **Configuration**: Adjust strategy parameters on the fly

> **📝 For detailed dashboard guide**, see [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)

### Starting the Platform (Console Mode)

**Option 1: Using convenience scripts**

Windows:
```batch
start_roboai.bat
```

Linux/Mac:
```bash
./start_roboai.sh
```

**Option 2: Direct Python command**

```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

python -m roboai.main
```

You'll see the startup banner with important warnings and configuration info.

> **📝 Note:** For detailed server commands including background mode, status checks, and troubleshooting, see [SERVER_COMMANDS.md](SERVER_COMMANDS.md)

### Paper Trading Mode (Default)

Paper trading mode allows you to test strategies without risking real money:
- All trades are simulated
- Realistic order execution
- Track virtual PnL
- Learn the platform safely

### Live Trading Mode (Advanced)

⚠️ **ONLY enable after thorough testing in paper mode!**

1. Set `mode: "live"` in config.yaml
2. Ensure `auto_trade: true` for automated execution
3. Start with small position sizes
4. Monitor closely during market hours

### Monitoring

The platform provides:
- Real-time agent status
- PnL updates every 30 seconds
- Trade notifications
- Error logging to `logs/` directory

### Stopping the Platform

**Option 1: Graceful shutdown (Recommended)**
- Press `Ctrl+C` in the terminal where the platform is running

**Option 2: Using stop scripts**

Windows:
```batch
stop_roboai.bat
```

Linux/Mac:
```bash
./stop_roboai.sh
```

The platform will:
- Stop all agents gracefully
- Close database connections properly
- Save final state

> **📝 Note:** See [SERVER_COMMANDS.md](SERVER_COMMANDS.md) for advanced options like background mode and service management

## 🏗️ Project Structure

```
BPSALGOAi/
├── roboai/                    # Main package
│   ├── agents/                # Agent modules
│   │   ├── agent_manager.py   # Orchestrates all agents
│   │   ├── auth_agent.py      # Authentication
│   │   ├── data_agent.py      # Data fetching
│   │   ├── market_scanner.py  # Market scanning
│   │   ├── sentiment_agent.py # Sentiment analysis
│   │   ├── strategy_agent.py  # Strategy identification
│   │   ├── execution_agent.py # Order execution
│   │   └── rca_agent.py       # Post-trade analysis
│   ├── core/                  # Core functionality
│   │   ├── mstock_client.py   # mStock API client
│   │   ├── totp_handler.py    # TOTP authentication
│   │   ├── reconnection_manager.py  # Auto-reconnect
│   │   └── network_manager.py # Network handling
│   ├── utils/                 # Utilities
│   │   ├── config_manager.py  # Configuration
│   │   ├── logger.py          # Logging
│   │   ├── database.py        # SQLite database
│   │   └── backup.py          # Backup management
│   └── main.py                # Entry point
├── data/                      # Database storage
├── logs/                      # Log files
├── backups/                   # Backups
├── config.yaml               # Configuration (create from example)
├── config.example.yaml       # Configuration template
├── requirements.txt          # Dependencies
├── setup.py                  # Package setup
├── install.bat              # Windows installer
└── README.md                # This file
```

## 🔧 Development

### Adding New Strategies

Strategies are evaluated in `strategy_agent.py`. To add new strategies:

1. Create strategy logic in `evaluate_opportunity()`
2. Add technical indicators as needed
3. Test thoroughly in paper mode
4. Monitor performance via RCA

### Extending Agents

All agents inherit from `BaseAgent`:

```python
from roboai.agents.base_agent import BaseAgent

class MyCustomAgent(BaseAgent):
    async def initialize(self) -> bool:
        # Initialization logic
        return True
    
    async def run(self) -> None:
        # Main agent loop
        while self.is_running:
            # Your logic here
            await asyncio.sleep(10)
    
    async def stop(self) -> None:
        # Cleanup logic
        pass
```

## 📊 Database

The platform uses SQLite to store:
- Trade history
- Order records
- Market data snapshots
- Sentiment analysis results
- RCA logs
- Configuration history

Database location: `data/roboai.db`

## 🔒 Security

- API credentials stored in config.yaml (add to .gitignore)
- TOTP tokens generated dynamically
- No credentials in logs
- Encrypted database (future enhancement)

## 🐛 Troubleshooting

### "Python not found"
- Install Python 3.10+ from python.org
- Ensure "Add Python to PATH" is checked during installation

### "Failed to authenticate"
- Verify API credentials in config.yaml
- Check TOTP secret is correct
- Ensure internet connectivity

### "Import errors"
- Activate virtual environment
- Run: `pip install -r requirements.txt`

### "Database locked"
- Close other instances of the platform
- Check file permissions on data/ directory

## 📝 Logging

Logs are stored in the `logs/` directory:
- Format: `roboai_YYYYMMDD.log`
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Console output: INFO and above
- File output: All levels

## 🔄 Backup & Restore

### Create Backup
```python
from roboai.utils import create_backup
backup_path = create_backup()
```

### Restore Backup
```python
from roboai.utils import restore_backup
restore_backup("backups/roboai_backup_20240117_120000.zip")
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Test thoroughly
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- mStock for API access
- Python community for excellent libraries
- All contributors and testers

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Email: birenpatel1975@example.com

## 🗺️ Roadmap

### Current Version (1.0.0)
- ✅ Multi-agent architecture
- ✅ Paper trading
- ✅ Basic market scanning
- ✅ Order execution
- ✅ RCA engine

### Future Enhancements
- [ ] Android mobile app
- [ ] Advanced ML models
- [ ] Backtesting engine
- [ ] Social trading features
- [ ] Multi-broker support
- [ ] Advanced charting
- [ ] Portfolio optimization
- [ ] News integration
- [ ] Webhook notifications

---

**Remember: Trade responsibly. Only risk capital you can afford to lose. This platform is a tool, not a guarantee of profits.**

**Happy Trading! 🚀📈**
