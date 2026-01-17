# ROBOAi Quick Reference Card

## 🚀 Start/Stop Commands

### Start Platform

| OS | Command |
|----|---------|
| **Windows** | `start_roboai.bat` |
| **Linux/Mac** | `./start_roboai.sh` |
| **Direct** | `python -m roboai.main` |

### Stop Platform

| OS | Command |
|----|---------|
| **Windows** | `stop_roboai.bat` or `Ctrl+C` |
| **Linux/Mac** | `./stop_roboai.sh` or `Ctrl+C` |

## 📊 Platform Status

| Action | Windows | Linux/Mac |
|--------|---------|-----------|
| **Check if running** | `tasklist \| findstr python` | `ps aux \| grep roboai` |
| **View logs** | `type logs\roboai_*.log` | `tail -f logs/roboai_*.log` |
| **Check config** | `type config.yaml` | `cat config.yaml` |

## 🧪 Testing

```bash
# Run test suite
python test_platform.py

# Expected: 5/5 tests passed
```

## ⚙️ Configuration

```bash
# Edit configuration
notepad config.yaml     # Windows
nano config.yaml        # Linux/Mac

# Key settings:
# - trading.mode: "paper" or "live"
# - trading.auto_trade: true/false
# - trading.max_positions: 5
# - risk.max_daily_loss: 5000
```

## 📁 Important Files

| File | Purpose |
|------|---------|
| `config.yaml` | Main configuration |
| `logs/roboai_*.log` | Application logs |
| `data/roboai.db` | Database (trades, orders) |
| `SERVER_COMMANDS.md` | Detailed server commands |
| `README.md` | Full documentation |

## 🛡️ Safety Checklist

- [ ] Config mode set to "paper" for testing
- [ ] auto_trade disabled for manual control
- [ ] Reviewed risk limits in config
- [ ] Tested with test_platform.py
- [ ] API credentials configured (if live)
- [ ] Understand stop-loss settings

## 🔗 Quick Links

- Full Documentation: [README.md](README.md)
- Installation Guide: [INSTALL.md](INSTALL.md)
- Server Commands: [SERVER_COMMANDS.md](SERVER_COMMANDS.md)
- Project Summary: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

## ⚠️ Emergency Stop

If normal stop doesn't work:

**Windows:**
```batch
taskkill /F /IM python.exe
```

**Linux/Mac:**
```bash
pkill -9 -f roboai.main
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Won't start | Check: Python version, dependencies, config.yaml |
| Won't stop | Try Ctrl+C multiple times, then use stop script |
| No trades | Check: auto_trade enabled, market hours, strategies |
| Errors in logs | Review logs/ directory for details |

---

**Remember:** Always start in paper trading mode! 📝
