// Main application logic
let autoRefreshEnabled = false;
let autoRefreshInterval = null;
let currentData = null;

// Get API base URL from current location
const API_BASE_URL = window.location.origin;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing Financial News Bot...');
    initializeApp();
    setupEventListeners();
});

function initializeApp() {
    fetchNews();
}

function setupEventListeners() {
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            fetchNews(true);
        });
    }

  
    const autoRefreshBtn = document.getElementById('autoRefreshBtn');
    if (autoRefreshBtn) {
        autoRefreshBtn.addEventListener('click', toggleAutoRefresh);
    }

    // Timeframe change
    const timeframe = document.getElementById('timeframe');
    if (timeframe) {
        timeframe.addEventListener('change', () => {
            fetchNews();
        });
    }
}

async function fetchNews(force = false) {
    const loadingState = document.getElementById('loadingState');
    const mainContent = document.getElementById('mainContent');
    const errorState = document.getElementById('errorState');
    const refreshBtn = document.getElementById('refreshBtn');

    // Show loading
    if (loadingState) loadingState.style.display = 'flex';
    if (mainContent) mainContent.style.display = 'none';
    if (errorState) errorState.style.display = 'none';
    if (refreshBtn) refreshBtn.disabled = true;

    try {
        const endpoint = force ? '/api/refresh' : '/api/news';
        const method = force ? 'POST' : 'GET';
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
            currentData = result.data;
            updateUI(result.data);
            updateLastUpdateTime();
            
            if (force) {
                showNotification('Data refreshed successfully!', 'success');
            }
        } else {
            throw new Error(result.error || 'Unknown error');
        }

    } catch (error) {
        console.error('Error fetching news:', error);
        showError(error.message);
    } finally {
        if (loadingState) loadingState.style.display = 'none';
        if (refreshBtn) refreshBtn.disabled = false;
    }
}

function updateUI(data) {
    const mainContent = document.getElementById('mainContent');
    const errorState = document.getElementById('errorState');

    if (errorState) errorState.style.display = 'none';
    if (mainContent) mainContent.style.display = 'block';

    // Update summary
    updateSummary(data.summary || []);

    // Update stats
    const totalArticles = document.getElementById('totalArticles');
    const totalInstitutions = document.getElementById('totalInstitutions');
    const positiveCount = document.getElementById('positiveCount');
    const negativeCount = document.getElementById('negativeCount');

    if (totalArticles) totalArticles.textContent = data.total_articles || 0;
    if (totalInstitutions) totalInstitutions.textContent = data.total_institutions || 0;
    if (positiveCount) positiveCount.textContent = data.positive_count || 0;
    if (negativeCount) negativeCount.textContent = data.negative_count || 0;

    // Update chart
    if (window.chartFunctions && data.institutions) {
        window.chartFunctions.createImpactChart(data.institutions);
    }

    // Update table
    updateTable(data.institutions || {});

    // Update top 3 analysis
    updateAnalysisGrid(data.institutions || {});
}

function updateSummary(summary) {
    const summaryList = document.getElementById('summaryList');
    if (!summaryList) return;
    
    summaryList.innerHTML = '';

    if (!summary || summary.length === 0) {
        summaryList.innerHTML = '<li>No summary available</li>';
        return;
    }

    summary.forEach(point => {
        const li = document.createElement('li');
        li.textContent = point;
        summaryList.appendChild(li);
    });
}

