"""Flask Web API for ROBOAi Trading Platform"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import asyncio
import threading
from typing import Optional
from pathlib import Path

from ..utils import get_config, get_logger, get_database
from ..main import ROBOAiPlatform

# Global instances
app = Flask(__name__, static_folder='../ui/static', template_folder='../ui/templates')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

logger = get_logger("WebAPI")
config = get_config()
database = get_database()
platform: Optional[ROBOAiPlatform] = None
platform_thread: Optional[threading.Thread] = None


def create_app():
    """Create and configure Flask app"""
    return app


@app.route('/')
def index():
    """Serve the dashboard"""
    return send_from_directory(app.template_folder, 'dashboard.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get platform status"""
    try:
        if platform and platform.agent_manager:
            agents_status = {}
            for name in platform.agent_manager.list_agents():
                agent = platform.agent_manager.get_agent(name)
                if agent:
                    agents_status[name] = {
                        'is_running': agent.is_running,
                        'status': agent.status,
                        'last_update': agent.last_update.isoformat() if agent.last_update else None
                    }
            
            # Get PnL if execution agent exists
            pnl_data = {}
            if platform.execution_agent:
                pnl_data = platform.execution_agent.get_pnl()
            
            return jsonify({
                'success': True,
                'platform_running': platform is not None and not platform._shutdown,
                'agents': agents_status,
                'pnl': pnl_data,
                'config': {
                    'mode': config.get('trading.mode'),
                    'auto_trade': config.get('trading.auto_trade'),
                    'max_positions': config.get('trading.max_positions'),
                }
            })
        else:
            return jsonify({
                'success': True,
                'platform_running': False,
                'agents': {},
                'pnl': {},
                'config': {
                    'mode': config.get('trading.mode'),
                    'auto_trade': config.get('trading.auto_trade'),
                }
            })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config_api():
    """Get current configuration"""
    try:
        return jsonify({
            'success': True,
            'config': {
                'trading': {
                    'mode': config.get('trading.mode'),
                    'auto_trade': config.get('trading.auto_trade'),
                    'min_gain_target': config.get('trading.min_gain_target'),
                    'max_positions': config.get('trading.max_positions'),
                    'stop_loss_percent': config.get('trading.stop_loss_percent'),
                    'target_profit_percent': config.get('trading.target_profit_percent'),
                },
                'risk': {
                    'max_daily_loss': config.get('risk.max_daily_loss'),
                    'max_position_size': config.get('risk.max_position_size'),
                    'circuit_breaker_enabled': config.get('risk.circuit_breaker_enabled'),
                },
                'strategy': {
                    'trailing_sl_percent': config.get('strategy.trailing_sl_percent', 20),
                    'profit_lock_threshold': config.get('strategy.profit_lock_threshold', 500),
                }
            }
        })
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['POST'])
def update_config_api():
    """Update configuration"""
    try:
        data = request.json
        
        # Update trading mode
        if 'mode' in data:
            config.set('trading.mode', data['mode'])
            logger.info(f"Trading mode changed to: {data['mode']}")
        
        # Update auto-trade
        if 'auto_trade' in data:
            config.set('trading.auto_trade', data['auto_trade'])
            logger.info(f"Auto-trade changed to: {data['auto_trade']}")
            
            # Update execution agent if running
            if platform and platform.execution_agent:
                platform.execution_agent.auto_trade = data['auto_trade']
        
        # Save configuration
        config.save_config()
        
        # Emit update to all connected clients
        socketio.emit('config_updated', {
            'mode': config.get('trading.mode'),
            'auto_trade': config.get('trading.auto_trade')
        })
        
        return jsonify({
            'success': True,
            'message': 'Configuration updated successfully'
        })
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/platform/start', methods=['POST'])
def start_platform():
    """Start the trading platform"""
    global platform, platform_thread
    
    try:
        if platform and not platform._shutdown:
            return jsonify({
                'success': False,
                'message': 'Platform is already running'
            }), 400
        
        # Create new platform instance
        platform = ROBOAiPlatform()
        
        # Run in separate thread
        def run_platform():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(platform.start())
            loop.close()
        
        platform_thread = threading.Thread(target=run_platform, daemon=True)
        platform_thread.start()
        
        logger.info("Platform started via web API")
        socketio.emit('platform_status', {'status': 'started'})
        
        return jsonify({
            'success': True,
            'message': 'Platform started successfully'
        })
    except Exception as e:
        logger.error(f"Error starting platform: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/platform/stop', methods=['POST'])
def stop_platform():
    """Stop the trading platform"""
    global platform
    
    try:
        if not platform or platform._shutdown:
            return jsonify({
                'success': False,
                'message': 'Platform is not running'
            }), 400
        
        # Trigger shutdown
        platform._shutdown = True
        
        logger.info("Platform stopped via web API")
        socketio.emit('platform_status', {'status': 'stopped'})
        
        return jsonify({
            'success': True,
            'message': 'Platform stopped successfully'
        })
    except Exception as e:
        logger.error(f"Error stopping platform: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get recent trades"""
    try:
        limit = request.args.get('limit', 50, type=int)
        status = request.args.get('status', None)
        
        trades = database.get_trades(status=status, limit=limit)
        
        return jsonify({
            'success': True,
            'trades': trades
        })
    except Exception as e:
        logger.error(f"Error getting trades: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get current positions"""
    try:
        if platform and platform.execution_agent:
            positions = platform.execution_agent.get_positions()
            return jsonify({
                'success': True,
                'positions': positions
            })
        else:
            return jsonify({
                'success': True,
                'positions': []
            })
    except Exception as e:
        logger.error(f"Error getting positions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pnl', methods=['GET'])
def get_pnl():
    """Get PnL summary"""
    try:
        # Get from execution agent
        if platform and platform.execution_agent:
            pnl = platform.execution_agent.get_pnl()
        else:
            pnl = {'total_pnl': 0, 'daily_pnl': 0}
        
        # Get database summary
        db_summary = database.get_pnl_summary()
        
        return jsonify({
            'success': True,
            'current': pnl,
            'summary': db_summary
        })
    except Exception as e:
        logger.error(f"Error getting PnL: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected to WebSocket")
    emit('connected', {'message': 'Connected to ROBOAi Platform'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected from WebSocket")


# Background task to emit status updates
def background_status_updates():
    """Emit status updates periodically"""
    while True:
        try:
            if platform and platform.agent_manager:
                # Get status
                status_data = {
                    'platform_running': not platform._shutdown,
                    'agents': {}
                }
                
                for name in platform.agent_manager.list_agents():
                    agent = platform.agent_manager.get_agent(name)
                    if agent:
                        status_data['agents'][name] = {
                            'is_running': agent.is_running,
                            'status': agent.status
                        }
                
                # Get PnL
                if platform.execution_agent:
                    status_data['pnl'] = platform.execution_agent.get_pnl()
                
                socketio.emit('status_update', status_data)
            
            socketio.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Error in background status updates: {e}")
            socketio.sleep(10)


# Start background thread
socketio.start_background_task(background_status_updates)
