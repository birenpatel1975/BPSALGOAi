import ssl
import time
import sys

try:
    import requests
except Exception:
    print('requests not installed; please install requests in your venv')
    sys.exit(1)

try:
    from websocket import WebSocketApp
except Exception:
    print('websocket-client not installed; please install websocket-client in your venv')
    sys.exit(1)

CONFIG_URL = 'http://127.0.0.1:5000/api/config'

print('Fetching config from', CONFIG_URL)
try:
    resp = requests.get(CONFIG_URL, timeout=5)
    cfg = resp.json()
    print('Config:', cfg)
except Exception as e:
    print('Failed to fetch config:', e)
    sys.exit(1)

ws_url = cfg.get('ws_endpoint')
if not ws_url:
    print('No ws_endpoint in config; access_token_valid=', cfg.get('access_token_valid'))
    sys.exit(1)

print('\nWS endpoint found:', ws_url[:200], '...')

# Handlers

def make_handlers(prefix=''):
    def on_open(ws):
        print(prefix + 'OPEN')
        # send a ping then close after short delay
        try:
            ws.send('ping')
        except Exception as e:
            print(prefix + 'send ping error:', e)

    def on_message(ws, msg):
        print(prefix + 'MSG:', msg)

    def on_error(ws, err):
        print(prefix + 'ERROR:', err)

    def on_close(ws, code, reason):
        print(prefix + 'CLOSE:', code, reason)

    return on_open, on_message, on_error, on_close

# Attempt 1: without Origin header
print('\nAttempt 1: connect without Origin header')
open1, msg1, err1, close1 = make_handlers('[NO-ORIGIN] ')
ws1 = WebSocketApp(ws_url, on_open=open1, on_message=msg1, on_error=err1, on_close=close1)
try:
    ws1.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, timeout=10)
except Exception as e:
    print('[NO-ORIGIN] run_forever exception:', e)

# Pause
print('\nSleeping 1s before second attempt...')
time.sleep(1)

# Attempt 2: with Origin header
print('\nAttempt 2: connect with Origin header http://127.0.0.1')
open2, msg2, err2, close2 = make_handlers('[ORIGIN] ')
headers = ["Origin: http://127.0.0.1"]
ws2 = WebSocketApp(ws_url, on_open=open2, on_message=msg2, on_error=err2, on_close=close2, header=headers)
try:
    ws2.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}, timeout=10)
except Exception as e:
    print('[ORIGIN] run_forever exception:', e)

print('\nTest complete')
