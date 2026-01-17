# ROBOAi Trading Platform - Server Commands

## Architecture Note

ROBOAi Trading Platform currently runs as a **unified application** (single process) that includes:
- Backend logic (agents, trading engine, database)
- Console-based interface (command-line UI)

There is no separate frontend/backend server architecture in the current version. The platform is designed as a standalone application.

## Starting the Platform

### Method 1: Direct Python Command (Recommended)

#### On Windows:
```batch
# Activate virtual environment
venv\Scripts\activate

# Start the platform
python -m roboai.main
```

#### On Linux/Mac:
```bash
# Activate virtual environment
source venv/bin/activate

# Start the platform
python -m roboai.main
```

### Method 2: Using Convenience Scripts (see below)

```batch
# Windows
start_roboai.bat

# Linux/Mac
./start_roboai.sh
```

## Stopping the Platform

### Graceful Shutdown:
Press `Ctrl+C` in the terminal where the platform is running.

The platform will:
1. Stop all agents gracefully
2. Close database connections
3. Save final state
4. Exit cleanly

### Force Kill (Not Recommended):
Only use if graceful shutdown fails.

**Windows:**
```batch
taskkill /F /IM python.exe
```

**Linux/Mac:**
```bash
pkill -9 -f "roboai.main"
```

## Platform Status

### Check if Running:

**Windows:**
```batch
tasklist | findstr python.exe
```

**Linux/Mac:**
```bash
ps aux | grep "roboai.main"
```

### View Logs in Real-time:

**Windows:**
```batch
type logs\roboai_YYYYMMDD.log
```

**Linux/Mac:**
```bash
tail -f logs/roboai_$(date +%Y%m%d).log
```

## Background/Daemon Mode

### Running in Background (Linux/Mac):

```bash
# Start in background
nohup python -m roboai.main > roboai.out 2>&1 &

# Save process ID
echo $! > roboai.pid

# Stop background process
kill $(cat roboai.pid)

# View output
tail -f roboai.out
```

### Running as Windows Service:

Use `nssm` (Non-Sucking Service Manager):

```batch
# Install nssm
# Download from https://nssm.cc/

# Create service
nssm install ROBOAi "C:\path\to\venv\Scripts\python.exe" "-m roboai.main"

# Start service
nssm start ROBOAi

# Stop service
nssm stop ROBOAi

# Remove service
nssm remove ROBOAi
```

## Quick Reference

| Action | Windows | Linux/Mac |
|--------|---------|-----------|
| **Start** | `python -m roboai.main` | `python -m roboai.main` |
| **Stop** | `Ctrl+C` | `Ctrl+C` |
| **Status** | `tasklist \| findstr python` | `ps aux \| grep roboai` |
| **Logs** | `type logs\roboai_*.log` | `tail -f logs/roboai_*.log` |

## Testing Before Start

Always test the platform before starting:

```bash
python test_platform.py
```

Expected output: `5/5 tests passed`

## Configuration Check

Verify configuration before starting:

```bash
python -c "from roboai.utils import get_config; c = get_config(); print(f'Mode: {c.get(\"trading.mode\")}')"
```

## Troubleshooting

### Platform won't start:
1. Check Python version: `python --version` (need 3.10+)
2. Check dependencies: `pip install -r requirements.txt`
3. Check config: Ensure `config.yaml` exists
4. Check logs: Review error messages in logs directory

### Platform won't stop:
1. Try `Ctrl+C` multiple times
2. Use force kill commands (see above)
3. Restart terminal/system if needed

### Can't find process:
```bash
# Check all Python processes
ps aux | grep python  # Linux/Mac
tasklist | findstr python  # Windows
```

---

## Future Architecture (Planned for v2.0)

In future versions, the platform will support separate frontend/backend:

**Backend API Server:**
- REST API for frontend communication
- WebSocket for real-time updates
- Command: `python -m roboai.backend`

**Frontend Dashboard:**
- Web-based UI (React/Vue)
- Real-time charts and monitoring
- Command: `npm run serve` or `yarn start`

This separation is planned but not yet implemented.
