"""
mStock Authentication Module
Implements Type A API authentication flow:
1. /connect/login (username + password) → OTP sent
2. /session/token (api_key + OTP) → access_token
"""
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)


class MStockAuth:
    """
    Handles Type A API authentication and access token management
    """

    def get_ws_token(self) -> Optional[str]:
        """
        Fetch the WebSocket token from mStock (Type A).
        This is NOT the REST JWT, but a short token specifically for WebSocket authentication.
        Returns:
            WebSocket token string, or None if failed.
        """
        try:
            endpoint = f"{self.base_url}/session/token"
            headers = {
                'X-Mirae-Version': '1',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            # Use API key and OTP (or request_token if already verified)
            # Fallback: if request_token is not set, try using access_token
            req_token = self.request_token or self.access_token or ''
            payload = {
                'api_key': self.api_key,
                'request_token': req_token,
                'checksum': 'L'
            }
            response = self.session.post(endpoint, data=payload, headers=headers, timeout=10)
            if response.ok:
                data = response.json()
                if data.get('status') == 'success':
                    ws_token = data.get('data', {}).get('access_token', '')
                    if ws_token and len(ws_token) < 300:
                        logger.info(f"WS token obtained: {ws_token[:20]}... (truncated)")
                        return ws_token
                    else:
                        logger.error(f"WS token response invalid length: {len(ws_token)}")
                else:
                    logger.error(f"WS token fetch failed: {data.get('message', 'Unknown error')}")
            else:
                logger.error(f"WS token HTTP error {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Error fetching WS token: {e}")
        return None
    
    def __init__(self, api_key: str, base_url: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize MStock Auth client for Type A API
        
        Args:
            api_key: mStock API Key
            base_url: Type A API base URL (e.g., https://api.mstock.trade/openapi/typea)
            username: mStock username (can be set via env or constructor)
            password: mStock password (can be set via env or constructor)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.username = username or os.getenv('MSTOCK_USERNAME', '')
        self.password = password or os.getenv('MSTOCK_PASSWORD', '')
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.request_token = None  # Will store OTP temporarily
        self.session = requests.Session()
        logger.info(f"MStockAuth initialized with Type A base URL: {self.base_url}")
    
    def step1_login(self) -> bool:
        """
        Step 1: Send username/password to /connect/login
        Returns OTP via SMS/Email
        
        Returns:
            True if OTP was sent, False otherwise
        """
        try:
            if not self.username or not self.password:
                logger.error("Username and password required for Type A login")
                return False
            
            endpoint = f"{self.base_url}/connect/login"
            
            headers = {
                'X-Mirae-Version': '1',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            payload = {
                'username': self.username,
                'password': self.password
            }
            
            logger.debug(f"Step 1: Sending login request to {endpoint}")
            response = self.session.post(endpoint, data=payload, headers=headers, timeout=10)
            
            if response.ok:
                data = response.json()
                logger.info(f"Step 1 Success: OTP sent. Response: {data.get('message', 'Check SMS/Email')}")
                return True
            else:
                logger.error(f"Step 1 Failed with status {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Step 1 Error: {str(e)}")
            return False
    
    def step2_session_token(self, otp: str) -> bool:
        """
        Step 2: Exchange API key + OTP for access_token via /session/token
        
        Args:
            otp: OTP received via SMS/Email
            
        Returns:
            True if access token obtained, False otherwise
        """
        try:
            if not self.api_key or not otp:
                logger.error("API key and OTP required for session token")
                return False
            endpoint = f"{self.base_url}/session/token"
            headers = {
                'X-Mirae-Version': '1',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            payload = {
                'api_key': self.api_key,
                'request_token': otp,  # OTP is used as request_token
                'checksum': 'L'  # Required by API
            }
            logger.debug(f"Step 2: Exchanging OTP for access token at {endpoint}")
            response = self.session.post(endpoint, data=payload, headers=headers, timeout=10)
            if response.ok:
                data = response.json()
                logger.debug(f"Step 2 Response: {data}")
                if data.get('status') == 'success':
                    self.access_token = data.get('data', {}).get('access_token', '')
                    self.refresh_token = data.get('data', {}).get('refresh_token', '')
                    self.request_token = otp  # Store OTP for WS token retrieval
                    if self.access_token:
                        logger.info(f"Step 2 Success: Access token obtained. Token: {self.access_token[:20]}... (truncated)")
                        self.token_expires_at = datetime.now() + timedelta(hours=24)
                        return True
                    else:
                        logger.error(f"Step 2 Failed: No access_token in response: {data}")
                        return False
                else:
                    logger.error(f"Step 2 Failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                logger.error(f"Step 2 Failed with status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Step 2 Error: {str(e)}")
            return False
    
    def get_token(self) -> Optional[str]:
        """
        Get valid access token
        Note: In production, implement full login flow with OTP input
        
        Returns:
            access_token or None if not authenticated
        """
        # Check if token exists and is still valid
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token

        # Try to refresh automatically if refresh_token is available
        if self.refresh_token:
            logger.info("Access token expired or missing — attempting refresh using refresh_token")
            try:
                refreshed = self.refresh_session()
                if refreshed and self.access_token:
                    return self.access_token
            except Exception as e:
                logger.warning(f"Automatic refresh failed: {e}")

        logger.warning("Access token missing or expired. Please authenticate with OTP.")
        logger.warning("Run: auth.step1_login() → receive OTP → auth.step2_session_token(otp)")
        return None

    def refresh_session(self) -> bool:
        """
        Attempt to refresh the session using the stored refresh token.

        Returns:
            True if refresh succeeded and access_token updated, False otherwise.
        """
        try:
            if not self.refresh_token:
                logger.error("No refresh_token available to refresh session")
                return False

            endpoint = f"{self.base_url}/session/refresh"
            headers = {
                'X-Mirae-Version': '1',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            payload = {
                'api_key': self.api_key,
                'refresh_token': self.refresh_token
            }

            logger.debug(f"Refreshing session at {endpoint}")
            response = self.session.post(endpoint, data=payload, headers=headers, timeout=10)

            if response.ok:
                data = response.json()
                if data.get('status') == 'success':
                    new_access = data.get('data', {}).get('access_token')
                    new_refresh = data.get('data', {}).get('refresh_token')
                    expires_in = data.get('data', {}).get('expires_in')

                    if new_access:
                        self.access_token = new_access
                        if new_refresh:
                            self.refresh_token = new_refresh
                        # If expires_in provided, set expiry accordingly; otherwise default to 24h
                        if expires_in:
                            try:
                                self.token_expires_at = datetime.now() + timedelta(seconds=int(expires_in))
                            except Exception:
                                self.token_expires_at = datetime.now() + timedelta(hours=24)
                        else:
                            self.token_expires_at = datetime.now() + timedelta(hours=24)

                        logger.info("Session refreshed successfully")
                        return True
                    else:
                        logger.error(f"Refresh succeeded but no access_token returned: {data}")
                        return False
                else:
                    logger.error(f"Refresh failed: {data.get('message', 'Unknown error')}")
                    return False
            else:
                logger.error(f"Refresh HTTP error {response.status_code}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Error refreshing session: {e}")
            return False
    
    def is_token_valid(self) -> bool:
        """Check if current access token is still valid"""
        if not self.access_token:
            return False
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            return False
        return True
    
    def get_auth_header(self) -> Dict[str, str]:
        """Get authorization header for subsequent API calls"""
        if self.access_token:
            return {
                'X-Mirae-Version': '1',
                'Authorization': f'token {self.api_key}:{self.access_token}'
            }
        return {}

