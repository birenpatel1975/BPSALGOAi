# BPSALGOAi
AI-powered algorithmic trading platform for NSE F&O using mStock Type A/B APIs.

## Quick Start

### Prerequisites
- Python 3.10+
- mStock trading account with API credentials
- Windows 11 Pro (or any Python-compatible OS)

### Setup

1. **Activate Virtual Environment:**
```bash
& D:\BPSALGOAi\BPSALGOAi\.venv\Scripts\Activate.ps1
```

2. **Install Dependencies:**
```bash
pip install -r bpsalgoAi/requirements.txt
```

3. **Configure Credentials:**
Edit `bpsalgoAi/.env`:
```dotenv
MSTOCK_USERNAME=your_username
MSTOCK_PASSWORD=your_password
API_KEY=your_api_key
```

4. **Run Application:**
```bash
python run.py
```
Or without activating:
```bash
D:\BPSALGOAi\BPSALGOAi\.venv\Scripts\python.exe run.py
```

Or using Flask CLI:
```bash
$env:FLASK_APP='run.py'
$env:FLASK_ENV='development'
flask run --host=0.0.0.0 --port=5000
```

5. **Access Dashboard:**
Open browser to: http://localhost:5000

## Authentication

⚠️ **Important**: Before trading, you must authenticate with your mStock credentials.

### Authentication Steps:
1. Ensure `MSTOCK_USERNAME` and `MSTOCK_PASSWORD` are in `.env`
2. Run the application
3. Use Python/Flask shell to authenticate:
   - Step 1: `auth.step1_login()` → Receive OTP on SMS/Email
   - Step 2: `auth.step2_session_token(otp)` → Get access token

**See [AUTHENTICATION.md](./AUTHENTICATION.md) for detailed setup instructions.**

## Features

- **Dashboard**: Live market data display with NIFTY50, BANKNIFTY, FINNIFTY
- **Algo Agent**: Start/Stop automated trading controls
- **Account Info**: Real-time fund summary and balances
- **Activity Log**: Track all trading signals and executions
- **Type A/B Support**: Works with both mStock API types

## Architecture

```
bpsalgoAi/
├── run.py                    # Application entry point
├── config.py                 # Configuration & environment loading
├── requirements.txt          # Python dependencies
├── .env                      # Credentials (gitignored)
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── routes.py             # API endpoints & views
│   ├── mstock_auth.py        # Type A/B authentication (3-step flow)
│   ├── mstock_api.py         # mStock API client
│   ├── algo_agent.py         # Trading algorithm logic
│   ├── static/
│   │   ├── css/style.css     # Dashboard styling
│   │   └── js/dashboard.js   # Frontend interactivity
│   └── templates/
│       └── dashboard.html    # Web UI
```

## API Endpoints

### Algo Agent
- `POST /api/algo/start` - Start trading agent
- `POST /api/algo/stop` - Stop trading agent
- `GET /api/algo/status` - Get agent status

### Market Data
- `GET /api/market/live` - Live quotes for symbols
- `GET /api/market/quote/<symbol>` - Single symbol quote

### Account
- `GET /api/account/info` - Account fund summary

### Configuration
- `GET /api/config` - API configuration status
- `GET /health` - Health check

## mStock API Documentation

- **Type A Docs**: https://tradingapi.mstock.com/docs/v1/typeA/User/
- **Type B Docs**: https://tradingapi.mstock.com/docs/v1/typeB/User/
- **Official Docs**: https://tradingapi.mstock.com/

## Technology Stack

- **Backend**: Flask 2.3.3 (Python)
- **Frontend**: HTML/CSS/JavaScript
- **APIs**: mStock Type A/B REST APIs
- **Authentication**: Token-based (api_key + access_token)

## Important Notes

### Token Expiry
- Access tokens expire at 12:00 AM (midnight)
- Application auto-detects expiry and prompts re-authentication

### Security
- Never commit `.env` file with real credentials
- API Key and Access Token are sensitive - keep them private
- Use environment variables for production deployment

### Testing Without Real Credentials
- Dashboard displays mock data when not authenticated
- Perfect for UI/UX testing and development
- Algo Agent can run in simulation mode

## Troubleshooting

**Issue**: "Not authenticated" message
- **Solution**: See [AUTHENTICATION.md](./AUTHENTICATION.md) for step-by-step login

**Issue**: "API is suspended/expired"
- **Solution**: Verify API key is valid at https://trade.mstock.com

**Issue**: Markets not updating
- **Solution**: Ensure `access_token_valid` is `true` in `/api/config`

## Project Structure

```
d:\BPSALGOAi\BPSALGOAi\
├── README.md              # This file
├── AUTHENTICATION.md      # Authentication setup guide
├── .git/                  # Git repository
├── .venv/                 # Python virtual environment
├── bpsalgoAi/             # Main application
└── requirements.txt       # Dependencies
```

## Git Workflow

All changes committed to `backenddev` branch. Authentication implementation follows official mStock Type A/B API specification.

## License

Proprietary - BPS ALGOAi Trading Platform
