"""
Flask Routes and API Endpoints
"""
from flask import Blueprint, render_template, jsonify, request
from config import (
    MSTOCK_API_BASE_URL_A,
    MSTOCK_API_BASE_URL_M,
    API_KEY,
    MSTOCK_ACCOUNT
)
from app.mstock_auth import MStockAuth
from app.mstock_api import MStockAPI
from app.algo_agent import AlgoAgent
import logging

logger = logging.getLogger(__name__)

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize Type A auth (JWT token retrieval)
mstock_auth = MStockAuth(api_key=API_KEY, base_url=MSTOCK_API_BASE_URL_A)
jwt_token = mstock_auth.get_token()

# Initialize Type M API (market data) with JWT token
mstock_api = MStockAPI(base_url=MSTOCK_API_BASE_URL_M, jwt_token=jwt_token, api_key=API_KEY)
algo_agent = AlgoAgent(mstock_api)

# ==================== Main Routes ====================

@main_bp.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'bpsalgoAi',
        'version': '1.0.0'
    })

# ==================== Algo Agent API ====================

@api_bp.route('/algo/start', methods=['POST'])
def start_algo():
    """Start the Algo Agent"""
    result = algo_agent.start()
    return jsonify(result)

@api_bp.route('/algo/stop', methods=['POST'])
def stop_algo():
    """Stop the Algo Agent"""
    result = algo_agent.stop()
    return jsonify(result)

@api_bp.route('/algo/status', methods=['GET'])
def algo_status():
    """Get Algo Agent status"""
    status = algo_agent.get_status()
    return jsonify(status)

# ==================== Market Data API ====================

@api_bp.route('/market/live', methods=['GET'])
def get_live_data():
    """Get live market data"""
    symbols = request.args.getlist('symbols')
    if not symbols:
        symbols = None
    data = mstock_api.get_live_data(symbols)
    return jsonify(data)

@api_bp.route('/market/quote/<symbol>', methods=['GET'])
def get_quote(symbol):
    """Get quote for a symbol"""
    quote = mstock_api.get_symbol_quote(symbol)
    return jsonify(quote)

# ==================== Account API ====================

@api_bp.route('/account/info', methods=['GET'])
def get_account_info():
    """Get account information"""
    account_info = mstock_api.get_account_info()
    return jsonify(account_info)

# ==================== Configuration API ====================

@api_bp.route('/config', methods=['GET'])
def get_config():
    """Get API configuration (safe values only)"""
    return jsonify({
        'type_a_api_configured': bool(API_KEY),
        'type_m_api_configured': bool(API_KEY),
        'type_a_base_url': MSTOCK_API_BASE_URL_A,
        'type_m_base_url': MSTOCK_API_BASE_URL_M,
        'mstock_account': MSTOCK_ACCOUNT,
        'jwt_token_valid': mstock_auth.is_token_valid()
    })

# ==================== Error Handlers ====================

@main_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500
