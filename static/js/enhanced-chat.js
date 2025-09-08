// Enhanced Chat Interface Functions

// Initialize enhanced chat features
function initializeEnhancedChat() {
    // Quick action buttons
    const quickButtons = document.querySelectorAll('.quick-btn');
    quickButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            if (query) {
                document.getElementById('chatInput').value = query;
                sendMessage();
            }
        });
    });
    
    // Clear chat button
    const clearChatBtn = document.getElementById('clearChatBtn');
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', clearChat);
    }
    
    // Enhanced send button
    const sendButton = document.getElementById('sendButton');
    if (sendButton) {
        sendButton.addEventListener('click', sendEnhancedMessage);
    }
    
    // Enhanced input handling
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendEnhancedMessage();
            }
        });
        
        // Auto-resize input
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }
}

// Enhanced message sending with typing indicator
function sendEnhancedMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message with timestamp
    addUserMessage(message);
    
    // Clear input and hide quick actions
    input.value = '';
    hideQuickActions();
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send to backend
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        addBotMessage(data.response);
        showQuickActions();
    })
    .catch(error => {
        hideTypingIndicator();
        addBotMessage('Sorry, I encountered an error. Please try again.');
        showQuickActions();
        console.error('Chat error:', error);
    });
}

// Add user message with enhanced styling
function addUserMessage(message) {
    const chatContainer = document.getElementById('chatContainer');
    const timestamp = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user-message';
    messageDiv.innerHTML = `
        <div class="message-content user-content">
            <div class="message-header">
                <span class="sender-name">You</span>
                <span class="message-time">${timestamp}</span>
            </div>
            <p>${message}</p>
        </div>
        <div class="message-avatar user-avatar">👤</div>
    `;
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Add bot message with enhanced styling
function addBotMessage(message) {
    const chatContainer = document.getElementById('chatContainer');
    const timestamp = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot-message';
    messageDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="message-header">
                <span class="sender-name">INGRES AI</span>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-text">${formatBotMessage(message)}</div>
        </div>
    `;
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Format bot messages with better styling
function formatBotMessage(message) {
    // Convert markdown-like formatting
    message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    message = message.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert lists
    message = message.replace(/^- (.*$)/gim, '<li>$1</li>');
    message = message.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    
    // Convert line breaks
    message = message.replace(/\n/g, '<br>');
    
    return message;
}

// Show/hide typing indicator
function showTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.style.display = 'flex';
        const chatContainer = document.getElementById('chatContainer');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

// Show/hide quick actions
function showQuickActions() {
    const quickActions = document.getElementById('quickActions');
    if (quickActions) {
        quickActions.style.display = 'flex';
    }
}

function hideQuickActions() {
    const quickActions = document.getElementById('quickActions');
    if (quickActions) {
        quickActions.style.display = 'none';
    }
}

// Clear chat function
function clearChat() {
    const chatContainer = document.getElementById('chatContainer');
    if (chatContainer) {
        // Keep only the welcome message
        const welcomeMessage = chatContainer.querySelector('.welcome-message');
        chatContainer.innerHTML = '';
        if (welcomeMessage) {
            chatContainer.appendChild(welcomeMessage);
        }
        showQuickActions();
    }
}