#!/usr/bin/env python
"""
BPSAlgoAI - AI-Based Algorithmic Trading Automation
Main application entry point
"""
import logging
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info('Starting BPSAlgoAI Application...')
    
    # Create Flask application
    app = create_app('DevelopmentConfig')
    
    # Run the application
    logger.info('Running Flask server on http://localhost:5000')
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )
