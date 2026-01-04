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
const watchlistData = document.getElementById('watchlistData') || document.getElementById('watchlistTabContent');
const refreshWatchlistBtn = document.getElementById('refreshWatchlistBtn');
const viewAlgoPicksBtn = document.getElementById('viewAlgoPicksBtn');
const paperTradeToggle = document.getElementById('paperTradeToggle');
const paperTradeLabel = document.getElementById('paperTradeLabel');
const summaryStatus = document.getElementById('summaryStatus');
const summaryTicker = document.getElementById('summaryTicker');
const summaryAction = document.getElementById('summaryAction');
const summaryWatchlist = document.getElementById('summaryWatchlist');
const tickerTextEl = document.getElementById('tickerText');
const opportunitiesTable = document.getElementById('opportunitiesTable');
const liveFeedEl = document.getElementById('liveFeed');
// Add backtest toggle
const backtestToggle = (() => {
    const existingToggle = document.getElementById('backtestToggle');
    if (existingToggle) {
        return existingToggle;
    }

    // Dynamically add if not present
    const algoControls = document.querySelector('.algo-controls');
    if (!algoControls) {
        return null;
    }

    const label = document.createElement('label');
    label.style.display = 'flex';
    label.style.alignItems = 'center';
    label.style.gap = '6px';
    label.style.fontWeight = '500';
    label.innerHTML = `<input type="checkbox" id="backtestToggle" style="accent-color: #f59e42; width: 18px; height: 18px;"> <span id="backtestLabel">Backtest</span>`;
    algoControls.appendChild(label);

    return document.getElementById('backtestToggle');
})();

const agentActivityText = document.getElementById('agentActivityText');

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
            // Auto-refresh for market movers (watchlist) page
            let watchlistInterval = null;
            function startWatchlistAutoRefresh() {
                if (watchlistInterval) clearInterval(watchlistInterval);
                watchlistInterval = setInterval(() => {
                    const watchlistSection = document.getElementById('watchlistSection');
                    if (watchlistSection && watchlistSection.style.display !== 'none') {
                        refreshCurrentWatchlistTab(true);
                    }
                }, 10000); // 10 seconds
            }
            function stopWatchlistAutoRefresh() {
                if (watchlistInterval) clearInterval(watchlistInterval);
                watchlistInterval = null;
            }
        // Navigation bar logic
        const navDashboard = document.getElementById('navDashboard');
        const navWatchlist = document.getElementById('navWatchlist');
        const authSection = document.querySelector('.auth-section');
        const mainSections = [
            document.querySelector('.auth-section'),
            document.getElementById('marketSection'),
            document.getElementById('accountSection'),
            document.getElementById('watchlistSection'),
            document.querySelector('.log-section'),
            document.querySelector('.config-section')
        ];

        function showDashboardPage() {
            // Show all main dashboard sections except watchlist
            mainSections.forEach(sec => {
                if (!sec) return;
                if (sec.id === 'watchlistSection') {
                    sec.style.display = 'none';
                } else {
                    sec.style.display = '';
                }
            });
            stopWatchlistAutoRefresh();
        }
        if (navDashboard) navDashboard.addEventListener('click', showDashboardPage);
        if (navWatchlist) navWatchlist.addEventListener('click', () => {
            window.open('/market-movers', '_blank');
        });
    console.log('Dashboard initialized');
    
    // Hide all sections except auth until authenticated
    setSectionsLocked(true);

    // Auth controls
    if (sendOtpBtn) sendOtpBtn.addEventListener('click', sendOtp);
    if (verifyOtpBtn) verifyOtpBtn.addEventListener('click', verifyOtp);

    // If this page has no auth UI (e.g., Market Movers standalone), unlock immediately
    if (!authSection) {
        setSectionsLocked(false);
        if (!window._sectionsUnlocked) {
            setupUnlockedSections();
            window._sectionsUnlocked = true;
        }
    }

    // Show initial auth status and hide auth section if already authenticated
    try {
        if (typeof cfg !== 'undefined' && cfg && cfg.access_token_valid) {
            if (authStatus) authStatus.textContent = 'Auth: valid';
            if (authSection) authSection.style.display = 'none';
            setSectionsLocked(false);
            if (!window._sectionsUnlocked) {
                setupUnlockedSections();
                window._sectionsUnlocked = true;
            }
        } else if (authStatus) {
            authStatus.textContent = 'Auth: not authenticated';
        }
    } catch (e) {}
});

function setSectionsLocked(locked) {
    const sections = [
        document.getElementById('marketSection'),
        document.getElementById('watchlistSection'),
        document.getElementById('accountSection')
    ];
    for (const sec of sections) {
        if (sec) sec.style.display = locked ? 'none' : '';
    }
    // Visually fade out market and account blocks if locked
    const marketSection = document.getElementById('marketSection');
    const accountSection = document.getElementById('accountSection');
    if (marketSection) marketSection.style.opacity = locked ? '0.5' : '1';
    if (accountSection) accountSection.style.opacity = locked ? '0.5' : '1';
    // Disable/enable buttons in those blocks
    if (refreshDataBtn) refreshDataBtn.disabled = locked;
    if (wsConnectBtn) wsConnectBtn.disabled = locked;
    if (wsDisconnectBtn) wsDisconnectBtn.disabled = locked;
    if (refreshAccountBtn) refreshAccountBtn.disabled = locked;
    // Also disable WS controls if locked
    if (locked) {
        if (typeof closeWebSocket === 'function') closeWebSocket();
        if (typeof updateWsStatus === 'function') updateWsStatus('disconnected');
    }
}


