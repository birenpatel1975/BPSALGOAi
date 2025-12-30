/**
 * Dashboard JavaScript
 * Handles interactions with the Flask backend API
 */

// API Base URL
const API_BASE = '/api';

// DOM Elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const refreshDataBtn = document.getElementById('refreshDataBtn');
const refreshAccountBtn = document.getElementById('refreshAccountBtn');
const agentStatus = document.getElementById('agentStatus');
const lastExecution = document.getElementById('lastExecution');
const tradeCount = document.getElementById('tradeCount');
const marketData = document.getElementById('marketData');
const accountInfo = document.getElementById('accountInfo');
const activityLog = document.getElementById('activityLog');
const configInfo = document.getElementById('configInfo');

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    
    // Set up event listeners
    startBtn.addEventListener('click', startAlgoAgent);
    stopBtn.addEventListener('click', stopAlgoAgent);
    refreshDataBtn.addEventListener('click', refreshMarketData);
    refreshAccountBtn.addEventListener('click', refreshAccountInfo);
    
    // Initial loads
    loadConfig();
    refreshAccountInfo();
    updateAgentStatus();
    
    // Auto-refresh agent status every 5 seconds
    setInterval(updateAgentStatus, 5000);
    
    // Auto-refresh market data every 10 seconds
    setInterval(refreshMarketData, 10000);
    // Initialize WS if configured
    initWebSocketIfConfigured();
});

/**
 * Start Algo Agent
 */
async function startAlgoAgent() {
    try {
        startBtn.disabled = true;
        addLog('Starting Algo Agent...', 'info');
        
        const response = await fetch(`${API_BASE}/algo/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            addLog('✅ Algo Agent started successfully', 'success');
            updateAgentStatus();
        } else {
            addLog('❌ Failed to start Algo Agent: ' + data.message, 'error');
        }
    } catch (error) {
        addLog('❌ Error starting Algo Agent: ' + error.message, 'error');
        startBtn.disabled = false;
    }
}

/**
 * Stop Algo Agent
 */
async function stopAlgoAgent() {
    try {
        stopBtn.disabled = true;
        addLog('Stopping Algo Agent...', 'info');
        
        const response = await fetch(`${API_BASE}/algo/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            addLog('✅ Algo Agent stopped successfully', 'success');
            updateAgentStatus();
        } else {
            addLog('❌ Failed to stop Algo Agent: ' + data.message, 'error');
        }
    } catch (error) {
        addLog('❌ Error stopping Algo Agent: ' + error.message, 'error');
        stopBtn.disabled = false;
    }
}

/**
 * Update Algo Agent Status
 */
async function updateAgentStatus() {
    try {
        const response = await fetch(`${API_BASE}/algo/status`, {
            method: 'GET'
        });
        
        const data = await response.json();
        
        // Update status display
        const statusLower = data.status.toLowerCase();
        agentStatus.textContent = data.status;
        agentStatus.className = 'status-value status-' + statusLower;
        
        // Update last execution
        if (data.last_execution) {
            const date = new Date(data.last_execution);
            lastExecution.textContent = date.toLocaleString();
        } else {
            lastExecution.textContent = '-';
        }
        
        // Update trade count
        tradeCount.textContent = data.trade_count;
        
        // Update button states
        if (data.is_running) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
        } else {
            startBtn.disabled = false;
            stopBtn.disabled = true;
        }
        
        // Add recent logs
        if (data.recent_logs && data.recent_logs.length > 0) {
            data.recent_logs.forEach(log => {
                // Only add if not already in log
                if (!activityLog.textContent.includes(log)) {
                    addLog(log, 'info');
                }
            });
        }
        
    } catch (error) {
        console.error('Error updating agent status:', error);
    }
}

/**
 * Refresh Market Data
 */
