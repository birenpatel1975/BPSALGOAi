"""
mStock WebSocket Client
Handles real-time market data streaming from Mirae WebSocket API
"""
import websocket
import threading
import json
import logging

logger = logging.getLogger(__name__)

class MStockWSClient:
    def __init__(self, api_key, access_token, on_message=None):
        self.api_key = api_key
        self.access_token = access_token
        self.ws_url = f"wss://ws.mstock.trade?API_KEY={api_key}&ACCESS_TOKEN={access_token}"
        self.ws = None
        self.thread = None
        self.on_message = on_message
        self.connected = False

    def connect(self):
        def _on_open(ws):
            logger.info("WebSocket connection opened. Sending LOGIN message...")
            ws.send(f"LOGIN:{self.access_token}")
            self.connected = True

        def _on_message(ws, message):
            if self.on_message:
                self.on_message(message)
            else:
                logger.info(f"WebSocket message: {message}")

        def _on_error(ws, error):
            logger.error(f"WebSocket error: {error}")

        def _on_close(ws, close_status_code, close_msg):
            logger.info(f"WebSocket closed: {close_status_code} {close_msg}")
            self.connected = False

        self.ws = websocket.WebSocketApp(
            self.ws_url,
            on_open=_on_open,
            on_message=_on_message,
            on_error=_on_error,
            on_close=_on_close
        )
        self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.thread.start()

    def subscribe(self, tokens):
        """Subscribe to market data for given instrument tokens (list of ints)"""
        if self.ws and self.connected:
            msg = json.dumps({"a": "subscribe", "v": tokens})
            self.ws.send(msg)
            logger.info(f"Subscribed to tokens: {tokens}")

    def unsubscribe(self, tokens):
        """Unsubscribe from market data for given instrument tokens (list of ints)"""
        if self.ws and self.connected:
            msg = json.dumps({"a": "unsubscribe", "v": tokens})
            self.ws.send(msg)
            logger.info(f"Unsubscribed from tokens: {tokens}")

    def set_mode(self, mode):
        """Set data mode: 'ltp', 'quote', or 'full'"""
        if self.ws and self.connected:
            msg = json.dumps({"a": "mode", "v": [mode]})
            self.ws.send(msg)
            logger.info(f"Set data mode: {mode}")

    def close(self):
        if self.ws:
            self.ws.close()
            self.connected = False

# Usage example (not run automatically):
# def handle_message(msg):
#     print("Received WS message:", msg)
# ws_client = MStockWSClient(api_key, access_token, on_message=handle_message)
# ws_client.connect()
# ws_client.subscribe([55256, 55412])
# ws_client.set_mode('ltp')
# ...
# ws_client.close()
