"""
Flask Routes and API Endpoints
"""
from flask import Blueprint, render_template, jsonify, request
from config import (
    MSTOCK_API_BASE_URL_A,
    API_KEY,
    MSTOCK_ACCOUNT,
    MSTOCK_WS_ENDPOINT
)
from app.mstock_auth import MStockAuth
from app.mstock_api import MStockAPI
from app.algo_agent import AlgoAgent
import logging
import os

logger = logging.getLogger(__name__)

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize Type A authentication with credentials from environment
mstock_auth = MStockAuth(
    api_key=API_KEY,
    base_url=MSTOCK_API_BASE_URL_A,
    username=os.getenv('MSTOCK_USERNAME', ''),
    password=os.getenv('MSTOCK_PASSWORD', '')
)

# Initialize Type A/B API client (will use access_token once authenticated)
mstock_api = MStockAPI(base_url=MSTOCK_API_BASE_URL_A, api_key=API_KEY, auth=mstock_auth)
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
    """Start the Algo Agent (accepts trade_mode: 'paper' or 'live' in JSON body)"""
    trade_mode = None
    try:
        if request.is_json:
            body = request.get_json()
            trade_mode = body.get('trade_mode')
    except Exception:
        trade_mode = None
    result = algo_agent.start(trade_mode=trade_mode)
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
    # === REVERTED TO ORIGINAL OTP/AUTH ENDPOINTS ===
    quote = mstock_api.get_symbol_quote(symbol)
    return jsonify(quote)


@api_bp.route('/market/ws', methods=['GET'])
def get_market_ws():
    """Return WebSocket URL for frontend to connect to real-time market data"""
    # WebSocket endpoint is not supported in REST API flow.
    return jsonify({'error': 'WebSocket endpoint is not supported in REST API flow. Please refer to mStock WebSocket documentation.'})


@api_bp.route('/auth/refresh', methods=['POST'])
def refresh_auth():
    """Attempt to refresh the Type A session using stored refresh token"""
    try:
        success = mstock_auth.refresh_session()
        return jsonify({
            'success': bool(success),
            'access_token_valid': mstock_auth.is_token_valid()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/auth/start', methods=['POST'])
def auth_start():
    """Trigger Type A login (step1) to send OTP to user via SMS/Email"""
    try:
        sent = mstock_auth.step1_login()
        if sent:
            return jsonify({'success': True, 'message': 'OTP sent. Check SMS/Email.'})
        # Add backend error details for debugging
        return jsonify({'success': False, 'message': 'Failed to send OTP. Check credentials or logs.', 'error': getattr(mstock_auth, 'last_error', None)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/auth/verify', methods=['POST'])
def auth_verify():
    """Verify OTP (step2) and obtain session token"""
    try:
        body = request.get_json() or {}
        otp = body.get('otp') or body.get('request_token')
        if not otp:
            return jsonify({'success': False, 'message': 'OTP required'}), 400

        ok = mstock_auth.step2_session_token(otp)
        # Add backend error details for debugging
        return jsonify({
            'success': bool(ok),
            'access_token_valid': mstock_auth.is_token_valid(),
            'error': getattr(mstock_auth, 'last_error', None)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== Account API ====================

@api_bp.route('/account/info', methods=['GET'])
def get_account_info():
    """Get account information"""
    account_info = mstock_api.get_account_info()
    return jsonify(account_info)


@api_bp.route('/watchlist', methods=['GET'])
def get_watchlist():
    """Get watchlist from mStock account (Type A API)"""
    try:
        watchlist = mstock_api.get_watchlist()
        return jsonify(watchlist)
    except Exception as e:
        logger.error(f"Error fetching watchlist: {e}")
        return jsonify({'success': False, 'error': str(e), 'data': []}), 500

@api_bp.route('/watchlist/tab/<tab>', methods=['GET'])
def get_watchlist_tab(tab):
    """Get stocks for a specific watchlist tab. Tab 1 is for Algo Agent, others are sector-based or user's mStock account."""
    try:
        # Tab 1: Algo Agent's Top 10
        if tab == 'algo_top10':
            return jsonify(mstock_api.get_watchlist_tab('algo_top10'))
        # Tab 2-7: Sectors or user's mStock account watchlist
        elif tab in mstock_api.SECTOR_STOCKS:
            return jsonify(mstock_api.get_watchlist_tab(tab))
        elif tab == 'user':
            # Replicate user's mStock account watchlist (authenticated)
            watchlist = mstock_api.get_watchlist()
            return jsonify(watchlist)
        else:
            return jsonify({'success': False, 'data': [], 'error': 'Invalid tab'})
    except Exception as e:
        logger.error(f"Error fetching watchlist tab {tab}: {e}")
        return jsonify({'success': False, 'data': [], 'error': str(e)})

@api_bp.route('/watchlist/tab/user', methods=['GET'])
def get_user_watchlist_tab():
    """Get the authenticated user's mStock account watchlist."""
    try:
        watchlist = mstock_api.get_watchlist()
        return jsonify(watchlist)
    except Exception as e:
        logger.error(f"Error fetching user watchlist tab: {e}")
        return jsonify({'success': False, 'data': [], 'error': str(e)})

# ==================== Configuration API ====================

@api_bp.route('/config', methods=['GET'])
def get_config():
    """Get API configuration (safe values only)"""
    try:
        logger.info(f"API_KEY: {API_KEY}")
        logger.info(f"MSTOCK_API_BASE_URL_A: {MSTOCK_API_BASE_URL_A}")
        logger.info(f"MSTOCK_ACCOUNT: {MSTOCK_ACCOUNT}")
        logger.info(f"MSTOCK_USERNAME: {os.getenv('MSTOCK_USERNAME')}")
        logger.info(f"MSTOCK_PASSWORD: {os.getenv('MSTOCK_PASSWORD')}")
        access_token_valid = mstock_auth.is_token_valid()
        critical_config_present = bool(API_KEY and MSTOCK_API_BASE_URL_A and MSTOCK_ACCOUNT and MSTOCK_WS_ENDPOINT)
        config = {
            'success': bool(access_token_valid and critical_config_present),
            'access_token_valid': access_token_valid,
            'ws_endpoint': None,
            'config_complete': critical_config_present
        }
        if access_token_valid and critical_config_present:
            ws_url = f"{MSTOCK_WS_ENDPOINT}?API_KEY={API_KEY}&ACCESS_TOKEN={mstock_auth.get_token()}"
            config['ws_endpoint'] = ws_url
        return jsonify(config)
    except Exception as e:
        logger.error(f"/api/config error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e), 'config': None}), 500
    try:
        body = request.get_json() or {}
        otp = body.get('otp') or body.get('request_token')
        logger.info(f"Received OTP for verification: {otp}")
        if not otp:
            logger.error("OTP not provided in request body")
            return jsonify({'success': False, 'message': 'OTP required'}), 400

        ok = mstock_auth.step2_session_token(otp)
        logger.info(f"OTP verification result: {ok}, access_token_valid: {mstock_auth.is_token_valid()}")
        ws_endpoint = None
        try:
            ws_endpoint = mstock_api.get_ws_url()
        except Exception as ws_ex:
            logger.error(f"Error getting ws_endpoint after OTP verify: {ws_ex}")
        return jsonify({
            'success': bool(ok),
            'access_token_valid': mstock_auth.is_token_valid(),
            'ws_endpoint': ws_endpoint
        })
    except Exception as e:
        logger.error(f"/api/auth/verify error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500
