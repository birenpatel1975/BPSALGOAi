# ROBOAi Trading Platform - API Integration Guide

## Table of Contents
1. [Overview](#overview)
2. [mStock API Integration](#mstock-api-integration)
3. [Platform REST API](#platform-rest-api)
4. [WebSocket API](#websocket-api)
5. [Authentication](#authentication)
6. [Examples](#examples)

## Overview

ROBOAi integrates with external APIs and provides its own API for programmatic access.

### Architecture

```
┌─────────────────┐
│   ROBOAi Web    │  ← User Interface
└────────┬────────┘
         │ HTTP/WebSocket
┌────────▼────────┐
│  Flask Web API  │  ← Platform API
└────────┬────────┘
         │
┌────────▼────────┐
│  Agent System   │  ← Core Logic
└────────┬────────┘
         │
┌────────▼────────┐
│  mStock API     │  ← Broker Integration
└─────────────────┘
```

## mStock API Integration

### Setup

1. **Get API Credentials**:
   - Login to mStock account
   - Navigate to API section
   - Generate API key and secret
   - Note your client code

2. **Enable Two-Factor Authentication**:
   - Go to Settings → Security
   - Enable TOTP (Time-based OTP)
   - Save the secret key

3. **Configure ROBOAi**:
   ```yaml
   mstock:
     api_key: "your_api_key"
     api_secret: "your_api_secret"
     totp_secret: "your_totp_secret"
     client_code: "your_client_code"
   ```

### TOTP Authentication

ROBOAi automatically generates TOTP tokens for authentication.

**Manual TOTP Generation**:
```python
from roboai.core import TOTPHandler

totp = TOTPHandler("YOUR_TOTP_SECRET")
token = totp.generate_token()
print(f"Current token: {token}")

# Verify token
is_valid = totp.verify_token(token)
print(f"Token valid: {is_valid}")
```

**TOTP Token Lifecycle**:
- Generated every 30 seconds
- Valid for current and previous period (60 seconds total)
- Automatically refreshed during authentication

### mStock API Client

**Usage Example**:
```python
from roboai.core import MStockClient, TOTPHandler

# Initialize client
client = MStockClient(
    api_key="your_key",
    api_secret="your_secret",
    client_code="your_code"
)

# Generate TOTP
totp = TOTPHandler("your_totp_secret")
token = totp.generate_token()

# Authenticate
success = await client.authenticate(token)
if success:
    print("Authentication successful")
else:
    print("Authentication failed")
```

### Available mStock Methods

#### Market Data
```python
# Get quote
quote = await client.get_quote("NIFTY")

# Get option chain
chain = await client.get_option_chain("NIFTY", expiry="2024-01-25")

# Get market depth
depth = await client.get_market_depth("NIFTY50")
```

#### Order Management
```python
# Place order
order_id = await client.place_order(
    symbol="NIFTY 18000 CE",
    quantity=50,
    price=100.0,
    order_type="LIMIT",
    transaction_type="BUY"
)

# Modify order
success = await client.modify_order(
    order_id=order_id,
    quantity=75,
    price=95.0
)

# Cancel order
success = await client.cancel_order(order_id)
```

#### Position & Portfolio
```python
# Get positions
positions = await client.get_positions()

# Get holdings
holdings = await client.get_holdings()

# Get funds
funds = await client.get_funds()
```

### Auto-Reconnection

ROBOAi automatically reconnects to mStock if connection is lost.

**Configuration**:
```yaml
network:
  reconnect_interval: 60  # Reconnect every 60 seconds
  max_retries: 5          # Maximum retry attempts
  retry_delay: 10         # Delay between retries
```

**Implementation**:
```python
from roboai.core import ReconnectionManager

reconnection_manager = ReconnectionManager(
    client=mstock_client,
    interval=60
)

# Start auto-reconnection
await reconnection_manager.start()

# Stop auto-reconnection
await reconnection_manager.stop()
```

## Platform REST API

ROBOAi provides a Flask-based REST API for external access.

### Starting the API Server

```bash
# Start dashboard (includes API)
start_dashboard.bat  # Windows
./start_dashboard.sh  # Linux/Mac

# Or directly
python start_dashboard.py
```

Server runs on: `http://localhost:5000`

### API Endpoints

#### System Status

**GET /api/status**

Get platform status.

Response:
```json
{
  "status": "running",
  "version": "1.0.0",
  "mode": "paper",
  "agents": {
    "AuthAgent": "running",
    "DataAgent": "running",
    "MarketScannerAgent": "running",
    "StrategyAgent": "running",
    "ExecutionAgent": "running",
    "RCAAgent": "running",
    "PromptAgent": "running"
  }
}
```

#### Positions

**GET /api/positions**

Get current positions.

Response:
```json
{
  "positions": [
    {
      "symbol": "NIFTY 18000 CE",
      "quantity": 50,
      "average_price": 100.0,
      "current_price": 105.0,
      "pnl": 250.0,
      "pnl_percent": 5.0
    }
  ],
  "total_pnl": 250.0
}
```

#### Orders

**GET /api/orders**

Get order history.

Query parameters:
- `status`: Filter by status (pending/completed/cancelled)
- `limit`: Number of orders to return (default: 50)

Response:
```json
{
  "orders": [
    {
      "order_id": "12345",
      "symbol": "NIFTY 18000 CE",
      "quantity": 50,
      "price": 100.0,
      "type": "LIMIT",
      "side": "BUY",
      "status": "completed",
      "timestamp": "2024-01-17T10:30:00Z"
    }
  ]
}
```

**POST /api/orders**

Place new order.

Request:
```json
{
  "symbol": "NIFTY 18000 CE",
  "quantity": 50,
  "price": 100.0,
  "order_type": "LIMIT",
  "transaction_type": "BUY"
}
```

Response:
```json
{
  "order_id": "12345",
  "status": "placed",
  "message": "Order placed successfully"
}
```

#### Trading Control

**POST /api/trading/start**

Start auto-trading.

Response:
```json
{
  "status": "success",
  "message": "Auto-trading started"
}
```

**POST /api/trading/stop**

Stop auto-trading.

Response:
```json
{
  "status": "success",
  "message": "Auto-trading stopped"
}
```

#### Market Data

**GET /api/market/indices**

Get current index values.

Response:
```json
{
  "indices": [
    {
      "name": "NIFTY50",
      "value": 18000.50,
      "change": 150.25,
      "change_percent": 0.84
    }
  ]
}
```

**GET /api/market/scan**

Get latest scan results.

Response:
```json
{
  "opportunities": [
    {
      "symbol": "NIFTY 18000 CE",
      "signal": "BUY",
      "entry_price": 100.0,
      "target": 105.0,
      "stop_loss": 98.0,
      "confidence": 75.5,
      "reason": "Bullish breakout with high volume"
    }
  ]
}
```

#### Dynamic Commands

**POST /api/commands**

Submit dynamic command.

Request:
```json
{
  "prompt": "Increase position size by 20%"
}
```

Response:
```json
{
  "status": "success",
  "analysis": {
    "command_type": "position_size",
    "action": "apply",
    "description": "Adjust position size by 20%",
    "impact": "This will affect risk per trade...",
    "parameters": {
      "adjustment": 20,
      "current_size": 10000
    }
  }
}
```

**GET /api/commands/history**

Get command history.

Response:
```json
{
  "commands": [
    {
      "prompt": "Increase position size by 20%",
      "status": "applied",
      "timestamp": "2024-01-17T10:30:00Z"
    }
  ]
}
```

## WebSocket API

Real-time updates via WebSocket.

### Connection

```javascript
// JavaScript example
const socket = io('http://localhost:5000');

socket.on('connect', () => {
    console.log('Connected to ROBOAi');
});

socket.on('disconnect', () => {
    console.log('Disconnected from ROBOAi');
});
```

### Events

#### Market Updates

**Event**: `market_update`

Payload:
```json
{
  "type": "index_update",
  "symbol": "NIFTY50",
  "value": 18000.50,
  "change": 150.25,
  "timestamp": "2024-01-17T10:30:00Z"
}
```

#### Trade Signals

**Event**: `trade_signal`

Payload:
```json
{
  "type": "signal",
  "symbol": "NIFTY 18000 CE",
  "signal": "BUY",
  "entry_price": 100.0,
  "target": 105.0,
  "stop_loss": 98.0,
  "confidence": 75.5,
  "timestamp": "2024-01-17T10:30:00Z"
}
```

#### Order Updates

**Event**: `order_update`

Payload:
```json
{
  "type": "order_filled",
  "order_id": "12345",
  "symbol": "NIFTY 18000 CE",
  "quantity": 50,
  "price": 100.0,
  "status": "completed",
  "timestamp": "2024-01-17T10:30:00Z"
}
```

#### P&L Updates

**Event**: `pnl_update`

Payload:
```json
{
  "type": "pnl",
  "total_pnl": 1500.0,
  "daily_pnl": 250.0,
  "open_positions": 3,
  "timestamp": "2024-01-17T10:30:00Z"
}
```

## Authentication

### API Key Authentication

For programmatic access, use API keys.

**Generate API Key**:
```python
from roboai.utils import generate_api_key

api_key = generate_api_key()
print(f"Your API key: {api_key}")
```

**Use API Key**:
```python
import requests

headers = {
    'Authorization': f'Bearer {api_key}'
}

response = requests.get(
    'http://localhost:5000/api/positions',
    headers=headers
)
```

### Session Authentication

For web access, use session cookies.

```python
import requests

session = requests.Session()

# Login
session.post('http://localhost:5000/login', json={
    'username': 'admin',
    'password': 'your_password'
})

# Access protected endpoint
response = session.get('http://localhost:5000/api/positions')
```

## Examples

### Complete Trading Flow

```python
import asyncio
from roboai.core import MStockClient, TOTPHandler
from roboai.agents import StrategyAgent, ExecutionAgent

async def trading_flow():
    # 1. Authenticate
    client = MStockClient(api_key="key", api_secret="secret", client_code="code")
    totp = TOTPHandler("totp_secret")
    await client.authenticate(totp.generate_token())
    
    # 2. Get market data
    quote = await client.get_quote("NIFTY")
    print(f"NIFTY: {quote['last_price']}")
    
    # 3. Find opportunities
    strategy_agent = StrategyAgent()
    await strategy_agent.initialize()
    opportunities = await strategy_agent.scan_opportunities()
    
    # 4. Execute best trade
    if opportunities:
        best = opportunities[0]
        execution_agent = ExecutionAgent(client)
        order_id = await execution_agent.execute_trade(best)
        print(f"Order placed: {order_id}")
    
    # 5. Monitor position
    positions = await client.get_positions()
    for pos in positions:
        print(f"{pos['symbol']}: P&L = ₹{pos['pnl']}")

asyncio.run(trading_flow())
```

### WebSocket Client

```python
import socketio

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to ROBOAi')

@sio.on('trade_signal')
def on_signal(data):
    print(f"Signal: {data['signal']} {data['symbol']}")
    print(f"Entry: {data['entry_price']}, Target: {data['target']}")

@sio.on('order_update')
def on_order(data):
    print(f"Order {data['order_id']}: {data['status']}")

@sio.on('pnl_update')
def on_pnl(data):
    print(f"Total P&L: ₹{data['total_pnl']}")

sio.connect('http://localhost:5000')
sio.wait()
```

### Dynamic Command Injection

```python
from roboai.agents import PromptAgent

async def inject_commands():
    prompt_agent = PromptAgent()
    await prompt_agent.initialize()
    
    # Inject command
    result = await prompt_agent.inject_prompt(
        prompt="Increase position size by 25%",
        source="api"
    )
    
    print(f"Command: {result['description']}")
    print(f"Impact: {result['impact']}")
    
    if result['action'] == 'apply':
        print("Command will be applied")
    else:
        print(f"Command ignored: {result['reason']}")

asyncio.run(inject_commands())
```

### Custom Strategy Integration

```python
from roboai.strategies import BreakoutStrategy
import pandas as pd

# Create strategy
strategy = BreakoutStrategy(config={
    'breakout_lookback': 20,
    'volume_threshold': 1.5
})

# Get market data
data = pd.DataFrame({
    'open': [...],
    'high': [...],
    'low': [...],
    'close': [...],
    'volume': [...]
})

# Analyze
signal = strategy.analyze(data)

if signal:
    print(f"Signal: {signal['signal']}")
    print(f"Entry: {signal['entry_price']}")
    print(f"Target: {signal['target']}")
    print(f"Stop Loss: {signal['stop_loss']}")
    print(f"Confidence: {signal['confidence']}%")
```

## Error Handling

### Common Errors

```python
from roboai.core import MStockClient, AuthenticationError, APIError

client = MStockClient(...)

try:
    await client.authenticate(token)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except APIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Retry Logic

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def place_order_with_retry(client, order):
    return await client.place_order(**order)
```

## Rate Limiting

mStock API has rate limits. ROBOAi implements automatic rate limiting.

**Configuration**:
```yaml
network:
  rate_limit:
    enabled: true
    max_requests_per_second: 10
    burst_size: 20
```

**Manual Rate Limiting**:
```python
from roboai.utils import RateLimiter

limiter = RateLimiter(max_requests=10, time_window=1.0)

async def rate_limited_request():
    async with limiter:
        response = await client.get_quote("NIFTY")
    return response
```

## Testing

### Mock mStock API

For testing without real broker connection:

```python
from roboai.core import MockMStockClient

# Use mock client
client = MockMStockClient()

# Behaves like real client but returns simulated data
quote = await client.get_quote("NIFTY")
```

### Integration Tests

```python
import pytest
from roboai.core import MStockClient

@pytest.mark.asyncio
async def test_authentication():
    client = MStockClient(api_key="test", api_secret="test", client_code="test")
    result = await client.authenticate("123456")
    assert result == True

@pytest.mark.asyncio
async def test_place_order():
    client = MStockClient(...)
    order_id = await client.place_order(
        symbol="NIFTY 18000 CE",
        quantity=50,
        price=100.0,
        order_type="LIMIT",
        transaction_type="BUY"
    )
    assert order_id is not None
```

## Best Practices

1. **Always handle errors**: Network issues are common
2. **Use retry logic**: For transient failures
3. **Respect rate limits**: Avoid overwhelming the API
4. **Validate data**: Check responses before using
5. **Log everything**: Essential for debugging
6. **Use timeouts**: Prevent hanging requests
7. **Secure credentials**: Never hardcode API keys
8. **Test thoroughly**: Use paper trading first

## Support

- **mStock API Documentation**: Refer to mStock official docs
- **ROBOAi Issues**: GitHub repository
- **Community**: GitHub Discussions

---

**Remember**: Always test API integrations in paper trading mode first!
