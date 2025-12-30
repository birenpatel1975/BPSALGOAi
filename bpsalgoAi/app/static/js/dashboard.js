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
const wsToggle = document.getElementById('wsToggle');
const wsStatus = document.getElementById('wsStatus');
const wsConnectBtn = document.getElementById('wsConnectBtn');
const wsDisconnectBtn = document.getElementById('wsDisconnectBtn');
const sendOtpBtn = document.getElementById('sendOtpBtn');
const verifyOtpBtn = document.getElementById('verifyOtpBtn');
const otpInput = document.getElementById('otpInput');
const authStatus = document.getElementById('authStatus');
const watchlistData = document.getElementById('watchlistData');
const refreshWatchlistBtn = document.getElementById('refreshWatchlistBtn');

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
    // Restore WS toggle preference
    try {
        const pref = localStorage.getItem('ws_enabled');
        if (pref === null) {
            // default to enabled if access token present
            wsToggle.checked = true;
        } else {
            wsToggle.checked = pref === 'true';
        }
    } catch (e) {
        console.warn('localStorage not available', e);
    }

    // Set up WS controls
    wsToggle.addEventListener('change', (e) => {
        try { localStorage.setItem('ws_enabled', e.target.checked); } catch (err) {}
        if (e.target.checked) {
            initWebSocketIfConfigured();
        } else {
            closeWebSocket();
            updateWsStatus('disabled');
        }
    });

    wsConnectBtn.addEventListener('click', () => initWebSocketIfConfigured(true));
    wsDisconnectBtn.addEventListener('click', () => { closeWebSocket(); updateWsStatus('disconnected'); });

    // Initialize WS if configured and toggle enabled
    initWebSocketIfConfigured();
    // Auth controls
    if (sendOtpBtn) sendOtpBtn.addEventListener('click', sendOtp);
    if (verifyOtpBtn) verifyOtpBtn.addEventListener('click', verifyOtp);
    // Watchlist controls
    if (refreshWatchlistBtn) refreshWatchlistBtn.addEventListener('click', refreshWatchlist);
    // Show initial auth status
    try {
        authStatus.textContent = cfg && cfg.access_token_valid ? 'Auth: valid' : 'Auth: not authenticated';
    } catch (e) {}
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

        console.log('WS config check:', { wsUrl, tokenValid, cfg });

        // Check user preference
        const enabled = wsToggle ? wsToggle.checked : true;

        // Block all WS attempts if not authenticated
        if (!tokenValid) {
            addLog('WebSocket blocked: OTP authentication required', 'warning');
            updateWsStatus('disconnected');
            closeWebSocket();
            return;
        }

        if (!enabled) {
            console.log('WebSocket disabled by user preference');
            updateWsStatus('disabled');
            return;
        }

        if (wsUrl && tokenValid) {
            console.log('Attempting WS connection to:', wsUrl);
            connectWebSocket(wsUrl);
        } else {
            console.warn('WebSocket not initialized', { wsUrl, tokenValid });
            addLog('WebSocket unavailable: token=' + (tokenValid ? 'valid' : 'invalid') + ', url=' + (wsUrl ? 'yes' : 'no'), 'warning');
            updateWsStatus('disconnected');
            closeWebSocket();
        }
    } catch (err) {
        console.warn('Error checking websocket config:', err);
        addLog('WS config fetch error: ' + err.message, 'error');
    }
}

