# mStock Type A/B API Authentication Setup

This document explains the official mStock Type A/B API authentication flow implemented in bpsalgoAi.

## Official API Documentation
- **Type A**: https://tradingapi.mstock.com/docs/v1/typeA/User/
- **Type B**: https://tradingapi.mstock.com/docs/v1/typeB/User/

## Authentication Overview

mStock uses a **three-step authentication flow**:

### Step 1: Login (Get OTP)
```
POST https://api.mstock.trade/openapi/typea/connect/login
Headers:
  X-Mirae-Version: 1
  Content-Type: application/x-www-form-urlencoded

Body:
  username=your_username
  password=your_password

Response:
  {
    "status": "success",
    "data": {
      "ugid": "...",
      "cid": "YOUR_CLIENT_ID",
      ...
    }
  }
```
**OTP will be sent to your registered mobile number and/or email.**

### Step 2: Generate Access Token (Exchange OTP)
```
POST https://api.mstock.trade/openapi/typea/session/token
Headers:
  X-Mirae-Version: 1
  Content-Type: application/x-www-form-urlencoded

Body:
  api_key=YOUR_API_KEY
  request_token=OTP_RECEIVED
  checksum=L

Response:
  {
    "status": "success",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIs...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
      "user_name": "YOUR_USERNAME",
      "exchanges": ["NSE", "NFO", "CDS"],
      "products": ["CNC", "NRML", "MIS"],
      ...
    }
  }
```

### Step 3: Use Access Token for All API Calls
```
Authorization: token YOUR_API_KEY:YOUR_ACCESS_TOKEN
X-Mirae-Version: 1
```

**Important**: The access token is valid until 12:00 AM (midnight) of the generated day.

## Setup Instructions

### 1. Update `.env` with Your Credentials

Edit `bpsalgoAi/.env`:
```dotenv
# Your mStock trading account credentials
MSTOCK_USERNAME=your_username_here
MSTOCK_PASSWORD=your_password_here

# Your API key (generated from https://trade.mstock.com)
API_KEY=YOUR_API_KEY_HERE
```

### 2. Manual Authentication (During Development)

If TOTP is **disabled** (recommended for testing):

**Option A: Using Python REPL**
```python
from bpsalgoAi.app.mstock_auth import MStockAuth

auth = MStockAuth(
    api_key="YOUR_API_KEY",
    base_url="https://api.mstock.trade/openapi/typea",
    username="your_username",
    password="your_password"
)

# Step 1: Request OTP
auth.step1_login()
# Output: "Step 1 Success: OTP sent. Check SMS/Email"

# Wait for OTP to arrive on your phone/email

# Step 2: Exchange OTP for access token
otp = input("Enter OTP: ")  # e.g., "123456"
auth.step2_session_token(otp)
# Output: "Step 2 Success: Access token obtained"

# Now the access token is cached and used automatically
print(auth.access_token)
```

**Option B: Using Flask Shell**
```bash
cd d:\BPSALGOAi\BPSALGOAi
python -m flask shell
```

Then in the shell:
```python
from bpsalgoAi.app import create_app
from bpsalgoAi.app.routes import mstock_auth

# Step 1: Request OTP
mstock_auth.step1_login()

# Enter OTP when prompted
otp = input("Enter OTP: ")
mstock_auth.step2_session_token(otp)

# Verify token
print(f"Token valid: {mstock_auth.is_token_valid()}")
```

### 3. Verify Configuration

Visit API config endpoint while server is running:
```
GET http://localhost:5000/api/config
```

Response should show:
```json
{
  "type_a_api_configured": true,
  "type_b_api_configured": true,
  "credentials_present": true,
  "access_token_valid": true
}
```

### 4. Test Live Data Endpoint

Once authenticated:
```
GET http://localhost:5000/api/market/live
```

## Type A vs Type B

| Feature | Type A | Type B |
|---------|--------|--------|
| Base URL | `/openapi/typea` | `/openapi/typeb` |
| clientcode/username | ✓ Username | ✓ Clientcode |
| Use Case | Individual traders | Institutional accounts |
| Market Data | ✓ Yes | ✓ Yes |
| Orders | ✓ Yes | ✓ Yes |

Both Type A and Type B support the same endpoints. The application uses **Type A by default**.

## Important Security Notes

⚠️ **Never share:**
- API Key (X-PrivateKey)
- Access Token
- Username & Password

⚠️ **For Production:**
- Store credentials in secure environment variables
- Implement token refresh logic before midnight
- Use TOTP if enabled (requires `auth.step2_session_token()` or dedicated TOTP endpoint)
- Do not hardcode credentials in code

## Token Expiry

Access tokens are **valid until 12:00 AM (midnight) of the day they were generated**.

Implementation handles this by:
1. Checking token validity before API calls
2. Logging when token expires
3. Requiring re-authentication after midnight

## Endpoints Using Access Token

All endpoints require the `Authorization` header:

```
Authorization: token API_KEY:ACCESS_TOKEN
X-Mirae-Version: 1
```

### Available Endpoints (Type A)

- `POST /connect/login` - Initial login
- `POST /session/token` - Get access token
- `POST /session/verifytotp` - Verify TOTP (if enabled)
- `GET /user/fundsummary` - Account funds
- `GET /logout` - Invalidate token
- `POST /order/place` - Place order
- `GET /market/quotes` - Market data (see Market Quotes API docs)
- And more... (see official documentation)

## Troubleshooting

### "Not authenticated" message
- Ensure credentials are in `.env`
- Run `auth.step1_login()` and `auth.step2_session_token(otp)`
- Verify OTP was entered correctly
- Check if access token has expired (after midnight)

### "API is suspended/expired"
- Verify API key is valid at https://trade.mstock.com
- Check if API subscription is active
- Ensure API key hasn't been revoked

### "Invalid username or password"
- Verify credentials are correct
- Ensure account is active
- Check if multiple failed attempts locked the account

### "API is suspended for use"
- API Key may have expired
- Subscription may need renewal
- Generate a new API key from dashboard

## Testing Without Real Credentials

The application includes mock market data fallback:
- Dashboard will display sample NIFTY50, BANKNIFTY, FINNIFTY data
- Algo Agent can run with mock data
- Set `USE_WEBSOCKET=false` in `.env`

## References

- [mStock Type A API Docs](https://tradingapi.mstock.com/docs/v1/typeA/User/)
- [mStock Type B API Docs](https://tradingapi.mstock.com/docs/v1/typeB/User/)
- [Official Trading API Docs](https://tradingapi.mstock.com/)
