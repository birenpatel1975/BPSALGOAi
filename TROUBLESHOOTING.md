# ROBOAi Trading Platform - Troubleshooting Guide

## Quick Diagnostics

Run these commands to quickly diagnose issues:

```bash
# Test platform installation
python test_platform.py

# Check Python version
python --version  # Should be 3.10+

# Verify dependencies
pip list | grep -E "(pandas|numpy|aiohttp|flask)"

# Check configuration
python -c "from roboai.utils import get_config; c = get_config(); print(c.get('trading.mode'))"
```

## Common Issues

### 1. Installation Issues

#### Python Not Found

**Symptoms**:
```
'python' is not recognized as an internal or external command
```

**Solutions**:
1. Install Python 3.10+ from [python.org](https://python.org)
2. During installation, check "Add Python to PATH"
3. Restart terminal/command prompt
4. Verify: `python --version`

#### Virtual Environment Issues

**Symptoms**:
```
No module named 'venv'
```

**Solutions**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-venv

# Recreate virtual environment
python -m venv venv --clear

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### Dependency Installation Failures

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions**:
```bash
# Update pip
python -m pip install --upgrade pip

# Install with verbose output
pip install -r requirements.txt -v

# Install problematic package separately
pip install pandas==2.1.0

# On Windows, ta-lib may need binary
# Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib-0.4.28-cp310-cp310-win_amd64.whl
```

### 2. Import Errors

#### Module Not Found

**Symptoms**:
```
ModuleNotFoundError: No module named 'roboai'
```

**Solutions**:
1. Ensure virtual environment is activated:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. Verify you're in the correct directory:
   ```bash
   cd /path/to/BPSALGOAi
   python -m roboai.main
   ```

3. Reinstall:
   ```bash
   pip install -e .
   ```

#### Circular Import Errors

**Symptoms**:
```
ImportError: cannot import name 'X' from partially initialized module
```

**Solutions**:
1. Clear Python cache:
   ```bash
   find . -type d -name "__pycache__" -exec rm -r {} +
   find . -type f -name "*.pyc" -delete
   ```

2. Restart Python interpreter

### 3. Configuration Issues

#### Config File Not Found

**Symptoms**:
```
FileNotFoundError: config.yaml not found
```

**Solutions**:
```bash
# Create from example
cp config.example.yaml config.yaml

# Or on Windows
copy config.example.yaml config.yaml

# Verify location
ls -la config.yaml
```

#### Invalid Configuration

**Symptoms**:
```
Configuration validation failed
```

**Solutions**:
1. Check YAML syntax:
   ```python
   import yaml
   with open('config.yaml') as f:
       config = yaml.safe_load(f)
       print(config)
   ```

2. Common YAML mistakes:
   - Incorrect indentation (use 2 spaces)
   - Missing colons
   - Unquoted special characters
   
3. Reset to defaults:
   ```bash
   cp config.example.yaml config.yaml
   # Then edit with your values
   ```

### 4. Authentication Issues

#### TOTP Generation Failed

**Symptoms**:
```
Failed to generate TOTP token
```

**Solutions**:
1. Verify TOTP secret format:
   ```python
   from roboai.core import TOTPHandler
   totp = TOTPHandler("YOUR_SECRET_HERE")
   print(totp.generate_token())
   ```

2. TOTP secret should be:
   - Base32 encoded string
   - Usually 16-32 characters
   - No spaces or special characters

3. Extract from QR code:
   - Use QR code reader app
   - Look for `secret=` parameter in URL
   - Copy the value after `secret=`

#### Authentication Failed

**Symptoms**:
```
Failed to authenticate with mStock API
```

**Solutions**:
1. Verify credentials:
   ```yaml
   mstock:
     api_key: "your_key"      # Check for typos
     api_secret: "your_secret"
     totp_secret: "your_totp"
     client_code: "your_code"
   ```

2. Test API connectivity:
   ```python
   import requests
   response = requests.get("https://mstockapi.com/health")
   print(response.status_code)
   ```

3. Check API permissions in mStock account

4. Verify TOTP is synchronized:
   - Time on computer should be accurate
   - Use NTP time synchronization

### 5. Runtime Issues

#### Agents Not Starting

**Symptoms**:
```
Failed to initialize agents
```

**Solutions**:
1. Check logs:
   ```bash
   tail -f logs/roboai_*.log
   ```

2. Test agents individually:
   ```python
   from roboai.agents import AuthAgent
   agent = AuthAgent()
   await agent.initialize()
   ```

3. Verify database:
   ```python
   from roboai.utils import get_database
   db = get_database()
   # Check if database is accessible
   ```

#### High Memory Usage

**Symptoms**:
- Platform using > 2GB RAM
- System becoming slow

**Solutions**:
1. Reduce scan frequency:
   ```yaml
   scanning:
     scan_interval: 180  # Increase from 60
   ```

2. Limit monitored indices:
   ```yaml
   markets:
     indices:
       - NIFTY50  # Only essential indices
   ```

3. Reduce data retention:
   ```python
   # Clean old data
   from roboai.utils import get_database
   db = get_database()
   await db.cleanup_old_data(days=30)
   ```

#### High CPU Usage

**Symptoms**:
- CPU usage > 80%
- Platform slowing down

**Solutions**:
1. Reduce agent activity:
   ```yaml
   sentiment:
     update_interval: 600  # Increase from 300
   ```

2. Disable non-essential agents:
   ```yaml
   sentiment:
     enabled: false
   ```

3. Use lightweight mode:
   ```python
   # Reduce technical indicator calculations
   ```

### 6. Trading Issues

#### No Trades Being Executed

**Symptoms**:
- Platform running
- No orders placed

**Checklist**:
1. [ ] Auto-trade enabled?
   ```yaml
   trading:
     auto_trade: true
   ```

2. [ ] Market hours?
   - NSE: 9:15 AM - 3:30 PM IST
   - Check if market is open

3. [ ] Funds available?
   - Check mStock account balance
   - Verify margin requirements

4. [ ] Position limit reached?
   ```yaml
   trading:
     max_positions: 5  # Check current positions
   ```

5. [ ] Circuit breaker active?
   - Check logs for circuit breaker activation
   - Review daily P&L

6. [ ] Strategy filters too strict?
   ```yaml
   # Try relaxing filters
   technical:
     rsi_overbought: 75  # From 70
     rsi_oversold: 25    # From 30
   ```

#### Orders Getting Rejected

**Symptoms**:
```
Order rejected: Insufficient funds / Invalid symbol / etc.
```

**Solutions by rejection reason**:

1. **Insufficient funds**:
   - Check account balance
   - Reduce position size
   - Add funds to account

2. **Invalid symbol**:
   ```python
   # Verify symbol format
   # Correct: "NIFTY 18000 CE"
   # Wrong: "NIFTY18000CE"
   ```

3. **Order outside market hours**:
   - Check if market is open
   - Use appropriate order types

4. **Risk management rejection**:
   - Check broker RMS settings
   - Verify margin requirements
   - Reduce order quantity

#### Stop Loss Not Triggering

**Symptoms**:
- Loss exceeded stop loss
- Position not closed

**Solutions**:
1. Check if stop loss was placed:
   ```python
   from roboai.utils import get_database
   db = get_database()
   # Query orders table for SL orders
   ```

2. Verify stop loss calculation:
   ```python
   entry_price = 100
   sl_percent = 2
   stop_loss = entry_price * (1 - sl_percent/100)
   print(f"Stop loss: {stop_loss}")  # Should be 98
   ```

3. Check broker confirmation:
   - Login to mStock
   - Verify SL order in order book

### 7. Database Issues

#### Database Locked

**Symptoms**:
```
sqlite3.OperationalError: database is locked
```

**Solutions**:
1. Close other instances:
   ```bash
   # Windows
   tasklist | findstr python
   taskkill /F /PID <pid>
   
   # Linux
   ps aux | grep python
   kill <pid>
   ```

2. Check file permissions:
   ```bash
   ls -la data/roboai.db
   chmod 644 data/roboai.db
   ```

3. Backup and recreate:
   ```bash
   cp data/roboai.db data/roboai.db.bak
   rm data/roboai.db
   # Restart platform (will recreate)
   ```

#### Database Corruption

**Symptoms**:
```
sqlite3.DatabaseError: database disk image is malformed
```

**Solutions**:
1. Try recovery:
   ```bash
   sqlite3 data/roboai.db "PRAGMA integrity_check;"
   ```

2. Export and reimport:
   ```bash
   sqlite3 data/roboai.db .dump > backup.sql
   rm data/roboai.db
   sqlite3 data/roboai.db < backup.sql
   ```

3. Use backup:
   ```bash
   cp backups/roboai_backup_*.zip ./
   unzip roboai_backup_*.zip
   ```

### 8. Network Issues

#### Connection Timeout

**Symptoms**:
```
requests.exceptions.ConnectionError: Connection timeout
```

**Solutions**:
1. Check internet connection:
   ```bash
   ping 8.8.8.8
   curl -I https://google.com
   ```

2. Verify API endpoints:
   ```python
   import requests
   response = requests.get("https://mstockapi.com")
   print(response.status_code)
   ```

3. Check firewall:
   - Allow Python through firewall
   - Check antivirus settings

4. Use proxy if needed:
   ```yaml
   network:
     proxy: "http://proxy:port"
   ```

#### WebSocket Connection Failed

**Symptoms**:
```
websockets.exceptions.ConnectionClosedError
```

**Solutions**:
1. Check WebSocket support:
   ```python
   import websockets
   import asyncio
   
   async def test():
       async with websockets.connect('ws://echo.websocket.org/') as ws:
           await ws.send('test')
           response = await ws.recv()
           print(response)
   
   asyncio.run(test())
   ```

2. Enable auto-reconnect:
   ```yaml
   network:
     reconnect_interval: 60
     max_retries: 5
   ```

### 9. Performance Issues

#### Slow Startup

**Symptoms**:
- Takes > 60 seconds to start

**Solutions**:
1. Reduce initialization load:
   ```yaml
   # Disable non-essential features on startup
   sentiment:
     enabled: false
   ```

2. Clear cache:
   ```bash
   rm -rf __pycache__
   rm -rf roboai/__pycache__
   ```

3. Check disk I/O:
   - Ensure database is on fast drive
   - Close other disk-intensive applications

#### Slow Trade Execution

**Symptoms**:
- Orders take > 5 seconds to place

**Solutions**:
1. Optimize data fetching:
   ```yaml
   data:
     cache_enabled: true
     cache_ttl: 30
   ```

2. Reduce indicator calculations:
   ```python
   # Calculate only essential indicators
   ```

3. Use limit orders instead of market orders

### 10. Notification Issues

#### No Notifications Appearing

**Symptoms**:
- Platform running
- No desktop notifications

**Solutions**:

**Windows**:
```bash
# Install win10toast
pip install win10toast

# Test notifications
python -c "from win10toast import ToastNotifier; ToastNotifier().show_toast('Test', 'Working')"
```

**Linux**:
```bash
# Install notify-send
sudo apt-get install libnotify-bin

# Test
notify-send "Test" "Working"
```

**Platform Settings**:
```yaml
alerts:
  enabled: true
  notification_enabled: true
```

## Diagnostic Tools

### Test Suite

Run comprehensive tests:
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

### Log Analysis

```bash
# View all errors
grep ERROR logs/roboai_*.log

# View warnings
grep WARNING logs/roboai_*.log

# View today's activity
tail -f logs/roboai_$(date +%Y%m%d).log

# Search for specific error
grep "authentication" logs/roboai_*.log
```

### Database Inspection

```bash
# Open database
sqlite3 data/roboai.db

# List tables
.tables

# View recent trades
SELECT * FROM trades ORDER BY created_at DESC LIMIT 10;

# Check trade statistics
SELECT 
    COUNT(*) as total_trades,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl
FROM trades;
```

### Network Diagnostics

```python
# Test API connectivity
from roboai.core import MStockClient
client = MStockClient()
status = client.check_connection()
print(f"Connection: {status}")
```

## Getting Help

If issues persist:

1. **Check Documentation**:
   - README.md
   - USER_MANUAL.md
   - INSTALL.md

2. **Review Logs**:
   - `logs/roboai_YYYYMMDD.log`
   - Look for ERROR and WARNING messages

3. **Run Diagnostics**:
   ```bash
   python test_platform.py
   ```

4. **GitHub Issues**:
   - Search existing issues
   - Create new issue with:
     - Platform version
     - Python version
     - Operating system
     - Error logs
     - Steps to reproduce

5. **Community Support**:
   - GitHub Discussions
   - Email: birenpatel1975@example.com

## Emergency Procedures

### Stop All Trading Immediately

```bash
# Windows
stop_roboai.bat

# Linux/Mac
./stop_roboai.sh

# Or press Ctrl+C in terminal
```

### Close All Positions

```python
from roboai.api import close_all_positions
close_all_positions(reason="emergency")
```

### Disable Auto-Trading

```yaml
trading:
  auto_trade: false
```

### Reset to Defaults

```bash
# Backup current config
cp config.yaml config.yaml.bak

# Reset to defaults
cp config.example.yaml config.yaml

# Edit with minimal settings
```

---

**Remember**: When in doubt, use paper trading mode first!