function setupUnlockedSections() {
    // Set up event listeners for unlocked sections
    if (startBtn) startBtn.addEventListener('click', startAlgoAgent);
    if (stopBtn) stopBtn.addEventListener('click', stopAlgoAgent);
    if (refreshDataBtn) refreshDataBtn.addEventListener('click', refreshMarketData);
    if (refreshAccountBtn) refreshAccountBtn.addEventListener('click', refreshAccountInfo);
    if (refreshWatchlistBtn) refreshWatchlistBtn.addEventListener('click', refreshWatchlist);
    // Paper/Live trade toggle logic
    if (paperTradeToggle && paperTradeLabel) {
        // Restore mode from localStorage
        const savedMode = localStorage.getItem('trade_mode');
        if (savedMode === 'live') {
            paperTradeToggle.checked = false;
            paperTradeLabel.textContent = 'Live Trade';
        } else {
            paperTradeToggle.checked = true;
            paperTradeLabel.textContent = 'Paper Trade';
        }
        paperTradeToggle.addEventListener('change', function() {
            if (paperTradeToggle.checked) {
                localStorage.setItem('trade_mode', 'paper');
                paperTradeLabel.textContent = 'Paper Trade';
                addLog('Switched to Paper Trade mode', 'info');
            } else {
                localStorage.setItem('trade_mode', 'live');
                paperTradeLabel.textContent = 'Live Trade';
                addLog('Switched to Live Trade mode', 'warning');
            }
        });
    }
    // Auto-refresh agent status every 5 seconds
    setInterval(updateAgentStatus, 5000);
    // Auto-refresh market data every 10 seconds
    setInterval(refreshMarketData, 10000);
    // WS controls
    if (wsToggle) {
        wsToggle.addEventListener('change', (e) => {
            try { localStorage.setItem('ws_enabled', e.target.checked); } catch (err) {}
            if (e.target.checked) {
                // Only connect if not already connected
                if (!marketSocket || marketSocket.readyState !== WebSocket.OPEN) {
                    addLog('Enabling live market feed (WebSocket)...', 'info');
                    initWebSocketIfConfigured();
                }
            } else {
                addLog('Disabling live market feed (WebSocket)...', 'info');
                closeWebSocket();
                updateWsStatus('disabled');
            }
        });
    }
    if (wsConnectBtn) wsConnectBtn.addEventListener('click', () => initWebSocketIfConfigured(true));
    if (wsDisconnectBtn) wsDisconnectBtn.addEventListener('click', () => { closeWebSocket(); updateWsStatus('disconnected'); });
    // Restore WS toggle preference and auto-connect
    try {
        if (wsToggle) {
            const pref = localStorage.getItem('ws_enabled');
            wsToggle.checked = pref === null ? true : pref === 'true';
            if (wsToggle.checked) initWebSocketIfConfigured();
        }
    } catch (e) {}
    // Initial loads
    loadConfig();
    refreshAccountInfo();
    updateAgentStatus();

    if (viewAlgoPicksBtn) {
        viewAlgoPicksBtn.addEventListener('click', () => {
            const oppTable = document.getElementById('opportunitiesTable');
            if (oppTable) {
                oppTable.scrollIntoView({ behavior: 'smooth', block: 'center' });
                oppTable.classList.add('flash-border');
                setTimeout(() => oppTable.classList.remove('flash-border'), 1600);
            }
        });
    }
}

/**
 * Start Algo Agent
 */
