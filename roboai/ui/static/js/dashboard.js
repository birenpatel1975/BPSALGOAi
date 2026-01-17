// ROBOAi Trading Dashboard JavaScript

let socket;
let pnlChart;
let currentConfig = {};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    initializeEventListeners();
    initializeChart();
    loadInitialData();
});

// WebSocket Connection
function initializeWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });
    
    socket.on('status_update', function(data) {
        updateDashboard(data);
    });
    
    socket.on('config_updated', function(data) {
        console.log('Configuration updated:', data);
        updateConfigUI(data);
    });
    
    socket.on('platform_status', function(data) {
        console.log('Platform status changed:', data.status);
        updatePlatformStatus(data.status);
    });
}

// Event Listeners
function initializeEventListeners() {
    // Platform control
    document.getElementById('startBtn').addEventListener('click', startPlatform);
    document.getElementById('stopBtn').addEventListener('click', stopPlatform);
    
    // Trading mode
    document.getElementById('paperModeBtn').addEventListener('click', () => setTradingMode('paper'));
    document.getElementById('liveModeBtn').addEventListener('click', () => setTradingMode('live'));
    
    // Strategy mode
    document.getElementById('algoModeBtn').addEventListener('click', () => setStrategyMode('algo'));
    document.getElementById('manualModeBtn').addEventListener('click', () => setStrategyMode('manual'));
    
    // Config save
    document.getElementById('saveConfigBtn').addEventListener('click', saveConfiguration);
}

// Initialize Chart
function initializeChart() {
    const ctx = document.getElementById('pnlChart').getContext('2d');
    pnlChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'P&L',
                data: [],
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#9ca3af'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#9ca3af'
                    }
                }
            }
        }
    });
}

// API Calls
async function loadInitialData() {
    try {
        // Load status
        const statusRes = await fetch('/api/status');
        const statusData = await statusRes.json();
        if (statusData.success) {
            updateDashboard(statusData);
        }
        
        // Load config
        const configRes = await fetch('/api/config');
        const configData = await configRes.json();
        if (configData.success) {
            currentConfig = configData.config;
            updateConfigUI(currentConfig);
        }
        
        // Load trades
        loadTrades();
        
        // Load positions
        loadPositions();
        
        // Load PnL
        loadPnL();
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

async function startPlatform() {
    try {
        const response = await fetch('/api/platform/start', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showNotification('Platform started successfully', 'success');
            document.getElementById('startBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            updatePlatformStatusBadge('running');
        } else {
            showNotification(data.message || 'Failed to start platform', 'error');
        }
    } catch (error) {
        console.error('Error starting platform:', error);
        showNotification('Error starting platform', 'error');
    }
}

async function stopPlatform() {
    try {
        const response = await fetch('/api/platform/stop', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            showNotification('Platform stopped successfully', 'success');
            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            updatePlatformStatusBadge('stopped');
        } else {
            showNotification(data.message || 'Failed to stop platform', 'error');
        }
    } catch (error) {
        console.error('Error stopping platform:', error);
        showNotification('Error stopping platform', 'error');
    }
}

async function setTradingMode(mode) {
    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode: mode })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update UI
            document.getElementById('paperModeBtn').classList.toggle('active', mode === 'paper');
            document.getElementById('liveModeBtn').classList.toggle('active', mode === 'live');
            
            const description = mode === 'paper' 
                ? 'Safe testing environment - No real money'
                : '⚠️ LIVE TRADING - Real money at risk!';
            document.getElementById('modeDescription').textContent = description;
            
            showNotification(`Switched to ${mode.toUpperCase()} mode`, 'success');
        } else {
            showNotification('Failed to change trading mode', 'error');
        }
    } catch (error) {
        console.error('Error setting trading mode:', error);
        showNotification('Error changing trading mode', 'error');
    }
}

async function setStrategyMode(mode) {
    try {
        const isAlgo = mode === 'algo';
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ auto_trade: isAlgo })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Update UI
            document.getElementById('algoModeBtn').classList.toggle('active', isAlgo);
            document.getElementById('manualModeBtn').classList.toggle('active', !isAlgo);
            
            const description = isAlgo
                ? 'Automated trading with AI'
                : 'Manual trading - You control orders';
            document.getElementById('strategyDescription').textContent = description;
            
            showNotification(`Switched to ${mode.toUpperCase()} mode`, 'success');
        } else {
            showNotification('Failed to change strategy mode', 'error');
        }
    } catch (error) {
        console.error('Error setting strategy mode:', error);
        showNotification('Error changing strategy mode', 'error');
    }
}

async function saveConfiguration() {
    try {
        const config = {
            profit_lock_threshold: parseInt(document.getElementById('profitLockThreshold').value),
            trailing_sl: parseInt(document.getElementById('trailingSL').value),
            min_gain_target: parseInt(document.getElementById('minGainTarget').value),
            max_positions: parseInt(document.getElementById('maxPositions').value)
        };
        
        showNotification('Configuration saved successfully', 'success');
    } catch (error) {
        console.error('Error saving configuration:', error);
        showNotification('Error saving configuration', 'error');
    }
}

async function loadTrades() {
    try {
        const response = await fetch('/api/trades?limit=20');
        const data = await response.json();
        
        if (data.success && data.trades.length > 0) {
            updateTradesTable(data.trades);
        }
    } catch (error) {
        console.error('Error loading trades:', error);
    }
}

