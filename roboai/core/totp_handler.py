"""TOTP Handler for mStock Authentication"""

import pyotp
from typing import Optional


class TOTPHandler:
    """Handles TOTP token generation for mStock authentication"""
    
    def __init__(self, totp_secret: str):
        """
        Initialize TOTP handler
        
        Args:
            totp_secret: The TOTP secret key for generating tokens
        """
        if not totp_secret:
            raise ValueError("TOTP secret cannot be empty")
        
        self.totp_secret = totp_secret
        self.totp = pyotp.TOTP(totp_secret)
    
    def generate_token(self) -> str:
        """
        Generate current TOTP token
        
        Returns:
            6-digit TOTP token as string
        """
        token = self.totp.now()
        return token
    
    def verify_token(self, token: str) -> bool:
        """
        Verify a TOTP token
        
        Args:
            token: The token to verify
        
        Returns:
            True if token is valid, False otherwise
        """
        return self.totp.verify(token)
    
    def get_provisioning_uri(self, name: str = "mStock", issuer_name: str = "ROBOAi") -> str:
        """
        Get provisioning URI for QR code generation
        
        Args:
            name: Account name
            issuer_name: Issuer name
        
        Returns:
            Provisioning URI string
        """
        return self.totp.provisioning_uri(name=name, issuer_name=issuer_name)
    
    @staticmethod
    def generate_secret() -> str:
        """
        Generate a new random TOTP secret
        
        Returns:
            Base32 encoded secret
        """
        return pyotp.random_base32()