async function startAlgoAgent() {
    try {
        if (startBtn) startBtn.disabled = true;
        // Reset agent status for new session (preserve activity log history)
        if (agentStatus) {
            agentStatus.textContent = 'STARTING...';
            agentStatus.className = 'status-value';
        }
        if (lastExecution) lastExecution.textContent = '-';
        if (tradeCount) tradeCount.textContent = '0';
        if (activityLog) activityLog.innerHTML = '';
        addLog('Starting Algo Agent. The system will now scan for top stocks and begin trading automatically.', 'info');
        // Determine trade mode from toggles
        let trade_mode = 'paper';
        if (backtestToggle && backtestToggle.checked) {
            trade_mode = 'backtest';
        } else if (paperTradeToggle && !paperTradeToggle.checked) {
            trade_mode = 'live';
        }
        const response = await fetch(`${API_BASE}/algo/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ trade_mode })
        });
        const data = await response.json();
        if (data.success) {
            addLog(
                '✅ Algo Agent started in ' +
                (trade_mode === 'live'
                    ? 'LIVE'
                    : trade_mode === 'backtest'
                        ? 'BACKTEST'
                        : 'PAPER') +
                ' mode',
                'success'
            );
            // Flip to live interactive page with feed and picks
            window.location.hash = '#live';
            const dashboardTabs = document.getElementById('dashboardTabs');
            const marketMoversPage = document.getElementById('marketMoversPage');
            if (dashboardTabs) dashboardTabs.style.display = 'none';
            if (marketMoversPage) marketMoversPage.style.display = 'block';
            // Auto-select Algo Top 10 tab and trigger live feed refresh
            const watchlistTabs = document.querySelectorAll('.watchlist-tab');
            watchlistTabs.forEach(btn => {
                btn.classList.remove('active');
            });
            const top10Btn = document.querySelector('.watchlist-tab[data-tab="algo_top10"]');
            if (top10Btn) {
                top10Btn.classList.add('active');
                setActiveWatchlistTab('algo_top10');
            }
            addLog('Agent started, flipped to live page and loaded Algo Top 10 tab.', 'info');
        } else {
            addLog('❌ Failed to start Algo Agent: ' + data.message, 'error');
        }
        updateAgentStatus();
    } catch (error) {
        addLog('❌ Error starting Algo Agent: ' + error.message, 'error');
    } finally {
        startBtn.disabled = false;
    }
}

/**
 * Stop Algo Agent
 */
async function stopAlgoAgent() {
    try {
        stopBtn.disabled = true;
        addLog('Stopping Algo Agent. All trading actions will be paused.', 'warning');
        const response = await fetch(`${API_BASE}/algo/stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const data = await response.json();
        if (data.success) {
            addLog('✅ Algo Agent stopped successfully', 'success');
        } else {
            addLog('❌ Failed to stop Algo Agent: ' + data.message, 'error');
        }
        updateAgentStatus();
    } catch (error) {
        addLog('❌ Error stopping Algo Agent: ' + error.message, 'error');
    } finally {
        stopBtn.disabled = false;
    }
}

/**
 * Update Algo Agent Status
 */
async function updateAgentStatus() {
    try {
        const response = await fetch(`${API_BASE}/algo/status`, { method: 'GET' });
        const data = await response.json();
        if (data) {
            if (agentStatus) {
                agentStatus.textContent = data.status || '-';
                agentStatus.className = 'status-value ' + (data.status === 'RUNNING' ? 'status-running' : 'status-stopped');
            }
            if (lastExecution) lastExecution.textContent = data.last_execution ? formatDateTime(data.last_execution) : '-';
            if (tradeCount) tradeCount.textContent = data.trade_count || '0';
            // Show logs
            if (data.logs && Array.isArray(data.logs) && activityLog) {
                activityLog.innerHTML = '';
                data.logs.forEach(log => addLog(log, 'info'));
            }
            // Show live stats (top right)
            const liveStatsContent = document.getElementById('liveStatsContent');
            if (liveStatsContent && data.stats) {
                liveStatsContent.innerHTML =
                    `<span style='color:#f59e42;font-weight:600;'>Backtest</span><br>` +
                    `Best: <b>${data.stats.best_symbol || '-'}</b> (${data.stats.best_return || 0}% return)<br>` +
                    `Trades: <b>${data.stats.trades || 0}</b> &nbsp; P&amp;L: <b>${data.stats.pnl || 0}</b>`;
            } else if (liveStatsContent) {
                liveStatsContent.innerHTML = '';
            }

            // Update button states
            if (startBtn && stopBtn) {
                if (data.is_running) {
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                } else {
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                }
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

            // Update live panels from status payload
            renderAlgoLivePanels(data);
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
        if (refreshDataBtn) refreshDataBtn.disabled = true;
        addLog('Fetching live market data...', 'info');
        // Fetch with default symbols
        const response = await fetch(`${API_BASE}/market/live`, {
            method: 'GET'
        });
        const data = await response.json();
        console.log('Market data response:', data);
        if (data.success) {
            displayMarketData(data.data);
            addLog('✅ Market data loaded', 'success');
        } else {
            console.warn('Market data fetch failed:', data);
            addLog('⚠️ Failed to load market data: ' + (data.error || 'Unknown error'), 'warning');
            // Display mock data on error
            if (data.data) {
                displayMarketData(data.data);
            }
        }
        if (refreshDataBtn) refreshDataBtn.disabled = false;
    } catch (error) {
        addLog('❌ Error fetching market data: ' + error.message, 'error');
        if (refreshDataBtn) refreshDataBtn.disabled = false;
    }
}

/**
 * Display Market Data
 */
function displayMarketData(data) {
    if (!marketData) return;
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
        // Only show minimal config info
        const minimalKeys = ['success', 'access_token_valid', 'ws_endpoint'];
        minimalKeys.forEach(key => {
            if (!(key in data)) return;
            const item = document.createElement('div');
            item.className = 'config-item';
            let displayKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            let displayValue = data[key];
            if (key === 'ws_endpoint' && typeof displayValue === 'string') {
                // Truncate long ws_endpoint for display
                displayValue = displayValue.length > 60 ? displayValue.slice(0, 60) + '...' : displayValue;
            }
            item.innerHTML = `
                <span class="config-label">${displayKey}</span>
                <span class="config-value">${displayValue}</span>
            `;
            configInfo.appendChild(item);
        });
        
    } catch (error) {
        console.error('Error loading config:', error);
    }
}

/**
 * Add Log Entry
 */
function addLog(message, type = 'info') {
    if (!activityLog) { console.log(message); return; }
    let color = '#fff';
    if (type === 'error') color = '#e53e3e';
    if (type === 'success') color = '#38a169';
    if (type === 'warning') color = '#f6ad55';
    if (type === 'info') color = '#3182ce';
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    entry.style.color = color;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    activityLog.appendChild(entry);
    activityLog.scrollTop = activityLog.scrollHeight;
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
            refreshCurrentWatchlistTab();
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
    refreshCurrentWatchlistTab(false, true);
}

async function refreshCurrentWatchlistTab(silent = false, logIt = false) {
    try {
        if (refreshWatchlistBtn && !silent) refreshWatchlistBtn.disabled = true;
        if (logIt && !silent) addLog('Refreshing watchlist tab...', 'info');
        await fetchWatchlistTab(currentWatchlistTab, { silent });
        if (logIt && !silent) addLog('✅ Watchlist refreshed', 'success');
    } catch (e) {
        if (logIt && !silent) addLog('❌ Error refreshing watchlist: ' + e.message, 'error');
    } finally {
        if (refreshWatchlistBtn && !silent) refreshWatchlistBtn.disabled = false;
    }
}

function displayWatchlist(items) {
    watchlistData.innerHTML = '';
    if (!items || items.length === 0) {
        watchlistData.innerHTML = '<p class="placeholder">No watchlist items</p>';
        return;
    }

    symbolMeta = {};

    // Sort by change ascending (gainers/losers)
    items = items.slice().sort((a, b) => {
        const ca = parseFloat(a.change || a.pchange || 0);
        const cb = parseFloat(b.change || b.pchange || 0);
        return ca - cb;
    });

    const table = document.createElement('table');
    table.style.width = '100%';
    table.style.borderCollapse = 'collapse';
    table.style.background = '#1e293b';
    table.style.fontSize = '1.05em';
    table.style.boxShadow = '0 2px 8px rgba(30,64,175,0.08)';
    table.innerHTML = `<thead style="background:#1e40af;"><tr>
        <th style="border: 1px solid #334155; padding: 8px; text-align: left; color:#fff;">Symbol</th>
        <th style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff;">Price</th>
        <th style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff;">Change (%)</th>
        <th style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff;">Open</th>
        <th style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff;">Close</th>
        <th style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff;">High</th>
        <th style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff;">Low</th>
        <th style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff;">Volume</th>
        <th style="border: 1px solid #334155; padding: 8px; text-align: center; color:#fff;">Trend</th>
    </tr></thead>`;

    const tbody = document.createElement('tbody');
    items.forEach(item => {
        if (typeof item === 'string') {
            // Simple symbol string
            const row = document.createElement('tr');
            row.innerHTML = `<td style="border: 1px solid #cbd5e1; padding: 8px;">${item}</td>` +
                '<td style="border: 1px solid #cbd5e1; padding: 8px; text-align: right;">-</td>'.repeat(7) +
                '<td style="border: 1px solid #cbd5e1; padding: 8px; text-align: center;">-</td>';
            tbody.appendChild(row);
        } else if (typeof item === 'object' && item.symbol) {
            const price = item.price || item.ltp || '-';
            let change = item.change || item.pchange || '-';
            const open = item.open || item.open_price || '-';
            const close = item.close || item.close_price || item.prevclose || '-';
            const high = item.high || item.high_price || '-';
            const low = item.low || item.low_price || '-';
            const volume = item.volume || item.vol || '-';
            let changeVal = parseFloat(change) || 0;
            // Show change as percent with 2 decimals
            if (change !== '-') {
                change = changeVal.toFixed(2) + '%';
            }
            const trend = changeVal > 0 ? '▲' : changeVal < 0 ? '▼' : '-';
            const trendColor = changeVal > 0 ? 'green' : changeVal < 0 ? 'red' : 'gray';
            const row = document.createElement('tr');
            row.innerHTML = `
                <td style="border: 1px solid #334155; padding: 8px; font-weight:600; color:#fff; background:#273449;">${item.symbol}</td>
                <td style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff; background:#273449;">${price}</td>
                <td style="border: 1px solid #334155; padding: 8px; text-align: right; color: ${trendColor}; font-weight:600; background:#273449;">${change}</td>
                <td style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff; background:#273449;">${open}</td>
                <td style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff; background:#273449;">${close}</td>
                <td style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff; background:#273449;">${high}</td>
                <td style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff; background:#273449;">${low}</td>
                <td style="border: 1px solid #334155; padding: 8px; text-align: right; color:#fff; background:#273449;">${volume}</td>
                <td style="border: 1px solid #334155; padding: 8px; text-align: center; color: ${trendColor}; font-size: 1.2em; font-weight: bold; background:#273449;">${trend}</td>
            `;
            tbody.appendChild(row);
        }
    });
    table.appendChild(tbody);
    watchlistData.appendChild(table);
}

// Watchlist tab logic
const watchlistTabs = document.querySelectorAll('.watchlist-tab');
const watchlistTabContent = document.getElementById('watchlistTabContent');
let currentWatchlistTab = 'algo_top10';

function setActiveWatchlistTab(tab) {
    watchlistTabs.forEach(btn => {
        if (btn.dataset.tab === tab) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    currentWatchlistTab = tab;
    fetchWatchlistTab(tab);
}

watchlistTabs.forEach(btn => {
    btn.addEventListener('click', () => {
        setActiveWatchlistTab(btn.dataset.tab);
    });
});

if (watchlistTabs && watchlistTabs.length) {
    setActiveWatchlistTab(currentWatchlistTab);
}

// Stock search and add functionality
// Load custom symbols from localStorage on page load
let customWatchlistSymbols = [];
try {
    const saved = localStorage.getItem('customWatchlistSymbols');
    if (saved) {
        customWatchlistSymbols = JSON.parse(saved);
        console.log('✅ Loaded custom symbols from localStorage:', customWatchlistSymbols);
    }
} catch (e) {
    console.warn('⚠️ Failed to load custom symbols from localStorage:', e);
}

const stockSearchInput = document.getElementById('stockSearchInput');
const addStockBtn = document.getElementById('addStockBtn');

if (addStockBtn && stockSearchInput) {
    addStockBtn.addEventListener('click', async () => {
        const symbol = stockSearchInput.value.trim().toUpperCase();
        if (!symbol) {
            console.log('Please enter a stock symbol');
            if (typeof addLog !== 'undefined') addLog('Please enter a stock symbol', 'warning');
            return;
        }

        // Check if already in default or custom watchlist
        const defaultSymbols = ['BANKNIFTY', 'FINNIFTY', 'GIFTNIFTY', 'NIFTY50', 'SENSEX'];
        if (defaultSymbols.includes(symbol) || customWatchlistSymbols.includes(symbol)) {
            console.log(`${symbol} is already in watchlist`);
            if (typeof addLog !== 'undefined') addLog(`${symbol} is already in watchlist`, 'warning');
            return;
        }

        console.log(`Adding ${symbol} to watchlist...`);
        if (typeof addLog !== 'undefined') addLog(`Adding ${symbol} to watchlist...`, 'info');
        
        try {
            // Fetch live data for this symbol to verify it exists
            const response = await fetch(`${API_BASE}/market/live?symbols=${encodeURIComponent(symbol)}`);
            const data = await response.json();
            
            console.log('Add stock response:', data);
            
            if (data.success && data.data && data.data.symbols && data.data.symbols.length > 0) {
                customWatchlistSymbols.push(symbol);
                customWatchlistSymbols.sort(); // Keep alphabetically sorted
                
                // Save to localStorage for persistence
                try {
                    localStorage.setItem('customWatchlistSymbols', JSON.stringify(customWatchlistSymbols));
                    console.log('💾 Saved custom symbols to localStorage');
                } catch (e) {
                    console.warn('⚠️ Failed to save to localStorage:', e);
                }
                
                stockSearchInput.value = '';
                console.log(`✅ Added ${symbol} to watchlist (total custom symbols: ${customWatchlistSymbols.length})`);
                if (typeof addLog !== 'undefined') addLog(`✅ Added ${symbol} to watchlist`, 'success');
                
                // Force immediate refresh
                console.log('Triggering immediate refresh after adding symbol...');
                await fetchAlgoWatchlist();
            } else {
                console.warn(`⚠️ Could not fetch data for ${symbol}`, data);
                if (typeof addLog !== 'undefined') addLog(`⚠️ Could not fetch data for ${symbol} (symbol may not exist)`, 'warning');
            }
        } catch (error) {
            console.error(`❌ Error adding ${symbol}:`, error);
            if (typeof addLog !== 'undefined') addLog(`❌ Error adding ${symbol}: ${error.message}`, 'error');
        }
    });

    // Allow Enter key to add stock
    stockSearchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addStockBtn.click();
        }
    });
}

// Handle authenticated user watchlist button
const authWatchlistBtn = document.getElementById('authWatchlistBtn');
if (authWatchlistBtn) {
    authWatchlistBtn.addEventListener('click', async () => {
        console.log('Loading authenticated user watchlist...');
        if (typeof addLog !== 'undefined') addLog('Loading authenticated user watchlist...', 'info');
        
        try {
            const response = await fetch(`${API_BASE}/watchlist/tab/user`);
            const data = await response.json();
            
            console.log('User watchlist response:', data);
            
            if (data.success && data.data && Array.isArray(data.data)) {
                // Sort alphabetically
                const sortedData = data.data.sort((a, b) => (a.symbol || '').localeCompare(b.symbol || ''));
                console.log(`✅ Loaded ${sortedData.length} symbols from user watchlist`);
                if (typeof addLog !== 'undefined') addLog(`✅ Loaded ${sortedData.length} symbols from user watchlist`, 'success');
                displayAlgoWatchlistTable(sortedData);
            } else if (data.data && data.data.symbols) {
                const sortedData = data.data.symbols.sort((a, b) => (a.symbol || '').localeCompare(b.symbol || ''));
                console.log(`✅ Loaded ${sortedData.length} symbols from user watchlist`);
                if (typeof addLog !== 'undefined') addLog(`✅ Loaded ${sortedData.length} symbols from user watchlist`, 'success');
                displayAlgoWatchlistTable(sortedData);
            } else {
                console.warn('No user watchlist data available - user may not be authenticated');
                if (typeof addLog !== 'undefined') addLog('No user watchlist available - please authenticate with OTP first', 'warning');
                if (watchlistTabContent) {
                    watchlistTabContent.innerHTML = `<p class="placeholder">No authenticated user watchlist available. Please authenticate with OTP first or use the default Algo Watchlist.</p>`;
                }
            }
        } catch (error) {
            console.error('Error loading user watchlist:', error);
            if (typeof addLog !== 'undefined') addLog(`Error loading user watchlist: ${error.message}`, 'error');
            if (watchlistTabContent) {
                watchlistTabContent.innerHTML = `<p class="placeholder">Error loading user watchlist: ${error.message}</p>`;
            }
        }
    });
}

function fetchWatchlistTab(tab, options = {}) {
    const silent = options.silent;
    if (!watchlistTabContent) {
        addLog('Watchlist content area not found. Please reload the page.', 'error');
        return;
    }

    if (tab === 'algo_top10') {
        if (!silent) {
            watchlistTabContent.innerHTML = '<p class="placeholder">Loading Algo watchlist...</p>';
        }
        return fetchAlgoWatchlist();
    }

    if (!silent) {
        watchlistTabContent.innerHTML = '<p class="placeholder">Loading...</p>';
    }
    let endpoint = `${API_BASE}/watchlist/tab/${tab}`;
    if (tab === 'user') {
        endpoint = `${API_BASE}/watchlist/tab/user`;
    }
    return fetch(endpoint)
        .then(res => res.json())
        .then(data => {
            console.log('Watchlist data received:', data);
            
            if (!data.success) {
                watchlistTabContent.innerHTML = `<p class="placeholder">Error loading tab: ${data.error || 'Unknown error'}</p>`;
                return;
            }
            
            if (!Array.isArray(data.data) || data.data.length === 0) {
                watchlistTabContent.innerHTML = '<p class="placeholder">No stocks found for this tab.</p>';
                return;
            }
            
            // Render a comprehensive table with all available data
            let html = `<table class="watchlist-table" style="width:100%; border-collapse:collapse;">
                <thead style="background:#1e40af; color:#fff;">
                    <tr>
                        <th style="padding:10px; text-align:left; border:1px solid #334155;">Symbol</th>
                        <th style="padding:10px; text-align:right; border:1px solid #334155;">Price</th>
                        <th style="padding:10px; text-align:right; border:1px solid #334155;">Change %</th>
                        <th style="padding:10px; text-align:right; border:1px solid #334155;">Open</th>
                        <th style="padding:10px; text-align:right; border:1px solid #334155;">High</th>
                        <th style="padding:10px; text-align:right; border:1px solid #334155;">Low</th>
                        <th style="padding:10px; text-align:right; border:1px solid #334155;">Close</th>
                        <th style="padding:10px; text-align:right; border:1px solid #334155;">Volume</th>
                    </tr>
                </thead>
                <tbody>`;
            
            data.data.forEach(stock => {
                const price = stock.price || stock.ltp || stock.close || '-';
                const change = parseFloat(stock.changepercent || stock.change || 0);
                const changeDisplay = change ? change.toFixed(2) + '%' : '-';
                const changeColor = change > 0 ? '#10b981' : change < 0 ? '#ef4444' : '#9ca3af';
                
                html += `<tr style="background:#0f172a; border-bottom:1px solid #334155;">
                    <td style="padding:10px; border:1px solid #334155; font-weight:600; color:#3b82f6;">${stock.symbol || '-'}</td>
                    <td style="padding:10px; border:1px solid #334155; text-align:right; color:#fff;">${formatPrice(price)}</td>
                    <td style="padding:10px; border:1px solid #334155; text-align:right; color:${changeColor}; font-weight:600;">${changeDisplay}</td>
                    <td style="padding:10px; border:1px solid #334155; text-align:right; color:#e2e8f0;">${formatPrice(stock.open || '-')}</td>
                    <td style="padding:10px; border:1px solid #334155; text-align:right; color:#e2e8f0;">${formatPrice(stock.high || '-')}</td>
                    <td style="padding:10px; border:1px solid #334155; text-align:right; color:#e2e8f0;">${formatPrice(stock.low || '-')}</td>
                    <td style="padding:10px; border:1px solid #334155; text-align:right; color:#e2e8f0;">${formatPrice(stock.close || '-')}</td>
                    <td style="padding:10px; border:1px solid #334155; text-align:right; color:#e2e8f0;">${formatVolume(stock.volume || '-')}</td>
                </tr>`;
            });
            
            html += '</tbody></table>';
            watchlistTabContent.innerHTML = html;
            
            // Attach click to rows to open chart
            watchlistTabContent.querySelectorAll('tbody tr').forEach(tr => {
                tr.style.cursor = 'pointer';
                tr.addEventListener('mouseenter', () => tr.style.background = '#1e293b');
                tr.addEventListener('mouseleave', () => tr.style.background = '#0f172a');
                tr.addEventListener('click', () => {
                    const sym = tr.children[0] ? tr.children[0].textContent : null;
                    if (sym) {
                        selectedSymbolMeta = { symbol: sym, price: tr.children[1] ? tr.children[1].textContent : null };
                        showMiniGraph(sym);
                    }
                });
            });
        })
        .catch(err => {
            if (watchlistTabContent) {
                watchlistTabContent.innerHTML = `<p class="placeholder">Error loading tab: ${err.message}</p>`;
            }
            addLog('Watchlist fetch failed: ' + err.message, 'error');
        });
}

// Helper function to format price
function formatPrice(val) {
    if (val === '-' || !val) return '-';
    const num = parseFloat(val);
    if (isNaN(num)) return '-';
    return num.toFixed(2);
}

// Helper function to format volume
function formatVolume(val) {
    if (val === '-' || !val) return '-';
    const num = parseFloat(val);
    if (isNaN(num)) return '-';
    if (num >= 10000000) return (num / 10000000).toFixed(1) + 'Cr';
    if (num >= 100000) return (num / 100000).toFixed(1) + 'L';
    return num.toString();
}

// --- Mini-graph logic ---
let miniGraph = null;
let miniGraphSymbol = null;
let miniGraphInterval = 1;
const miniGraphContainer = document.getElementById('miniGraphContainer');
const miniGraphCanvas = document.getElementById('miniGraph');
const miniGraphTitle = document.getElementById('miniGraphTitle');
const miniGraphIntervalSelect = document.getElementById('miniGraphInterval');
const miniGraphPlaceholder = document.getElementById('miniGraphPlaceholder');
const optionChainContent = document.getElementById('optionChainContent');
const openChartPage = document.getElementById('openChartPage');

let algoWatchlistFull = [];
let algoWatchlistShowMore = false;
let symbolMeta = {};
let selectedSymbolMeta = null;

function showMiniGraph(symbol) {
    if (!miniGraphCanvas) return; // Chart removed on some pages
    miniGraphSymbol = symbol;
    miniGraphInterval = miniGraphIntervalSelect ? parseInt(miniGraphIntervalSelect.value) : 1;
    const ltp = selectedSymbolMeta && selectedSymbolMeta.price ? selectedSymbolMeta.price : (selectedSymbolMeta && selectedSymbolMeta.ltp);
    miniGraphTitle.textContent = `Mini-Graph: ${symbol}${ltp ? ' @ ' + ltp : ''}`;
    if (miniGraphPlaceholder) miniGraphPlaceholder.textContent = '';
    miniGraphContainer.style.display = '';
    if (openChartPage) openChartPage.href = `/mini-graph?symbol=${encodeURIComponent(symbol)}`;
    fetchMiniGraphData();
    fetchOptionChain();
}

function fetchMiniGraphData() {
    if (!miniGraphSymbol || !miniGraphCanvas) return;
    fetch(`/api/algo/stock_graph/${miniGraphSymbol}?interval=${miniGraphInterval}`)
        .then(res => res.json())
        .then(data => {
            if (data.success && Array.isArray(data.data)) {
                renderMiniGraph(data.data);
            }
        });
}

function renderMiniGraph(data) {
    if (!miniGraphCanvas) return;
    const ctx = miniGraphCanvas.getContext('2d');
    if (miniGraph) miniGraph.destroy();
    const labels = data.map(d => d.time);
    const prices = data.map(d => d.price);
    // For demo, generate random volume and indicators
    const volumes = data.map(() => Math.floor(Math.random() * 1000 + 100));
    // Simple Bollinger Bands (mock)
    const sma = prices.map((_, i, arr) => arr.slice(Math.max(0, i-5), i+1).reduce((a,b)=>a+b,0)/(Math.min(i+1,6)));
    const std = prices.map((_, i, arr) => {
        const mean = sma[i];
        const slice = arr.slice(Math.max(0, i-5), i+1);
        return Math.sqrt(slice.reduce((a,b)=>a+(b-mean)**2,0)/slice.length);
    });
    const upper = sma.map((m,i)=>m+2*std[i]);
    const lower = sma.map((m,i)=>m-2*std[i]);
    // Mock ADX and Money Flow
    const adx = prices.map((_,i)=>50+10*Math.sin(i/10));
    const mfi = prices.map((_,i)=>50+20*Math.cos(i/15));
    miniGraph = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                { label: 'Price', data: prices, borderColor: '#1e40af', backgroundColor: 'rgba(30,64,175,0.1)', yAxisID: 'y' },
                { label: 'Upper Band', data: upper, borderColor: '#22d3ee', borderDash: [5,5], fill: false, yAxisID: 'y' },
                { label: 'Lower Band', data: lower, borderColor: '#f59e42', borderDash: [5,5], fill: false, yAxisID: 'y' },
                { label: 'ADX', data: adx, borderColor: '#f43f5e', fill: false, yAxisID: 'y2' },
                { label: 'MFI', data: mfi, borderColor: '#84cc16', fill: false, yAxisID: 'y2' },
                { label: 'Volume', data: volumes, type: 'bar', backgroundColor: 'rgba(16,185,129,0.3)', yAxisID: 'y3' }
            ]
        },
        options: {
            responsive: false,
            plugins: { legend: { display: true } },
            scales: {
                y: { type: 'linear', position: 'left', title: { display: true, text: 'Price' } },
                y2: { type: 'linear', position: 'right', title: { display: true, text: 'ADX/MFI' }, grid: { drawOnChartArea: false } },
                y3: { type: 'linear', position: 'right', title: { display: true, text: 'Volume' }, grid: { drawOnChartArea: false }, offset: true }
            }
        }
    });
}

