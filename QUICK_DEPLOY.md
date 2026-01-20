# ROBOAi Trading Platform - Quick Deployment Guide

## 🚀 One-Command Deployment

### Linux/Mac

**Interactive Mode:**
```bash
./deploy.sh
```

**Automated Mode (CI/CD, no prompts):**
```bash
./deploy.sh --yes
```

### Windows
```batch
install.bat
```

## 🎯 Command Options

### deploy.sh Options

- **No flags**: Interactive mode with prompts
- **-y, --yes, --auto**: Skip all interactive prompts (for automation)
- **-h, --help**: Show help message

Example for CI/CD:
```bash
./deploy.sh --yes
```

## ✅ What Gets Checked

The deployment script automatically verifies:

- ✅ Python 3.10+ installed
- ✅ pip package manager available
- ✅ venv module present
- ✅ System build tools (optional)
- ✅ Sufficient disk space (500MB+)
- ✅ Internet connectivity

## 📦 What Gets Installed

The deployment script automatically:

1. **Creates backups** of existing configuration and data
2. **Sets up virtual environment** in `venv/` directory
3. **Installs 68 Python packages** including:
   - Flask (web framework)
   - pandas, numpy (data processing)
   - ta-lib (technical analysis)
   - scikit-learn (machine learning)
   - matplotlib, plotly (visualization)
   - aiohttp, websockets (async networking)
   - And many more...
4. **Creates configuration** from `config.example.yaml`
5. **Creates required directories**: `data/`, `logs/`, `backups/`
6. **Runs validation tests** to ensure everything works

## ⏱️ Time Required

- First-time deployment: **5-10 minutes**
- Subsequent deployments: **2-3 minutes**

Most time is spent downloading and installing Python packages.

## 📋 Prerequisites

### Required
- Python 3.10 or higher
- pip (Python package manager)
- 500MB free disk space
- Internet connection

### Installation Commands

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv build-essential
```

**RHEL/Fedora:**
```bash
sudo dnf install python3 python3-pip
```

**macOS:**
```bash
brew install python@3.10
```

**Windows:**
- Download from [python.org](https://www.python.org/)
- Check "Add Python to PATH" during installation

## 🎯 Deployment Output

When deployment succeeds, you'll see:

```
================================================================
          Deployment Complete!
================================================================

The ROBOAi Trading Platform has been successfully deployed!

Quick Start Options:

  [A] Web Dashboard (Recommended):
      ./start_dashboard.sh
      Then open: http://localhost:5000

  [B] Console Mode:
      ./start_roboai.sh
```

## ✅ Verification

### Check Installation
```bash
source venv/bin/activate
python test_platform.py
```

Expected output:
```
5/5 tests passed
🎉 All tests passed! Platform is ready to use.
```

### Verify Version
```bash
source venv/bin/activate
python -c "import roboai; print(roboai.__version__)"
```

Expected output: `1.0.0`

## 🏁 Next Steps

After successful deployment:

1. **Review Configuration**
   ```bash
   nano config.yaml  # or your preferred editor
   ```
   - Default mode is `paper` (safe for testing)
   - Add mStock API credentials only if using live trading

2. **Start the Platform**
   
   **Option A: Web Dashboard (Recommended)**
   ```bash
   ./start_dashboard.sh
   ```
   Then open: http://localhost:5000
   
   **Option B: Console Mode**
   ```bash
   ./start_roboai.sh
   ```

3. **Test in Paper Trading Mode**
   - Platform starts in paper trading mode by default
   - Test all features without risking real money
   - Learn the platform thoroughly

4. **Only After Thorough Testing**
   - Consider live trading
   - Start with small position sizes
   - Monitor closely

## 🔧 Troubleshooting

### Python Version Error
```bash
python3 --version  # Should show 3.10 or higher
```

If lower than 3.10:
```bash
# Ubuntu
sudo apt-get install python3.10 python3.10-venv

# macOS
brew install python@3.10
```

### Permission Denied
```bash
chmod +x deploy.sh
./deploy.sh
```

### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dependency Installation Fails

Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install build-essential python3-dev libta-lib0-dev

# macOS
brew install ta-lib
```

### Import Errors After Installation

Activate virtual environment first:
```bash
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate.bat  # Windows
```

## 📚 Additional Resources

- **Complete Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Installation Details**: [INSTALL.md](INSTALL.md)
- **Main Documentation**: [README.md](README.md)
- **Dashboard Guide**: [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)

## ⚠️ Important Reminders

- **Trading involves substantial risk**
- **Start with paper trading mode**
- **Never trade with money you can't afford to lose**
- **Test thoroughly before considering live trading**
- **Past performance ≠ future results**

## 🎉 Success Indicators

Deployment succeeded when:
- ✅ All prerequisite checks pass
- ✅ Virtual environment created
- ✅ All 68 packages installed
- ✅ Configuration file created
- ✅ All 5 tests pass
- ✅ Platform starts without errors

## 📞 Getting Help

If deployment fails:
1. Check error messages in terminal
2. Review [DEPLOYMENT.md](DEPLOYMENT.md)
3. Check `logs/roboai_*.log` files
4. Open GitHub issue with:
   - Operating system and version
   - Python version (`python3 --version`)
   - Error messages
   - Steps to reproduce

---

**Happy Trading! 🚀📈**

Remember: This is a tool to assist decision-making, not a guarantee of profits. Always trade responsibly.