async function refreshMarketData() {
    try {
        refreshDataBtn.disabled = true;
        addLog('Fetching live market data...', 'info');
        
        const response = await fetch(`${API_BASE}/market/live`, {
            method: 'GET'
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayMarketData(data.data);
            addLog('✅ Market data loaded', 'success');
        } else {
            addLog('⚠️ Failed to load market data: ' + (data.error || 'Unknown error'), 'warning');
            // Display mock data on error
            if (data.data) {
                displayMarketData(data.data);
            }
        }
        
        refreshDataBtn.disabled = false;
    } catch (error) {
        addLog('❌ Error fetching market data: ' + error.message, 'error');
        refreshDataBtn.disabled = false;
    }
}

/**
 * Display Market Data
 */
function displayMarketData(data) {
    marketData.innerHTML = '';
    
    if (data && data.symbols && Array.isArray(data.symbols)) {
        data.symbols.forEach(symbol => {
            const item = document.createElement('div');
            item.className = 'market-item';
            
            const change = parseFloat(symbol.change) || 0;
            const changeClass = change > 0 ? 'positive' : change < 0 ? 'negative' : '';
            const changeSign = change > 0 ? '+' : '';
            
            item.innerHTML = `
                <div class="market-item-symbol">${symbol.symbol}</div>
                <div class="market-item-price">$${parseFloat(symbol.price).toFixed(2)}</div>
                <div class="market-item-change ${changeClass}">${changeSign}${change.toFixed(2)}%</div>
            `;
            
            marketData.appendChild(item);
        });
    } else {
        marketData.innerHTML = '<p class="placeholder">No market data available</p>';
    }
}

/**
 * Refresh Account Information
 */
async function refreshAccountInfo() {
    try {
        const response = await fetch(`${API_BASE}/account/info`, {
            method: 'GET'
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayAccountInfo(data.data);
            addLog('✅ Account info updated', 'success');
        } else {
            addLog('⚠️ Failed to load account info', 'warning');
            // Display mock data on error
            if (data.data) {
                displayAccountInfo(data.data);
            }
        }
        
    } catch (error) {
        addLog('❌ Error fetching account info: ' + error.message, 'error');
    }
}

/**
 * Display Account Information
 */
function displayAccountInfo(data) {
    accountInfo.innerHTML = '';
    
    if (data) {
        for (const [key, value] of Object.entries(data)) {
            const row = document.createElement('div');
            row.className = 'info-row';
            
            const displayKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            let displayValue = value;
            
            if (typeof value === 'number') {
                displayValue = typeof value === 'object' ? JSON.stringify(value) : value;
                if (key.includes('balance') || key.includes('power')) {
                    displayValue = '$' + parseFloat(value).toFixed(2);
                }
            }
            
            row.innerHTML = `
                <span class="info-label">${displayKey}</span>
                <span class="info-value">${displayValue}</span>
            `;
            
            accountInfo.appendChild(row);
        }
    } else {
        accountInfo.innerHTML = '<p class="placeholder">No account information available</p>';
    }
}

/**
 * Load Configuration
 */
async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`, {
            method: 'GET'
        });
        
        const data = await response.json();
        
        configInfo.innerHTML = '';
        for (const [key, value] of Object.entries(data)) {
            const item = document.createElement('div');
            item.className = 'config-item';
            
            const displayKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            let displayValue = value ? '✓ Configured' : '✗ Not configured';
            
            if (typeof value === 'string' || typeof value === 'boolean') {
                displayValue = value.toString();
            }
            
            item.innerHTML = `
                <span class="config-label">${displayKey}</span>
                <span class="config-value">${displayValue}</span>
            `;
            
            configInfo.appendChild(item);
        }
        
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

/**
 * Add Log Entry
 */
function addLog(message, type = 'info') {
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    
    const timestamp = new Date().toLocaleTimeString();
    entry.textContent = `[${timestamp}] ${message}`;
    
    activityLog.insertBefore(entry, activityLog.firstChild);
    
    // Keep only last 50 entries
    while (activityLog.children.length > 50) {
        activityLog.removeChild(activityLog.lastChild);
    }
}

// --- WebSocket support (connects to backend-provided WS URL) ---
// WebSocket variables
let marketSocket = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 6;

// Initialize WS if backend provides a URL & token is valid
async function initWebSocketIfConfigured() {
    try {
        const resp = await fetch(`${API_BASE}/config`, { method: 'GET' });
        const cfg = await resp.json();
        const wsUrl = cfg.ws_endpoint || null;
        const tokenValid = cfg.access_token_valid;

        if (wsUrl && tokenValid) {
            connectWebSocket(wsUrl);
        } else {
            console.warn('WebSocket not initialized: ws_url or token missing/invalid');
            closeWebSocket();
        }
    } catch (err) {
        console.warn('Error checking websocket config:', err);
    }
}

function connectWebSocket(url) {
    if (!url) return;
    if (marketSocket && (marketSocket.readyState === WebSocket.OPEN || marketSocket.readyState === WebSocket.CONNECTING)) {
        console.log('WebSocket already connected or connecting');
        return;
    }

    try {
        console.log('Connecting WebSocket to', url);
        marketSocket = new WebSocket(url);

        marketSocket.onopen = () => {
            console.log('WebSocket connected');
            addLog('WebSocket connected', 'success');
            reconnectAttempts = 0;
        };

        marketSocket.onmessage = (evt) => {
            try {
                const payload = JSON.parse(evt.data);
                if (payload && (payload.quotes || payload.data || payload.symbols)) {
                    if (payload.quotes) {
                        displayMarketData({ symbols: payload.quotes });
                    } else if (payload.data) {
                        displayMarketData({ symbols: payload.data });
                    } else if (payload.symbols) {
                        displayMarketData({ symbols: payload.symbols });
                    }
                } else {
                    addLog('WS: ' + JSON.stringify(payload), 'info');
                }
            } catch (e) {
                console.warn('Failed to parse WS message', e);
            }
        };

        marketSocket.onerror = (err) => {
            console.error('WebSocket error', err);
            addLog('WebSocket error', 'error');
        };

        marketSocket.onclose = (evt) => {
            console.warn('WebSocket closed', evt);
            addLog('WebSocket disconnected', 'warning');
            attemptReconnect(url);
        };

    } catch (e) {
        console.error('Failed to create WebSocket', e);
        attemptReconnect(url);
    }
}

function attemptReconnect(url) {
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        console.warn('Max WebSocket reconnect attempts reached');
        addLog('Max WebSocket reconnect attempts reached', 'error');
        return;
    }

    const delay = Math.min(30000, 1000 * Math.pow(2, reconnectAttempts));
    reconnectAttempts += 1;
    console.log(`Reconnecting WebSocket in ${delay}ms (attempt ${reconnectAttempts})`);
    setTimeout(() => connectWebSocket(url), delay);
}

function closeWebSocket() {
    if (marketSocket) {
        try {
            marketSocket.close();
        } catch (e) {
            console.warn('Error closing WebSocket', e);
        }
        marketSocket = null;
    }
}
