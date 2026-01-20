# ROBOAi Trading Platform - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the ROBOAi Trading Platform on your system. The deployment script automatically checks all prerequisites and sets up the platform for you.

## Quick Deployment

### For Linux/Mac Users (Recommended)

Simply run the automated deployment script:

```bash
./deploy.sh
```

This single command will:
- ✅ Check all system prerequisites
- ✅ Create backups of existing data
- ✅ Set up virtual environment
- ✅ Install all dependencies
- ✅ Configure the platform
- ✅ Run validation tests
- ✅ Provide next steps

### For Windows Users

Run the Windows installer:

```batch
install.bat
```

## Prerequisites

The deployment script checks for these prerequisites automatically:

### Required

1. **Python 3.10 or higher**
   - Ubuntu/Debian: `sudo apt-get install python3 python3-pip python3-venv`
   - RHEL/Fedora: `sudo dnf install python3 python3-pip`
   - macOS: `brew install python@3.10`
   - Windows: Download from [python.org](https://www.python.org/)

2. **pip (Python package manager)**
   - Usually included with Python
   - Ubuntu/Debian: `sudo apt-get install python3-pip`

3. **venv (Virtual environment module)**
   - Ubuntu/Debian: `sudo apt-get install python3-venv`
   - Usually included with Python on other systems

### Recommended

4. **Build tools (for compiling Python packages)**
   - Ubuntu/Debian: `sudo apt-get install build-essential`
   - RHEL/Fedora: `sudo dnf groupinstall "Development Tools"`
   - macOS: `xcode-select --install`
   - Windows: Visual Studio Build Tools

5. **Git (for version control)**
   - Ubuntu/Debian: `sudo apt-get install git`
   - RHEL/Fedora: `sudo dnf install git`
   - macOS: Included with Xcode or `brew install git`
   - Windows: Download from [git-scm.com](https://git-scm.com/)

### System Requirements

- **Disk Space**: At least 500MB free
- **RAM**: 2GB minimum (4GB recommended)
- **Internet Connection**: Required for package installation
- **OS**: Windows 10+, Ubuntu 20.04+, macOS 10.15+, or equivalent

## Deployment Process Details

### 1. Prerequisite Checking

The script verifies:
- Python version (>= 3.10)
- pip availability
- venv module
- System dependencies
- Disk space
- Internet connectivity

If any required prerequisite is missing, the script will display installation instructions and exit.

### 2. Backup Creation

If you have existing configuration or data:
- Backups are created in `backups/backup_YYYYMMDD_HHMMSS/`
- Includes: config.yaml, data/, logs/

### 3. Virtual Environment Setup

- Creates isolated Python environment in `venv/`
- Prevents conflicts with system packages
- Can be recreated if needed

### 4. Dependency Installation

Installs all required packages from `requirements.txt`:
- Core dependencies (requests, aiohttp, websockets)
- Data processing (pandas, numpy)
- Technical analysis (ta-lib, pandas-ta)
- Web framework (flask, flask-socketio)
- Authentication (pyotp, cryptography)
- And more...

This step may take 5-10 minutes depending on your internet connection.

### 5. Configuration Setup

- Creates `config.yaml` from `config.example.yaml`
- Sets default to PAPER TRADING mode (safe)
- Ready to use without API credentials for paper trading

### 6. Directory Creation

Creates required directories:
- `data/` - Database storage
- `logs/` - Application logs
- `backups/` - Configuration backups

### 7. Validation Tests

Runs `test_platform.py` to verify:
- Module imports
- Configuration loading
- TOTP generation
- Database operations
- Agent initialization

## Manual Deployment

If you prefer manual installation or need to troubleshoot:

```bash
# 1. Clone repository (if not already done)
git clone https://github.com/birenpatel1975/BPSALGOAi.git
cd BPSALGOAi

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate.bat  # Windows

# 4. Upgrade pip
python -m pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Create configuration
cp config.example.yaml config.yaml

# 7. Create directories
mkdir -p data logs backups

# 8. Test installation
python test_platform.py

# 9. Run the platform
python -m roboai.main
```

## Post-Deployment

### Starting the Platform

**Option A: Web Dashboard (Recommended)**
```bash
./start_dashboard.sh
# Open http://localhost:5000 in your browser
```

**Option B: Console Mode**
```bash
./start_roboai.sh
```

### Configuration

Edit `config.yaml` to customize:

```yaml
# Trading mode
trading:
  mode: "paper"  # Use "paper" for testing, "live" for real trading
  auto_trade: false  # Enable automated trading

# API credentials (only needed for live trading)
mstock:
  api_key: "your_api_key"
  api_secret: "your_api_secret"
  totp_secret: "your_totp_secret"
  client_code: "your_client_code"

# Risk management
risk:
  max_daily_loss: 5000  # Maximum daily loss in INR
  max_position_size: 10000  # Maximum position size in INR
```

### First Run Checklist

- [ ] Platform starts without errors
- [ ] Configuration loads successfully
- [ ] Agents initialize properly
- [ ] Web dashboard accessible (if using)
- [ ] Paper trading mode confirmed

## Troubleshooting

### Python Version Issues

**Problem**: "Python 3.10 or higher is required"

**Solution**: 
```bash
# Check version
python3 --version

# Install correct version (Ubuntu)
sudo apt-get install python3.10 python3.10-venv python3.10-dev

# Use specific version
python3.10 -m venv venv
```

### Dependency Installation Fails

**Problem**: Some packages fail to install

**Solution**:
```bash
# Install system dependencies (Ubuntu)
sudo apt-get install build-essential python3-dev

# Try installing again
source venv/bin/activate
pip install -r requirements.txt
```

### TA-Lib Installation Issues

**Problem**: "ERROR: Could not find a version that satisfies the requirement ta-lib"

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install libta-lib0-dev
pip install TA-Lib

# macOS
brew install ta-lib
pip install TA-Lib

# Windows - Use pre-built wheel
pip install TA-Lib-0.4.28-cp312-cp312-win_amd64.whl
```

### Permission Denied

**Problem**: "./deploy.sh: Permission denied"

**Solution**:
```bash
chmod +x deploy.sh
./deploy.sh
```

### Virtual Environment Not Activating

**Problem**: "venv/bin/activate: No such file or directory"

**Solution**:
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
```

### Database Locked Error

**Problem**: "database is locked"

**Solution**:
```bash
# Ensure no other instance is running
./stop_roboai.sh

# Check for stale processes
ps aux | grep roboai

# If needed, kill processes
kill -9 <PID>
```

## Deployment Verification

After deployment, verify everything is working:

### 1. Run Tests
```bash
python test_platform.py
```
Expected: All tests should pass

### 2. Check Configuration
```bash
python -c "from roboai.utils import get_config; c = get_config(); print(c.get('trading.mode'))"
```
Expected: Should print "paper"

### 3. Start Platform
```bash
./start_roboai.sh
```
Expected: Platform starts without errors, shows startup banner

### 4. Check Logs
```bash
tail -f logs/roboai_$(date +%Y%m%d).log
```
Expected: No ERROR level messages

## Updating the Platform

To update to the latest version:

```bash
# 1. Backup current configuration
./deploy.sh  # Choose backup option

# 2. Pull latest changes
git pull origin main

# 3. Activate virtual environment
source venv/bin/activate

# 4. Update dependencies
pip install -r requirements.txt --upgrade

# 5. Restart platform
./stop_roboai.sh
./start_roboai.sh
```

## Uninstalling

To completely remove the platform:

```bash
# 1. Stop all processes
./stop_roboai.sh

# 2. Backup important data (optional)
cp -r data/ backups/ ~/roboai_backup/

# 3. Remove virtual environment and dependencies
rm -rf venv/

# 4. Remove data and logs (optional)
rm -rf data/ logs/

# 5. Remove the repository
cd ..
rm -rf BPSALGOAi/
```

## Production Deployment

For production environments:

### 1. Use systemd Service (Linux)

Create `/etc/systemd/system/roboai.service`:

```ini
[Unit]
Description=ROBOAi Trading Platform
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/BPSALGOAi
ExecStart=/path/to/BPSALGOAi/venv/bin/python -m roboai.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable roboai
sudo systemctl start roboai
sudo systemctl status roboai
```

### 2. Use Docker (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "-m", "roboai.main"]
```

Build and run:
```bash
docker build -t roboai .
docker run -d --name roboai -v ./config.yaml:/app/config.yaml roboai
```

### 3. Set Up Monitoring

- Configure log rotation
- Set up alerts for errors
- Monitor system resources
- Track trading performance

## Security Considerations

### API Credentials

- Never commit `config.yaml` to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Limit API key permissions

### File Permissions

```bash
# Restrict config file access
chmod 600 config.yaml

# Set proper directory permissions
chmod 700 data/ logs/ backups/
```

### Network Security

- Use firewall rules
- Enable HTTPS for web dashboard
- Implement rate limiting
- Regular security updates

## Getting Help

If you encounter issues during deployment:

1. **Check Logs**: Review `logs/roboai_YYYYMMDD.log`
2. **Run Tests**: Execute `python test_platform.py`
3. **Review Documentation**: See README.md and INSTALL.md
4. **GitHub Issues**: Open an issue with:
   - Operating system and version
   - Python version
   - Error messages
   - Steps to reproduce

## Success Indicators

You know deployment succeeded when:

- ✅ All prerequisite checks pass
- ✅ Dependencies install without errors
- ✅ Tests pass successfully
- ✅ Platform starts without errors
- ✅ Web dashboard is accessible (if using)
- ✅ Paper trading mode is active

## Next Steps

After successful deployment:

1. **Familiarize yourself** with the platform in paper trading mode
2. **Review documentation** to understand all features
3. **Test strategies** without risking real money
4. **Monitor performance** and adjust settings
5. **Only consider live trading** after thorough testing

---

**Remember**: Trading involves substantial risk. This platform is a tool to assist decision-making, not a guarantee of profits. Always trade responsibly and never risk money you cannot afford to lose.

**Happy Trading! 🚀📈**
