from flask import Flask
from flask_cors import CORS

def create_app(config_name='DevelopmentConfig'):
    """Application factory"""
    app = Flask(__name__)

    import logging
    import os

    # Logging setup
    LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)
    LOG_FILE = os.path.join(LOG_DIR, 'app.log')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    CORS(app)
    
    # Load configuration
    if config_name == 'DevelopmentConfig':
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    elif config_name == 'ProductionConfig':
        from config import ProductionConfig
        app.config.from_object(ProductionConfig)
    else:
        from config import Config
        app.config.from_object(Config)
    
    # Register blueprints
    from app.routes import main_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    
    return app
