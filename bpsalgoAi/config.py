import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# mStock API Configuration
# Type A: For authentication
TYPE_A_API_KEY = os.getenv('TYPE_A_API_KEY', 'MAm4VlPS4JZKzr4x+pbxEZpaA2K0RA8YezG9r9QQ9O0=')
TYPE_A_API_BASE_URL = os.getenv('TYPE_A_API_BASE_URL', 'https://api.mstock.com')

# Type B: For market data
TYPE_B_API_KEY = os.getenv('TYPE_B_API_KEY', '')
TYPE_B_API_BASE_URL = os.getenv('TYPE_B_API_BASE_URL', 'https://api.mstock.com')

# WebSocket Configuration
MSTOCK_WS_ENDPOINT = os.getenv('MSTOCK_WS_ENDPOINT', 'wss://ws.mstock.trade')
USE_WEBSOCKET = os.getenv('USE_WEBSOCKET', 'false').lower() == 'true'

# Account Configuration
MSTOCK_ACCOUNT = os.getenv('MSTOCK_ACCOUNT', 'default')
TOTP_ENABLED = os.getenv('TOTP_ENABLED', 'False').lower() == 'true'

config = DevelopmentConfig()