function renderOptionChain(data) {
    if (!optionChainContent) return;
    if (!data || !data.data) {
        optionChainContent.innerHTML = '<p class="placeholder" style="padding:8px;">No option chain data.</p>';
        return;
    }
    const { atm = [], itm = [], otm = [] } = data.data;
    function pill(list, label) {
        if (!list || !list.length) return `<div class="option-pill"><strong>${label}</strong>n/a</div>`;
        return list.map(o => `<div class="option-pill"><strong>${label} ${o.type}</strong>Strike ${o.strike}<br>LTP ${o.ltp} | OI ${o.oi}</div>`).join('');
    }
    optionChainContent.innerHTML = `<div class="option-chain-grid">${pill(atm, 'ATM')}${pill(itm, 'ITM')}${pill(otm, 'OTM')}</div>`;
}

function fetchOptionChain() {
    if (!miniGraphSymbol || !optionChainContent) return;
    const ltp = selectedSymbolMeta && (selectedSymbolMeta.price || selectedSymbolMeta.ltp);
    const ltpParam = ltp ? `?ltp=${ltp}` : '';
    fetch(`/api/optionchain/data/OPTIDX/near/${miniGraphSymbol}${ltpParam}`)
        .then(res => res.json())
        .then(renderOptionChain)
        .catch(() => {
            if (optionChainContent) optionChainContent.innerHTML = '<p class="placeholder" style="padding:8px;">Option chain unavailable.</p>';
        });
}

