// WebSocket connection management
let socket = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

// Get WebSocket URL from current location
const WS_URL = window.location.origin;

function initWebSocket() {
    try {
        socket = io(WS_URL, {
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: MAX_RECONNECT_ATTEMPTS
        });

        socket.on('connect', () => {
            console.log('WebSocket connected');
            updateStatus('online', 'Connected');
            reconnectAttempts = 0;
        });

        socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
            updateStatus('offline', 'Disconnected');
        });

        socket.on('connection_response', (data) => {
            console.log('Connection response:', data);
        });

        socket.on('news_update', (data) => {
            console.log('News update received:', data);
            if (typeof updateUI === 'function') {
                updateUI(data);
            }
            if (typeof showNotification === 'function') {
                showNotification('New data available!', 'success');
            }
        });

        socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            reconnectAttempts++;
            
            if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                updateStatus('offline', 'Connection failed');
                if (typeof showNotification === 'function') {
                    showNotification('Failed to connect to server', 'error');
                }
            }
        });

        socket.on('reconnect', (attemptNumber) => {
            console.log('Reconnected after', attemptNumber, 'attempts');
            updateStatus('online', 'Reconnected');
            if (typeof showNotification === 'function') {
                showNotification('Reconnected to server', 'success');
            }
        });

        socket.on('reconnect_failed', () => {
            console.error('Reconnection failed');
            updateStatus('offline', 'Connection lost');
            if (typeof showNotification === 'function') {
                showNotification('Unable to reconnect to server', 'error');
            }
        });

    } catch (error) {
        console.error('Error initializing WebSocket:', error);
        updateStatus('offline', 'Connection error');
    }
}

function updateStatus(status, text) {
    const indicator = document.getElementById('statusIndicator');
    if (!indicator) return;
    
    const dot = indicator.querySelector('.status-dot');
    const statusText = indicator.querySelector('.status-text');
    
    if (dot) dot.className = `status-dot ${status}`;
    if (statusText) statusText.textContent = text;
}

function requestUpdate() {
    if (socket && socket.connected) {
        socket.emit('request_update');
    } else {
        console.warn('Socket not connected, cannot request update');
    }
}

// Initialize WebSocket on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing WebSocket connection...');
    initWebSocket();
});