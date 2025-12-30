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

# mStock API Credentials and Base URLs
API_KEY = os.getenv('API_KEY', '')

# Type A: Primary API (login, session, orders, fund summary)
MSTOCK_API_BASE_URL_A = os.getenv('MSTOCK_API_BASE_URL_A', 'https://api.mstock.trade/openapi/typea')

# Type B: Secondary API (same endpoints, alternative for redundancy)
MSTOCK_API_BASE_URL_B = os.getenv('MSTOCK_API_BASE_URL_B', 'https://api.mstock.trade/openapi/typeb')

# WebSocket Configuration
MSTOCK_WS_ENDPOINT = os.getenv('MSTOCK_WS_ENDPOINT', 'wss://ws.mstock.trade')
USE_WEBSOCKET = os.getenv('USE_WEBSOCKET', 'false').lower() == 'true'

# Account Configuration
MSTOCK_ACCOUNT = os.getenv('MSTOCK_ACCOUNT', 'default')
TOTP_ENABLED = os.getenv('TOTP_ENABLED', 'false').lower() == 'true'

config = DevelopmentConfig()