if (miniGraphIntervalSelect) {
    miniGraphIntervalSelect.addEventListener('change', () => {
        miniGraphInterval = parseInt(miniGraphIntervalSelect.value);
        fetchMiniGraphData();
    });
}

// --- Watchlist table click handler ---
function displayAlgoWatchlistTable(stocks) {
    algoWatchlistFull = stocks || [];
    // Force alphabetical sort by symbol
    algoWatchlistFull.sort((a, b) => (a.symbol || '').localeCompare(b.symbol || ''));
    const rows = algoWatchlistShowMore ? algoWatchlistFull : algoWatchlistFull.slice(0, 20);
    
    let html = `<div class="watchlist-container" style="padding: 16px; background: #0f172a; border-radius: 8px; margin-top: 12px;">
        <table class="watchlist-table" style="width:100%; border-collapse:collapse; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
            <thead style="background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%); color: #fff; position: sticky; top: 0; z-index: 10;">
                <tr>
                    <th style="padding: 14px 12px; text-align: left; border: none; font-weight: 600; font-size: 13px; letter-spacing: 0.5px;">Symbol</th>
                    <th style="padding: 14px 12px; text-align: right; border: none; font-weight: 600; font-size: 13px; letter-spacing: 0.5px;">Current</th>
                    <th style="padding: 14px 12px; text-align: right; border: none; font-weight: 600; font-size: 13px; letter-spacing: 0.5px;">Change</th>
                    <th style="padding: 14px 12px; text-align: right; border: none; font-weight: 600; font-size: 13px; letter-spacing: 0.5px;">% Change</th>
                    <th style="padding: 14px 12px; text-align: right; border: none; font-weight: 600; font-size: 13px; letter-spacing: 0.5px;">Open</th>
                    <th style="padding: 14px 12px; text-align: right; border: none; font-weight: 600; font-size: 13px; letter-spacing: 0.5px;">High</th>
                    <th style="padding: 14px 12px; text-align: right; border: none; font-weight: 600; font-size: 13px; letter-spacing: 0.5px;">Low</th>
                    <th style="padding: 14px 12px; text-align: right; border: none; font-weight: 600; font-size: 13px; letter-spacing: 0.5px;">Volume</th>
                </tr>
            </thead>
            <tbody>`;
    
    rows.forEach((stock, index) => {
        symbolMeta[stock.symbol] = stock;
        const ltp = stock.price ?? stock.ltp ?? '-';
        
        // Calculate actual change amount
        const currentPrice = parseFloat(ltp);
        const previousClose = parseFloat(stock.close ?? stock.prev_close ?? stock.last_close ?? 0);
        const changeAmount = previousClose > 0 ? (currentPrice - previousClose) : 0;
        const changePercent = previousClose > 0 ? ((changeAmount / previousClose) * 100) : 0;
        
        const changeColor = changeAmount > 0 ? '#10b981' : changeAmount < 0 ? '#ef4444' : '#9ca3af';
        const changeSymbol = changeAmount > 0 ? '▲' : changeAmount < 0 ? '▼' : '';
        
        const open = stock.open ?? '-';
        const high = stock.high ?? '-';
        const low = stock.low ?? '-';
        const volume = stock.volume ?? stock.volume_change ?? '-';
        const volumeDisplay = volume !== '-' ? formatVolume(volume) : '-';
        
        const rowBgColor = index % 2 === 0 ? '#0f172a' : '#1a1f3a';
        
        html += `<tr class="watchlist-row" data-symbol="${stock.symbol}" 
                 style="background: ${rowBgColor}; border-bottom: 1px solid #1e293b; 
                        cursor: pointer; transition: all 0.2s ease; height: 50px;">
            <td style="padding: 12px 12px; text-align: left; font-weight: 600; color: #3b82f6; font-size: 14px;">
                ${stock.symbol}
            </td>
            <td style="padding: 12px 12px; text-align: right; color: #e2e8f0; font-size: 14px; font-weight: 600;">
                ${formatPrice(ltp)}
            </td>
            <td style="padding: 12px 12px; text-align: right; color: ${changeColor}; font-weight: 600; font-size: 14px;">
                ${changeSymbol} ${Math.abs(changeAmount).toFixed(2)}
            </td>
            <td style="padding: 12px 12px; text-align: right; color: ${changeColor}; font-weight: 600; font-size: 14px;">
                ${changeAmount !== 0 ? (changePercent > 0 ? '+' : '') + changePercent.toFixed(2) + '%' : '-'}
            </td>
            <td style="padding: 12px 12px; text-align: right; color: #cbd5e1; font-size: 13px;">
                ${formatPrice(open)}
            </td>
            <td style="padding: 12px 12px; text-align: right; color: #94a3b8; font-size: 13px;">
                ${formatPrice(high)}
            </td>
            <td style="padding: 12px 12px; text-align: right; color: #94a3b8; font-size: 13px;">
                ${formatPrice(low)}
            </td>
            <td style="padding: 12px 12px; text-align: right; color: #94a3b8; font-size: 13px;">
                ${volumeDisplay}
            </td>
        </tr>`;
    });
    
    html += `</tbody></table></div>`;
    
    if (algoWatchlistFull.length > 20) {
        html += `<div style="padding: 16px; text-align: center; background: #0f172a; border-radius: 0 0 8px 8px; margin-top: -2px;">
                    <button class="show-more-btn" id="toggleAlgoShowMore" 
                            style="padding: 10px 20px; background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%); 
                                   color: #fff; border: none; border-radius: 6px; cursor: pointer; 
                                   font-weight: 600; transition: all 0.2s ease; font-size: 13px;">
                        ${algoWatchlistShowMore ? '↑ Show Top 20' : '↓ Show All ' + algoWatchlistFull.length}
                    </button>
                </div>`;
    }
    
    if (watchlistTabContent) watchlistTabContent.innerHTML = html;
    
    // Add row hover effect
    document.querySelectorAll('.watchlist-row').forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.style.background = '#1e293b';
            row.style.boxShadow = '0 0 8px rgba(59, 130, 245, 0.15)';
        });
        row.addEventListener('mouseleave', () => {
            const index = Array.from(row.parentNode.children).indexOf(row);
            row.style.background = index % 2 === 0 ? '#0f172a' : '#1a1f3a';
            row.style.boxShadow = 'none';
        });
        
        // Click handler for mini graph (if canvas exists)
        if (miniGraphCanvas) {
            row.addEventListener('click', function(e) {
                const sym = this.dataset.symbol;
                selectedSymbolMeta = symbolMeta[sym] || null;
                showMiniGraph(sym);
            });
        }
    });
    
    const toggleBtn = document.getElementById('toggleAlgoShowMore');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            algoWatchlistShowMore = !algoWatchlistShowMore;
            displayAlgoWatchlistTable(algoWatchlistFull);
        });
    }
}

