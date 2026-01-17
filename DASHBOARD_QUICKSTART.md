# ROBOAi Web Dashboard - Quick Start

## Start the Dashboard

```bash
# Windows
start_dashboard.bat

# Linux/Mac
./start_dashboard.sh

# Direct
python start_dashboard.py
```

**URL**: http://localhost:5000

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────┐
│  🤖 ROBOAi Trading Platform                v1.0.0       │
│                                    🟢 Connected          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Control Panel                                           │
│  ┌──────────┐  ┌────────────────┐  ┌─────────────────┐ │
│  │ Platform │  │ Trading Mode   │  │ Strategy Mode   │ │
│  │ ▶ Start  │  │ 📝 Paper  💰Live│  │ 🤖 Algo  👤Manual│ │
│  │ ■ Stop   │  │                │  │                 │ │
│  └──────────┘  └────────────────┘  └─────────────────┘ │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Profit & Loss                                           │
│  ┌──────────┬──────────┬──────────┬──────────┐         │
│  │ Daily P&L│ Total P&L│ Realized │Unrealized│         │
│  │  ₹0.00   │  ₹0.00   │  ₹0.00   │  ₹0.00   │         │
│  └──────────┴──────────┴──────────┴──────────┘         │
│  [P&L Chart]                                             │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Agent Status                                            │
│  ┌─────────┬─────────┬─────────┬─────────┐             │
│  │Auth 🟢  │Data 🟢  │Market🟢 │Strategy🟢│             │
│  │Exec 🟢  │Sent 🟢  │RCA 🟢   │Manager🟢 │             │
│  └─────────┴─────────┴─────────┴─────────┘             │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  Active Positions | Recent Trades                       │
│  [Tables with live data]                                │
├─────────────────────────────────────────────────────────┤
│  Strategy Configuration                                  │
│  Profit Lock: ₹500  Trailing SL: 20%  Target: ₹1000    │
│  💾 Save Configuration                                   │
└─────────────────────────────────────────────────────────┘
```

## Key Actions

| Action | Button | Location |
|--------|--------|----------|
| **Start Trading** | ▶ Start Platform | Control Panel |
| **Stop Trading** | ■ Stop Platform | Control Panel |
| **Paper Mode** | 📝 Paper Trading | Trading Mode |
| **Live Mode** | 💰 Live Trading | Trading Mode |
| **Enable Algo** | 🤖 Algo AI | Strategy Mode |
| **Manual Trading** | 👤 Manual | Strategy Mode |
| **Save Config** | 💾 Save Configuration | Bottom |

## Trading Modes

### Paper Trading (Safe)
- 📝 Simulated trades
- No real money
- Perfect for testing
- **Default mode**

### Live Trading (Real Money)
- 💰 Real order execution
- Actual funds at risk
- ⚠️ Use with caution
- Test in paper first!

## Strategy Modes

### Algo AI (Automated)
- 🤖 AI makes decisions
- Automated entry/exit
- Based on configured strategies
- Hands-free trading

### Manual (You Control)
- 👤 You make decisions
- Manual order placement
- Full control
- Learn the platform

## High-Precision Strategies

### Entry Signals

**For Call Options (CE)**:
```
✓ Price > VWAP
✓ 9 EMA > 21 EMA
✓ RSI > 60
→ BUY Weekly ATM CE
```

**For Put Options (PE)**:
```
✓ Price < VWAP
✓ 9 EMA < 21 EMA
✓ RSI < 40
→ BUY Weekly ATM PE
```

### Profit Management

```
Step 1: Reach ₹500 profit
        ↓
Step 2: Activate Safety Mode
        ↓
Step 3: Set trailing stop at 20%
        ↓
Step 4: Profit grows → SL trails up
        ↓
Step 5: Never lose >20% of peak
```

**Example**:
- Profit = ₹500 → SL at ₹400 (₹500 - 20%)
- Profit = ₹1000 → SL at ₹800 (₹1000 - 20%)
- Profit = ₹2000 → SL at ₹1600 (₹2000 - 20%)

## Real-Time Updates

- **Status**: Every 5 seconds
- **P&L**: Real-time
- **Positions**: Live updates
- **Trades**: Auto-refresh
- **WebSocket**: Instant notifications

## Quick Checks

### ✅ Dashboard is Working
- 🟢 Connection status is green
- Agents show status
- P&L displays values
- Tables load data

### ❌ Dashboard Issues
- 🔴 Connection status is red
- Agents show no status
- P&L shows ₹0.00
- Tables show "No data"

**Fix**: Refresh page, check if platform is started

## Safety Checklist

Before trading:
- [ ] Dashboard connected (🟢)
- [ ] Mode set to Paper 📝
- [ ] Platform started ▶
- [ ] Agents running (8/8 🟢)
- [ ] P&L tracking working
- [ ] Stop loss configured
- [ ] Position limits set

## Keyboard Shortcuts

- `Ctrl+R` or `F5`: Refresh dashboard
- `Ctrl+Shift+R`: Hard refresh (clear cache)
- `F12`: Open developer console
- `Ctrl+W`: Close tab

## Troubleshooting

### Dashboard won't load
1. Check server is running
2. Try http://127.0.0.1:5000
3. Clear browser cache

### Platform won't start
1. Check logs in logs/
2. Verify config.yaml exists
3. Ensure dependencies installed

### Data not updating
1. Check WebSocket (🟢 indicator)
2. Refresh page
3. Restart dashboard server

## Documentation

- **Full Guide**: DASHBOARD_GUIDE.md
- **Installation**: INSTALL.md
- **General**: README.md
- **Server Commands**: SERVER_COMMANDS.md

## Support

Issues? Check:
1. Browser console (F12)
2. Server logs
3. GitHub issues

---

**Remember**: Always start in Paper Trading mode! 📝
