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
    import os
    try:
        logger.info('Starting BPSAlgoAI Application...')
        # Print environment variables for debugging
        print('--- ENVIRONMENT VARIABLES ---')
        for k, v in os.environ.items():
            print(f'{k}={v}')
        print('-----------------------------')
        # Create Flask application
        app = create_app('DevelopmentConfig')
        # Run the application
        logger.info('Running Flask server on http://localhost:5000')
        app.run(
            host='0.0.0.0',
            port=5050,
            debug=True,
            use_reloader=False
        )
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        print(f"Fatal error in main: {e}")
        import traceback
        traceback.print_exc()