// Remove custom stock from watchlist
function removeCustomStock(symbol) {
    const index = customWatchlistSymbols.indexOf(symbol);
    if (index > -1) {
        customWatchlistSymbols.splice(index, 1);
        addLog(`Removed ${symbol} from watchlist`, 'info');
        refreshCurrentWatchlistTab(true);
    }
}

// --- Algo Agent Watchlist fetch/refresh ---
function fetchAlgoWatchlist() {
    if (!watchlistTabContent) {
        console.warn('watchlistTabContent not found');
        return Promise.resolve();
    }
    
    // Always fetch to keep data fresh (alphabetically sorted)
    // Fetch ONLY live market data (real spot prices, not algo/option data)
    // Default symbols sorted alphabetically
    const defaultSymbols = ['BANKNIFTY', 'FINNIFTY', 'GIFTNIFTY', 'NIFTY50', 'SENSEX'];
    const allSymbols = [...new Set([...defaultSymbols, ...customWatchlistSymbols])].sort(); // Remove duplicates and sort alphabetically
    
    const queryParams = allSymbols.map(s => `symbols=${encodeURIComponent(s)}`).join('&');
    
    return fetch(`${API_BASE}/market/live?${queryParams}`)
        .then(res => res.json())
        .then(data => {
            let combinedData = [];
            
            // Use ONLY the live market data
            if (data.success && data.data && data.data.symbols) {
                combinedData = Array.isArray(data.data.symbols) ? [...data.data.symbols] : [];
                // Sort alphabetically by symbol
                combinedData.sort((a, b) => (a.symbol || '').localeCompare(b.symbol || ''));
            }
            
            if (combinedData.length > 0 && currentWatchlistTab === 'algo_top10') {
                displayAlgoWatchlistTable(combinedData);
            } else if (watchlistTabContent && currentWatchlistTab === 'algo_top10' && combinedData.length === 0) {
                watchlistTabContent.innerHTML = `<p class="placeholder">No live market data available. Please try refreshing.</p>`;
            }
        })
        .catch(err => {
            console.error('Error loading live market data:', err);
            if (watchlistTabContent && currentWatchlistTab === 'algo_top10') {
                watchlistTabContent.innerHTML = `<p class="placeholder">Error loading live data: ${err.message}</p>`;
            }
        });
}

