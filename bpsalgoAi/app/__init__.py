from flask import Flask
from flask_cors import CORS

def create_app(config_name='DevelopmentConfig'):
    """Application factory"""
    import logging
    logger = logging.getLogger(__name__)
    app = Flask(__name__)
    CORS(app)
    try:
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
    except Exception as e:
        logger.error(f"Error during app initialization: {e}", exc_info=True)
        print(f"Error during app initialization: {e}")
        raise
    return app