async function loadPositions() {
    try {
        const response = await fetch('/api/positions');
        const data = await response.json();
        
        if (data.success) {
            updatePositionsTable(data.positions);
        }
    } catch (error) {
        console.error('Error loading positions:', error);
    }
}

async function loadPnL() {
    try {
        const response = await fetch('/api/pnl');
        const data = await response.json();
        
        if (data.success) {
            updatePnLDisplay(data.current, data.summary);
        }
    } catch (error) {
        console.error('Error loading PnL:', error);
    }
}

// UI Update Functions
function updateConnectionStatus(connected) {
    const indicator = document.getElementById('connectionStatus');
    const text = document.getElementById('connectionText');
    
    if (connected) {
        indicator.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        indicator.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

function updateDashboard(data) {
    // Update agents
    if (data.agents) {
        updateAgentsGrid(data.agents);
    }
    
    // Update PnL
    if (data.pnl) {
        updatePnLDisplay(data.pnl);
    }
    
    // Update platform status
    if (data.platform_running !== undefined) {
        const status = data.platform_running ? 'running' : 'stopped';
        updatePlatformStatusBadge(status);
        document.getElementById('startBtn').disabled = data.platform_running;
        document.getElementById('stopBtn').disabled = !data.platform_running;
    }
    
    // Update last update time
    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
}

function updateConfigUI(config) {
    if (config.trading) {
        // Trading mode
        const isPaper = config.trading.mode === 'paper';
        document.getElementById('paperModeBtn').classList.toggle('active', isPaper);
        document.getElementById('liveModeBtn').classList.toggle('active', !isPaper);
        
        // Strategy mode
        const isAlgo = config.trading.auto_trade;
        document.getElementById('algoModeBtn').classList.toggle('active', isAlgo);
        document.getElementById('manualModeBtn').classList.toggle('active', !isAlgo);
    }
    
    if (config.strategy) {
        document.getElementById('profitLockThreshold').value = config.strategy.profit_lock_threshold || 500;
        document.getElementById('trailingSL').value = config.strategy.trailing_sl_percent || 20;
    }
}

function updateAgentsGrid(agents) {
    const grid = document.getElementById('agentsGrid');
    grid.innerHTML = '';
    
    for (const [name, status] of Object.entries(agents)) {
        const card = document.createElement('div');
        card.className = 'agent-card' + (status.is_running ? ' running' : '');
        card.innerHTML = `
            <div class="agent-name">${name}</div>
            <div class="agent-status">${status.status}</div>
        `;
        grid.appendChild(card);
    }
}

function updatePnLDisplay(pnl, summary) {
    const dailyPnL = pnl.daily_pnl || 0;
    const totalPnL = pnl.total_pnl || 0;
    const realizedPnL = pnl.realized_pnl || 0;
    const unrealizedPnL = pnl.unrealized_pnl || 0;
    
    updatePnLValue('dailyPnL', dailyPnL);
    updatePnLValue('totalPnL', totalPnL);
    updatePnLValue('realizedPnL', realizedPnL);
    updatePnLValue('unrealizedPnL', unrealizedPnL);
}

function updatePnLValue(elementId, value) {
    const element = document.getElementById(elementId);
    element.textContent = `₹${value.toFixed(2)}`;
    element.classList.remove('positive', 'negative');
    element.classList.add(value >= 0 ? 'positive' : 'negative');
}

function updatePositionsTable(positions) {
    const tbody = document.getElementById('positionsBody');
    
    if (positions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="no-data">No active positions</td></tr>';
        return;
    }
    
    tbody.innerHTML = positions.map(pos => `
        <tr>
            <td>${pos.symbol}</td>
            <td>${pos.quantity}</td>
            <td>₹${pos.avg_price.toFixed(2)}</td>
            <td>₹${(pos.current_price || 0).toFixed(2)}</td>
            <td class="${(pos.pnl || 0) >= 0 ? 'positive' : 'negative'}">₹${(pos.pnl || 0).toFixed(2)}</td>
            <td>${pos.status}</td>
        </tr>
    `).join('');
}

function updateTradesTable(trades) {
    const tbody = document.getElementById('tradesBody');
    
    if (trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="no-data">No recent trades</td></tr>';
        return;
    }
    
    tbody.innerHTML = trades.map(trade => `
        <tr>
            <td>${new Date(trade.entry_time).toLocaleString()}</td>
            <td>${trade.symbol}</td>
            <td>${trade.side}</td>
            <td>${trade.quantity}</td>
            <td>₹${trade.entry_price.toFixed(2)}</td>
            <td>${trade.exit_price ? '₹' + trade.exit_price.toFixed(2) : '-'}</td>
            <td class="${(trade.pnl || 0) >= 0 ? 'positive' : 'negative'}">${trade.pnl ? '₹' + trade.pnl.toFixed(2) : '-'}</td>
            <td>${trade.status}</td>
        </tr>
    `).join('');
}

function updatePlatformStatusBadge(status) {
    const badge = document.getElementById('platformStatus');
    badge.textContent = status === 'running' ? 'Running' : 'Stopped';
    badge.classList.toggle('running', status === 'running');
}

function showNotification(message, type = 'info') {
    // Simple notification - can be enhanced with a proper notification library
    console.log(`[${type.toUpperCase()}] ${message}`);
    alert(message);
}

// Refresh data periodically
setInterval(() => {
    if (document.visibilityState === 'visible') {
        loadTrades();
        loadPositions();
        loadPnL();
    }
}, 10000); // Refresh every 10 seconds