// --- Auth helpers ---
async function sendOtp() {
    try {
        sendOtpBtn.disabled = true;
        addLog('Requesting OTP...', 'info');
        const resp = await fetch(`${API_BASE}/auth/start`, { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
            addLog('OTP sent. Check SMS/Email.', 'success');
            authStatus.textContent = 'Auth: OTP sent';
        } else {
            addLog('Failed to send OTP: ' + (data.message || data.error), 'error');
            authStatus.textContent = 'Auth: send failed';
        }
    } catch (e) {
        addLog('Error requesting OTP: ' + e.message, 'error');
        authStatus.textContent = 'Auth: error';
    } finally {
        sendOtpBtn.disabled = false;
    }
}

async function verifyOtp() {
    try {
        const otp = otpInput.value && otpInput.value.trim();
        if (!otp) { addLog('Please enter OTP', 'warning'); return; }
        verifyOtpBtn.disabled = true;
        addLog('Verifying OTP...', 'info');

        const resp = await fetch(`${API_BASE}/auth/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ otp })
        });

        const data = await resp.json();
        if (data.success) {
            addLog('OTP verified, session established', 'success');
            authStatus.textContent = data.access_token_valid ? 'Auth: valid' : 'Auth: invalid';
            // refresh config and try WS
            await loadConfig();
            refreshWatchlist();
            initWebSocketIfConfigured(true);
        } else {
            addLog('OTP verification failed: ' + (data.message || data.error), 'error');
            authStatus.textContent = 'Auth: verify failed';
        }
    } catch (e) {
        addLog('Error verifying OTP: ' + e.message, 'error');
        authStatus.textContent = 'Auth: error';
    } finally {
        verifyOtpBtn.disabled = false;
    }
}

function updateWsStatus(state) {
    // states: connecting, connected, disconnected, disabled, error
    if (!wsStatus) return;
    wsStatus.className = 'ws-status ws-' + state;
    switch (state) {
        case 'connecting': wsStatus.textContent = 'WS: connecting'; break;
        case 'connected': wsStatus.textContent = 'WS: connected'; break;
        case 'disabled': wsStatus.textContent = 'WS: disabled'; break;
        case 'error': wsStatus.textContent = 'WS: error'; break;
        default: wsStatus.textContent = 'WS: disconnected';
    }
    // Button states
    if (wsConnectBtn && wsDisconnectBtn) {
        if (state === 'connected') {
            wsConnectBtn.disabled = true;
            wsDisconnectBtn.disabled = false;
        } else {
            wsConnectBtn.disabled = false;
            wsDisconnectBtn.disabled = true;
        }
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
        // Log URL components for debugging
        try {
            const urlObj = new URL(url);
            console.log('WebSocket URL components:', {
                protocol: urlObj.protocol,
                host: urlObj.host,
                pathname: urlObj.pathname,
                search: urlObj.search,
                apiKeyLength: (urlObj.searchParams.get('API_KEY') || '').length,
                tokenLength: (urlObj.searchParams.get('ACCESS_TOKEN') || '').length
            });
        } catch (e) {
            console.log('Could not parse WS URL as URL object:', e.message);
        }
        
        updateWsStatus('connecting');
        marketSocket = new WebSocket(url);

        // Heartbeat monitoring
        let heartbeatInterval = null;
        let heartbeatTimeout = null;
        let lastMessageTime = Date.now();

        function startHeartbeat() {
            // send ping every 20s
            heartbeatInterval = setInterval(() => {
                try { marketSocket.send(JSON.stringify({ type: 'ping' })); } catch (e) {}
                // set timeout to check for any message in 30s
                clearTimeout(heartbeatTimeout);
                heartbeatTimeout = setTimeout(() => {
                    const age = Date.now() - lastMessageTime;
                    if (age > 30000) {
                        console.warn('No WS messages seen recently, closing socket to reconnect');
                        marketSocket.close();
                    }
                }, 30000);
            }, 20000);
        }

        function stopHeartbeat() {
            if (heartbeatInterval) { clearInterval(heartbeatInterval); heartbeatInterval = null; }
            if (heartbeatTimeout) { clearTimeout(heartbeatTimeout); heartbeatTimeout = null; }
        }

        marketSocket.onopen = () => {
            console.log('WebSocket connected');
            addLog('WebSocket connected', 'success');
            reconnectAttempts = 0;
            lastMessageTime = Date.now();
            startHeartbeat();
            updateWsStatus('connected');
            // Show ephemeral confirmation banner
            showConfirmation('WebSocket connected');
        };

        marketSocket.onmessage = (evt) => {
            lastMessageTime = Date.now();
            try {
                const payload = JSON.parse(evt.data);
                // handle simple pong
                if (payload && payload.type === 'pong') {
                    return;
                }

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
            console.log('WebSocket readyState:', marketSocket.readyState);
            addLog('WebSocket error (readyState=' + marketSocket.readyState + ')', 'error');
            updateWsStatus('error');
        };

        marketSocket.onclose = (evt) => {
            console.warn('WebSocket closed', { code: evt.code, reason: evt.reason, wasClean: evt.wasClean });
            addLog('WebSocket disconnected (code=' + evt.code + ', reason=' + (evt.reason || 'none') + ')', 'warning');
            stopHeartbeat();
            updateWsStatus('disconnected');
            attemptReconnect(url);
        };

    } catch (e) {
        console.error('Failed to create WebSocket', e);
        addLog('WebSocket creation failed', 'error');
        updateWsStatus('error');
        attemptReconnect(url);
    }
}

function showConfirmation(message, timeout = 3500) {
    try {
        const el = document.getElementById('confirmation');
        if (!el) return;
        el.textContent = message;
        el.style.display = 'block';
        setTimeout(() => { el.style.display = 'none'; }, timeout);
    } catch (e) {
        console.warn('Unable to show confirmation', e);
    }
}

// --- Watchlist support ---
async function refreshWatchlist() {
    try {
        refreshWatchlistBtn.disabled = true;
        addLog('Fetching watchlist...', 'info');
        const resp = await fetch(`${API_BASE}/watchlist`, { method: 'GET' });
        const data = await resp.json();

        if (data.success && data.data && Array.isArray(data.data)) {
            displayWatchlist(data.data);
            addLog('✅ Watchlist loaded (' + data.data.length + ' items)', 'success');
        } else if (data.data && Array.isArray(data.data) && data.data.length > 0) {
            displayWatchlist(data.data);
            addLog('✅ Watchlist loaded (' + data.data.length + ' items)', 'success');
        } else {
            addLog('⚠️ Watchlist empty or not available', 'warning');
            watchlistData.innerHTML = '<p class="placeholder">No watchlist items</p>';
        }
        refreshWatchlistBtn.disabled = false;
    } catch (e) {
        addLog('❌ Error fetching watchlist: ' + e.message, 'error');
        refreshWatchlistBtn.disabled = false;
    }
}

function displayWatchlist(items) {
    watchlistData.innerHTML = '';
    if (!items || items.length === 0) {
        watchlistData.innerHTML = '<p class="placeholder">No watchlist items</p>';
        return;
    }

    const table = document.createElement('table');
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    table.innerHTML = '<thead><tr><th style="border: 1px solid #ddd; padding: 8px; text-align: left;">Symbol</th><th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Price</th><th style="border: 1px solid #ddd; padding: 8px; text-align: right;">Change</th></tr></thead>';

    const tbody = document.createElement('tbody');
    items.forEach(item => {
        if (typeof item === 'string') {
            // Simple symbol string
            const row = document.createElement('tr');
            row.innerHTML = `<td style="border: 1px solid #ddd; padding: 8px;">${item}</td><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">-</td><td style="border: 1px solid #ddd; padding: 8px; text-align: right;">-</td>`;
            tbody.appendChild(row);
        } else if (typeof item === 'object' && item.symbol) {
            // Object with symbol, price, change
            const row = document.createElement('tr');
            const price = item.price || item.ltp || '-';
            const change = item.change || item.pchange || '-';
            const changeClass = change > 0 ? 'positive' : change < 0 ? 'negative' : '';
            row.innerHTML = `
                <td style="border: 1px solid #ddd; padding: 8px;">${item.symbol}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">${price}</td>
                <td style="border: 1px solid #ddd; padding: 8px; text-align: right; color: ${change > 0 ? 'green' : change < 0 ? 'red' : 'black'};">${change}</td>
            `;
            tbody.appendChild(row);
        }
    });
    table.appendChild(tbody);
    watchlistData.appendChild(table);
}

function attemptReconnect(url) {
    if (!wsToggle || !wsToggle.checked) {
        console.log('User disabled WebSocket; not attempting reconnect');
        return;
    }

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
