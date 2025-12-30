"""
mStock Authentication Module
Implements Type A API /connect/login for JWT token acquisition
"""
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MStockAuth:
    """Handles Type A API authentication and JWT token management"""
    
    def __init__(self, api_key: str, base_url: str):
        """
        Initialize MStock Auth client for Type A API
        
        Args:
            api_key: mStock API Key
            base_url: Type A API base URL (e.g., https://api.mstock.trade/openapi/typea)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.jwt_token = None
        self.token_expires_at = None
        self.session = requests.Session()
        logger.info(f"MStockAuth initialized with Type A base URL: {self.base_url}")
    
    def authenticate(self) -> Optional[str]:
        """
        Authenticate using Type A /connect/login endpoint
        
        Returns:
            JWT token if successful, None if failed
        """
        try:
            endpoint = f"{self.base_url}/connect/login"
            
            payload = {
                'apikey': self.api_key
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            logger.debug(f"Attempting Type A authentication at {endpoint}")
            response = self.session.post(endpoint, json=payload, headers=headers, timeout=10)
            
            if response.ok:
                data = response.json()
                logger.debug(f"Type A login response: {data}")
                
                # Extract JWT token from response
                # Try common response field names
                token = data.get('token') or data.get('jwttoken') or data.get('jwt_token') or data.get('access_token')
                
                if token:
                    self.jwt_token = token
                    # Set expiry (default to 1 hour if not provided)
                    exp_in = data.get('expires_in', 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=exp_in)
                    logger.info(f"Successfully authenticated with Type A API. Token expires at {self.token_expires_at}")
                    return self.jwt_token
                else:
                    logger.warning(f"Type A login response missing token field. Response: {data}")
                    return None
            else:
                logger.error(f"Type A login failed with status {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Type A authentication request timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to Type A API at {self.base_url}")
            return None
        except Exception as e:
            logger.error(f"Type A authentication error: {str(e)}")
            return None
    
    def get_token(self) -> Optional[str]:
        """
        Get valid JWT token, authenticating if necessary or if expired
        
        Returns:
            JWT token or None if authentication failed
        """
        # If token doesn't exist or is expired, authenticate
        if not self.jwt_token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            logger.debug("JWT token missing or expired, re-authenticating...")
            self.authenticate()
        
        return self.jwt_token
    
    def is_token_valid(self) -> bool:
        """Check if current token is still valid"""
        if not self.jwt_token:
            return False
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            return False
        return True