function updateTable(institutions) {
    const tableBody = document.getElementById('institutionsTableBody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';

    if (!institutions || Object.keys(institutions).length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center;">No data available</td></tr>';
        return;
    }

    let rank = 1;
    for (const [name, data] of Object.entries(institutions)) {
        const row = document.createElement('tr');
        
        const sentimentClass = data.sentiment.toLowerCase();
        const sentimentIcon = getDirectionIcon(data.sentiment);
        
        row.innerHTML = `
            <td><span class="rank-badge">${rank}</span></td>
            <td><strong>${name}</strong></td>
            <td><span class="score-badge">${data.impact_score.toFixed(2)}</span></td>
            <td>
                <span class="direction-${sentimentClass}">
                    ${sentimentIcon}
                    ${data.sentiment}
                </span>
            </td>
            <td>${data.mentions}</td>
            <td>
                <div class="linkage-bar">
                    <div class="linkage-fill" style="width: ${Math.min(data.india_linkage * 5, 100)}%"></div>
                </div>
                <small>${data.india_linkage} refs</small>
            </td>
            <td>${data.recent_articles} articles</td>
        `;
        
        tableBody.appendChild(row);
        rank++;
    }
}

function getDirectionIcon(sentiment) {
    if (sentiment === 'Positive') return '📈';
    if (sentiment === 'Negative') return '📉';
    return '➖';
}

function updateAnalysisGrid(institutions) {
    const analysisGrid = document.getElementById('analysisGrid');
    if (!analysisGrid) return;
    
    analysisGrid.innerHTML = '';

    if (!institutions || Object.keys(institutions).length === 0) {
        analysisGrid.innerHTML = '<p>No analysis available</p>';
        return;
    }

    const top3 = Object.entries(institutions).slice(0, 3);

    top3.forEach(([name, data], index) => {
        const div = document.createElement('div');
        div.className = 'analysis-item';
        
        let analysis = `High impact driven by ${data.mentions} mentions with ${data.sentiment.toLowerCase()} sentiment. `;
        analysis += `India relevance score of ${data.india_linkage} indicates ${
            data.india_linkage > 10 ? 'strong' : 
            data.india_linkage > 5 ? 'moderate' : 'limited'
        } connection to Indian markets. `;
        
        if (data.sentiment_value > 0.1) {
            analysis += 'Positive developments suggest potential market optimism.';
        } else if (data.sentiment_value < -0.1) {
            analysis += 'Negative sentiment may create market headwinds.';
        } else {
            analysis += 'Mixed signals require careful monitoring.';
        }

        div.innerHTML = `
            <h3>#${index + 1} ${name}</h3>
            <p>${analysis}</p>
            ${data.key_drivers && data.key_drivers.length > 0 ? `
                <div style="margin-top: 1rem;">
                    <strong style="color: var(--primary);">Key Drivers:</strong>
                    <ul style="margin-top: 0.5rem; padding-left: 1.5rem; color: var(--gray);">
                        ${data.key_drivers.map(driver => `<li>${driver}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;
        
        analysisGrid.appendChild(div);
    });
}

function updateLastUpdateTime() {
    const lastUpdate = document.getElementById('lastUpdate');
    if (!lastUpdate) return;
    
    const now = new Date();
    lastUpdate.textContent = now.toLocaleTimeString();
}

function toggleAutoRefresh() {
    autoRefreshEnabled = !autoRefreshEnabled;
    const statusSpan = document.getElementById('autoRefreshStatus');
    
    if (autoRefreshEnabled) {
        if (statusSpan) {
            statusSpan.textContent = 'ON';
            statusSpan.style.color = 'var(--success)';
        }
        autoRefreshInterval = setInterval(() => {
            fetchNews();
        }, 300000); // 5 minutes
        showNotification('Auto-refresh enabled (every 5 minutes)', 'success');
    } else {
        if (statusSpan) {
            statusSpan.textContent = 'OFF';
            statusSpan.style.color = 'var(--gray)';
        }
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
        }
        showNotification('Auto-refresh disabled', 'info');
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    if (!input) return;
    
    const message = input.value.trim();
    
    if (!message) return;

    addChatMessage(message, 'user');
    input.value = '';

    // Show typing indicator
    const typingIndicator = addChatMessage('Thinking...', 'bot', true);

    try {
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        const result = await response.json();

        // Remove typing indicator
        if (typingIndicator && typingIndicator.parentNode) {
            typingIndicator.remove();
        }

        if (result.success) {
            addChatMessage(result.response, 'bot');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
        }

    } catch (error) {
        console.error('Chat error:', error);
        if (typingIndicator && typingIndicator.parentNode) {
            typingIndicator.remove();
        }
        addChatMessage('Sorry, I could not process your request.', 'bot');
    }
}

function addChatMessage(text, sender, isTyping = false) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return null;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    
    if (isTyping) {
        messageDiv.classList.add('typing');
    }
    
    // Convert markdown-style formatting
    const formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    
    messageDiv.innerHTML = formattedText;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageDiv;
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? 'var(--success)' : type === 'error' ? 'var(--danger)' : 'var(--primary)'};
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showError(message) {
    const errorState = document.getElementById('errorState');
    const errorMessage = document.getElementById('errorMessage');
    
    if (errorMessage) errorMessage.textContent = message;
    if (errorState) errorState.style.display = 'block';
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .typing {
        opacity: 0.7;
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.7; }
        50% { opacity: 1; }
    }
`;
document.head.appendChild(style);
