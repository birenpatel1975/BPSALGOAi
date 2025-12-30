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

# API Configuration
API_KEY = os.getenv('API_KEY', 'MAm4VlPS4JZKzr4x+pbxEZpaA2K0RA8YezG9r9QQ9O0=')
API_TYPE = os.getenv('API_TYPE', 'A')
MSTOCK_ACCOUNT = os.getenv('MSTOCK_ACCOUNT', 'default')
TOTP_ENABLED = os.getenv('TOTP_ENABLED', 'False').lower() == 'true'
MSTOCK_API_BASE_URL = os.getenv('MSTOCK_API_BASE_URL', 'https://api.mstock.com')

config = DevelopmentConfig()
