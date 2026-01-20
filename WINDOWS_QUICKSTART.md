# ROBOAi Trading Platform - Windows Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:
- Python 3.10 or higher installed
- Python added to PATH (verify with `python --version`)
- Internet connection for package installation

## Step 1: Installation

Open PowerShell or Command Prompt in the project directory and run:

```batch
install.bat
```

This will:
1. Check Python installation
2. Create virtual environment (`venv` folder)
3. Install all required packages
4. Create configuration file (`config.yaml`)
5. Set up desktop shortcuts (optional)

**Important:** If you get a "venv already exists" message, the script will use the existing one.

## Step 2: Starting the Platform

### Option A: Web Dashboard (Recommended)

The web dashboard provides a user-friendly interface to control the platform.

**Start Dashboard:**
```batch
start_dashboard.bat
```

**Access Dashboard:**
Open your browser and go to: **http://localhost:5000**

**Features:**
- 🎛️ Toggle Paper/Live trading modes
- 🤖 Switch Algo AI/Manual strategies
- 📊 Real-time P&L monitoring
- 👁️ View positions and trades
- ⚙️ Configure strategies

### Option B: Console Mode (Advanced)

For command-line interface and direct platform control.

**Start Platform:**
```batch
start_roboai.bat
```

You'll see the ROBOAi banner and agent status updates.

## Step 3: Stopping the Platform

### Method 1: Graceful Shutdown (Recommended)
Press `Ctrl+C` in the terminal where the platform is running.

### Method 2: Using Stop Script
```batch
stop_roboai.bat
```

This will find and stop all ROBOAi processes.

### Method 3: Manual Process Kill (Last Resort)
```batch
tasklist | findstr python.exe
taskkill /PID <process_id> /F
```

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'roboai'"

**Cause:** Virtual environment is not activated or not created.

**Solution:**
```batch
# Option 1: Reinstall
install.bat

# Option 2: Manual activation
cd D:\BPSALGOAi\BPSALGOAi
venv\Scripts\activate
python -m roboai.main
```

### Issue: "Virtual environment not found"

**Solution:** Run `install.bat` to create it:
```batch
install.bat
```

### Issue: "Python is not installed or not in PATH"

**Solution:**
1. Download Python 3.10+ from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart Command Prompt/PowerShell
4. Verify: `python --version`

### Issue: Dashboard won't start

**Solution:**
```batch
# Ensure virtual environment exists
venv\Scripts\activate

# Check if port 5000 is available
netstat -an | findstr :5000

# Start dashboard
python start_dashboard.py
```

## Architecture Overview

```
ROBOAi Platform Architecture:
├── Backend (Trading Engine)
│   ├── 7 AI Agents (trading logic)
│   ├── Market Scanner
│   ├── Strategy Engine
│   └── Execution Engine
├── Frontend (Web Dashboard)
│   ├── Flask Web Server
│   ├── Real-time Updates (SocketIO)
│   └── Browser Interface
└── Database (SQLite)
    ├── Trades
    ├── Positions
    └── Logs
```

**Note:** The platform runs as a unified application. The "backend" runs when you start either:
- `start_roboai.bat` - Console mode (backend only)
- `start_dashboard.bat` - Web mode (backend + frontend)

## Quick Commands Reference

| Action | Command | Description |
|--------|---------|-------------|
| **Install** | `install.bat` | First-time setup |
| **Start Dashboard** | `start_dashboard.bat` | Launch web interface |
| **Start Console** | `start_roboai.bat` | Launch CLI mode |
| **Stop Platform** | `Ctrl+C` or `stop_roboai.bat` | Graceful shutdown |
| **Check Status** | `tasklist \| findstr python.exe` | See running processes |
| **View Config** | `notepad config.yaml` | Edit configuration |
| **View Logs** | `type logs\roboai_YYYYMMDD.log` | View today's logs |

## File Structure

```
D:\BPSALGOAi\BPSALGOAi\
├── venv\                    # Virtual environment (created by install.bat)
├── roboai\                  # Main application code
├── config.yaml              # Configuration file
├── config.example.yaml      # Template
├── install.bat              # Setup script
├── start_roboai.bat         # Start console mode
├── start_dashboard.bat      # Start web dashboard
├── start_dashboard.py       # Dashboard entry point
├── stop_roboai.bat          # Stop platform
├── requirements.txt         # Python dependencies
├── data\                    # Database files
└── logs\                    # Log files
```

## Next Steps

1. ✅ **Install:** Run `install.bat` (one time)
2. ✅ **Configure:** Edit `config.yaml` (optional for paper trading)
3. ✅ **Start:** Run `start_dashboard.bat` or `start_roboai.bat`
4. ✅ **Access:** Open http://localhost:5000 (if using dashboard)
5. ✅ **Test:** Platform starts in PAPER TRADING mode (safe)

## Getting Help

- **Full Documentation:** See `README.md`
- **Dashboard Guide:** See `DASHBOARD_GUIDE.md`
- **Installation Issues:** See `INSTALL.md`
- **Server Commands:** See `SERVER_COMMANDS.md`

## Safety Reminders

⚠️ **Default Mode:** PAPER TRADING (no real money)
⚠️ **API Credentials:** Not required for paper trading
⚠️ **Risk Warning:** Trading involves substantial risk
⚠️ **Testing:** Always test thoroughly before live trading

---

**Need more help?** Check the documentation files or open an issue on GitHub.
