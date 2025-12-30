"""
mStock Authentication Module
Handles Type A API authentication to get JWT tokens
"""
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MStockAuth:
    """Handles Type A API authentication"""
    
    def __init__(self, api_key: str, base_url: str):
        """
        Initialize MStock Auth client
        
        Args:
            api_key: Type A API Key
            base_url: Base URL for Type A API (e.g., https://api.mstock.com)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.jwt_token = None
        self.token_expires_at = None
        self.session = requests.Session()
        logger.info(f"MStockAuth initialized with base URL: {self.base_url}")
    
    def authenticate(self) -> Optional[str]:
        """
        Authenticate using Type A API to get JWT token
        
        Returns:
            JWT token string if successful, None if failed
        """
        try:
            # Try common authentication endpoints
            endpoints = [
                f"{self.base_url}/v1/auth/token",
                f"{self.base_url}/auth/login",
                f"{self.base_url}/api/auth/token",
            ]
            
            for endpoint in endpoints:
                try:
                    response = self._auth_request(endpoint)
                    if response and response.get('success'):
                        self.jwt_token = response.get('token') or response.get('access_token')
                        if self.jwt_token:
                            # Set expiry (assume 1 hour if not provided)
                            exp_in = response.get('expires_in', 3600)
                            self.token_expires_at = datetime.now() + timedelta(seconds=exp_in)
                            logger.info(f"Successfully authenticated. Token expires at {self.token_expires_at}")
                            return self.jwt_token
                except Exception as e:
                    logger.debug(f"Auth endpoint {endpoint} failed: {e}")
                    continue
            
            logger.warning("All authentication endpoints failed; using API key directly")
            return None
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return None
    
    def _auth_request(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """
        Make an authentication request
        
        Args:
            endpoint: Authentication endpoint URL
            
        Returns:
            Response JSON or None if failed
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            response = self.session.get(endpoint, headers=headers, timeout=5)
            if response.ok:
                data = response.json()
                return data
            else:
                logger.debug(f"Auth endpoint returned {response.status_code}")
                return None
        except Exception as e:
            logger.debug(f"Auth request error: {e}")
            return None
    
    def get_token(self) -> Optional[str]:
        """
        Get valid JWT token, authenticating if necessary
        
        Returns:
            JWT token or None if authentication failed
        """
        # If token doesn't exist or is expired, re-authenticate
        if not self.jwt_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            self.authenticate()
        
        return self.jwt_token
    
    def is_token_valid(self) -> bool:
        """Check if current token is still valid"""
        if not self.jwt_token:
            return False
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            return False
        return True
