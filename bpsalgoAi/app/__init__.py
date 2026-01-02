from flask import Flask
from flask_cors import CORS

def create_app(config_name='DevelopmentConfig'):
    """Application factory"""
    app = Flask(__name__)

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