// --- Auto-refresh every 1 second for live data ---
if (watchlistTabContent) {
    console.log('Setting up watchlist auto-refresh every 1 second...');
    setInterval(fetchAlgoWatchlist, 1000);
    console.log('Initial fetchAlgoWatchlist call...');
    fetchAlgoWatchlist();
} else {
    console.warn('watchlistTabContent element not found - watchlist will not load');
}

// --- Algo Agent live ticker, opportunities, and feed ---
function renderAlgoLivePanels(data) {
    if (tickerTextEl && data && data.ticker !== undefined) {
        tickerTextEl.textContent = data.ticker || 'Scanning...';
    }

    if (opportunitiesTable) {
        const tbody = opportunitiesTable.querySelector('tbody');
        if (tbody) {
            const items = Array.isArray(data && data.opportunities) ? data.opportunities : [];
            if (items.length) {
                tbody.innerHTML = items.slice(0, 15).map(o => {
                    const changeNum = isFinite(parseFloat(o.change)) ? parseFloat(o.change) : null;
                    const changeText = changeNum !== null ? `${changeNum.toFixed(2)}%` : (o.change ?? '-');
                    return `
                        <tr>
                            <td>${o.symbol || '-'}</td>
                            <td>${o.strike ?? '-'}</td>
                            <td>${o.price ?? '-'}</td>
                            <td>${changeText}</td>
                            <td>${o.score ?? '-'}</td>
                        </tr>`;
                }).join('');
            } else {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:12px;">No opportunities yet</td></tr>';
            }
        }
    }

    if (liveFeedEl && data && Array.isArray(data.feed)) {
        liveFeedEl.innerHTML = data.feed.map(line => `<div>${line}</div>`).join('');
        liveFeedEl.scrollTop = liveFeedEl.scrollHeight;
    }

    if (agentActivityText) {
        agentActivityText.textContent = data && data.latest_action ? data.latest_action : 'Waiting for signals...';
    }

    if (summaryStatus && data) summaryStatus.textContent = data.status || '-';
    if (summaryTicker && data) summaryTicker.textContent = data.ticker || 'Scanning...';
    if (summaryAction && data) summaryAction.textContent = data.latest_action || '-';
    if (summaryWatchlist) {
        const fallbackCount = Array.isArray(data && data.opportunities) ? data.opportunities.length : 0;
        summaryWatchlist.textContent = Array.isArray(algoWatchlistFull) && algoWatchlistFull.length ? algoWatchlistFull.length : fallbackCount;
    }

    if (viewAlgoPicksBtn) {
        const items = Array.isArray(data && data.opportunities) ? data.opportunities : [];
        if (items.length) {
            viewAlgoPicksBtn.classList.add('pulse');
        } else {
            viewAlgoPicksBtn.classList.remove('pulse');
        }
    }
}

async function pollAlgoLivePanels() {
    try {
        const resp = await fetch(`${API_BASE}/algo/status`);
        const data = await resp.json();
        renderAlgoLivePanels(data);
    } catch (e) {
        // ignore transient errors
    }
}

setInterval(pollAlgoLivePanels, 2000);
pollAlgoLivePanels();

// Ensure all functions and the file are properly closed
