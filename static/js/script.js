// Global variables
let waterLevelChart = null;
let qualityChart = null;

// Smart Features Variables
let userLocation = null;
let currentLanguage = 'en';
let speechRecognition = null;
let speechSynthesis = window.speechSynthesis;
let isListening = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing INGRES Chatbot...');
    
    // Set welcome time
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    const welcomeTimeEl = document.getElementById('welcomeTime');
    if (welcomeTimeEl) {
        welcomeTimeEl.textContent = timeString;
    }
    
    // Initialize enhanced chat interface
    initializeEnhancedChat();
    
    // Initialize help system
    initializeHelpSystem();
    
    initializeCharts();
    loadDistrictCards();
    loadCitations();
    setupEventListeners();
    initializeSmartFeatures();
    
    // Show onboarding for first-time users
    checkFirstTimeUser();
});

// Setup event listeners
function setupEventListeners() {
    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const refreshButton = document.getElementById('refreshData');

    // Chat functionality
    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Refresh data
    refreshButton.addEventListener('click', function() {
        refreshButton.innerHTML = '<span class="loading"></span> Refreshing...';
        setTimeout(() => {
            initializeCharts();
            loadDistrictCards();
            loadCitations();
            refreshButton.innerHTML = 'Refresh Data';
        }, 1000);
    });
}

// Chat functionality
async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();
    
    if (!message) return;

    // Add user message to chat
    addMessageToChat(message, 'user');
    chatInput.value = '';

    // Show typing indicator
    const typingIndicator = addMessageToChat('AI is typing...', 'bot');
    typingIndicator.classList.add('typing');

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();
        
        // Remove typing indicator
        typingIndicator.remove();
        
        // Add bot response
        addMessageToChat(data.response, 'bot');
        
        // If district data is included, show it
        if (data.district_data) {
            showDistrictData(data.district_data);
        }

    } catch (error) {
        typingIndicator.remove();
        addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
        console.error('Chat error:', error);
    }
}

function addMessageToChat(message, sender) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = message.replace(/\n/g, '<br>');
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

function showDistrictData(districtData) {
    const message = `
        <strong>📊 Detailed Information:</strong><br>
        💧 Water Level: ${districtData.water_level}m below ground<br>
        🔍 Quality: ${districtData.quality}<br>
        📈 Trend: ${districtData.trend}<br>
        🏭 Wells Monitored: ${districtData.wells_monitored}<br>
        📅 Last Updated: ${districtData.last_updated}<br>
        📚 Citation: ${districtData.citation}
    `;
    addMessageToChat(message, 'bot');
}

// Initialize charts
async function initializeCharts() {
    try {
        const response = await fetch('/api/visualization');
        const data = await response.json();
        
        createWaterLevelChart(data);
        createQualityChart(data);
        
    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}

function createWaterLevelChart(data) {
    const ctx = document.getElementById('waterLevelChart').getContext('2d');
    
    if (waterLevelChart) {
        waterLevelChart.destroy();
    }
    
    waterLevelChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.districts,
            datasets: [{
                label: 'Water Level (meters below ground)',
                data: data.water_levels,
                backgroundColor: [
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 205, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Depth (meters)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const index = context.dataIndex;
                            return `Source: ${data.citations[index]}`;
                        }
                    }
                }
            }
        }
    });
}

function createQualityChart(data) {
    const ctx = document.getElementById('qualityChart').getContext('2d');
    
    if (qualityChart) {
        qualityChart.destroy();
    }
    
    qualityChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.districts,
            datasets: [{
                label: 'Water Quality Score',
                data: data.quality_scores,
                backgroundColor: [
                    'rgba(46, 204, 113, 0.8)',
                    'rgba(241, 196, 15, 0.8)',
                    'rgba(231, 76, 60, 0.8)',
                    'rgba(155, 89, 182, 0.8)',
                    'rgba(52, 152, 219, 0.8)'
                ],
                borderColor: [
                    'rgba(46, 204, 113, 1)',
                    'rgba(241, 196, 15, 1)',
                    'rgba(231, 76, 60, 1)',
                    'rgba(155, 89, 182, 1)',
                    'rgba(52, 152, 219, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const qualityLabels = ['Critical', 'Poor', 'Moderate', 'Good'];
                            const score = context.parsed;
                            return `${context.label}: ${qualityLabels[score - 1]} (${score}/4)`;
                        },
                        afterLabel: function(context) {
                            const index = context.dataIndex;
                            return `Source: ${data.citations[index]}`;
                        }
                    }
                }
            }
        }
    });
}

// Load district cards
async function loadDistrictCards() {
    try {
        const response = await fetch('/api/districts');
        const districts = await response.json();
        
        const cardsContainer = document.getElementById('districtCards');
        cardsContainer.innerHTML = '';
        
        for (const district of districts) {
            const districtResponse = await fetch(`/api/groundwater/${district}`);
            const districtData = await districtResponse.json();
            
            const card = createDistrictCard(district, districtData);
            cardsContainer.appendChild(card);
        }
        
    } catch (error) {
        console.error('Error loading district cards:', error);
    }
}

function createDistrictCard(district, data) {
    const card = document.createElement('div');
    card.className = 'district-card';
    
    // Determine quality color
    const qualityColors = {
        'Good': '#27ae60',
        'Moderate': '#f39c12',
        'Poor': '#e74c3c',
        'Critical': '#c0392b'
    };
    
    card.innerHTML = `
        <h4>${district}</h4>
        <div class="water-level">${data.water_level}m</div>
        <div class="quality" style="background-color: ${qualityColors[data.quality] || '#95a5a6'}">
            ${data.quality}
        </div>
        <div class="trend">Trend: ${data.trend}</div>
        <div style="font-size: 0.8em; margin-top: 10px; opacity: 0.8;">
            ${data.wells_monitored} wells monitored<br>
            Updated: ${data.last_updated}
        </div>
    `;
    
    // Add click event to show detailed info
    card.addEventListener('click', () => {
        const message = `Tell me about groundwater in ${district}`;
        document.getElementById('chatInput').value = message;
        sendMessage();
    });
    
    return card;
}

// Load citations
async function loadCitations() {
    try {
        const response = await fetch('/api/visualization');
        const data = await response.json();
        
        const citationsList = document.getElementById('citationsList');
        citationsList.innerHTML = '';
        
        const uniqueCitations = [...new Set(data.citations)];
        
        uniqueCitations.forEach(citation => {
            const citationDiv = document.createElement('div');
            citationDiv.className = 'citation-item';
            citationDiv.textContent = citation;
            citationsList.appendChild(citationDiv);
        });
        
    } catch (error) {
        console.error('Error loading citations:', error);
    }
}

// Smart Features
function initializeSmartFeatures() {
    // Location Detection
    const locationBtn = document.getElementById('locationBtn');
    if (locationBtn) {
        locationBtn.addEventListener('click', detectLocation);
    }
    
    // Voice Input
    const voiceBtn = document.getElementById('voiceBtn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', toggleVoiceInput);
    }
    
    // Language Selection
    const languageSelect = document.getElementById('languageSelect');
    if (languageSelect) {
        languageSelect.addEventListener('change', function(e) {
            currentLanguage = e.target.value;
            addMessageToChat(`Language changed to ${e.target.options[e.target.selectedIndex].text}`, 'bot');
        });
    }
    
    // Initialize Speech Recognition
    initializeSpeechRecognition();
    
    // Initialize Water Game
    initializeWaterGame();
    
    // Initialize Crisis Predictor
    initializeCrisisPredictor();
}

// Location Detection
function detectLocation() {
    const locationBtn = document.getElementById('locationBtn');
    const locationText = document.getElementById('locationText');
    
    locationBtn.classList.add('active');
    locationText.textContent = 'Detecting...';
    
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function(position) {
                userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                
                locationText.textContent = `📍 ${userLocation.latitude.toFixed(2)}, ${userLocation.longitude.toFixed(2)}`;
                locationBtn.classList.remove('active');
                
                addMessageToChat(`Location detected: ${userLocation.latitude.toFixed(4)}, ${userLocation.longitude.toFixed(4)}`, 'bot');
            },
            function(error) {
                console.error('Geolocation error:', error);
                locationText.textContent = 'Location Failed';
                locationBtn.classList.remove('active');
                addMessageToChat('Unable to detect location. Please specify your area manually.', 'bot');
            }
        );
    } else {
        locationText.textContent = 'Not Supported';
        locationBtn.classList.remove('active');
        addMessageToChat('Geolocation is not supported by this browser.', 'bot');
    }
}

// Voice Recognition
function initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        speechRecognition = new SpeechRecognition();
        
        speechRecognition.continuous = false;
        speechRecognition.interimResults = false;
        speechRecognition.lang = 'en-US';
        
        speechRecognition.onstart = function() {
            isListening = true;
            const voiceBtn = document.getElementById('voiceBtn');
            const voiceText = document.getElementById('voiceText');
            
            voiceBtn.classList.add('voice-recording');
            voiceText.textContent = 'Listening...';
        };
        
        speechRecognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('chatInput').value = transcript;
            
            setTimeout(() => {
                sendMessage();
            }, 500);
        };
        
        speechRecognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            addMessageToChat(`Voice recognition error: ${event.error}. Please try again.`, 'bot');
        };
        
        speechRecognition.onend = function() {
            isListening = false;
            const voiceBtn = document.getElementById('voiceBtn');
            const voiceText = document.getElementById('voiceText');
            
            voiceBtn.classList.remove('voice-recording');
            voiceText.textContent = 'Voice';
        };
    }
}

function toggleVoiceInput() {
    if (!speechRecognition) {
        addMessageToChat('Voice recognition is not supported in your browser.', 'bot');
        return;
    }
    
    if (isListening) {
        speechRecognition.stop();
    } else {
        speechRecognition.start();
    }
}

// Water Game
let gameState = {
    isRunning: false,
    isPaused: false,
    waterLevel: 100,
    score: 0,
    timeLeft: 60,
    drops: [],
    waste: [],
    gameLoop: null,
    canvas: null,
    ctx: null
};

function initializeWaterGame() {
    const gameBtn = document.getElementById('gameBtn');
    const closeGameBtn = document.getElementById('closeGame');
    const startGameBtn = document.getElementById('startGame');
    const pauseGameBtn = document.getElementById('pauseGame');
    
    if (gameBtn) {
        gameBtn.addEventListener('click', toggleWaterGame);
    }
    
    if (closeGameBtn) {
        closeGameBtn.addEventListener('click', closeWaterGame);
    }
    
    if (startGameBtn) {
        startGameBtn.addEventListener('click', startWaterGame);
    }
    
    if (pauseGameBtn) {
        pauseGameBtn.addEventListener('click', pauseWaterGame);
    }
    
    gameState.canvas = document.getElementById('gameCanvas');
    if (gameState.canvas) {
        gameState.ctx = gameState.canvas.getContext('2d');
        gameState.canvas.addEventListener('click', handleGameClick);
    }
}

function toggleWaterGame() {
    const gameDiv = document.getElementById('waterGame');
    if (gameDiv.style.display === 'none') {
        gameDiv.style.display = 'block';
    } else {
        gameDiv.style.display = 'none';
        stopWaterGame();
    }
}

function closeWaterGame() {
    document.getElementById('waterGame').style.display = 'none';
    stopWaterGame();
}

function startWaterGame() {
    if (gameState.isRunning) return;
    
    gameState.isRunning = true;
    gameState.isPaused = false;
    gameState.waterLevel = 100;
    gameState.score = 0;
    gameState.timeLeft = 60;
    gameState.drops = [];
    gameState.waste = [];
    
    updateGameStats();
    document.getElementById('startGame').disabled = true;
    document.getElementById('pauseGame').disabled = false;
    
    gameState.gameLoop = setInterval(gameLoop, 50);
    
    const timer = setInterval(() => {
        if (!gameState.isRunning || gameState.isPaused) return;
        
        gameState.timeLeft--;
        updateGameStats();
        
        if (gameState.timeLeft <= 0) {
            clearInterval(timer);
            endWaterGame();
        }
    }, 1000);
    
    addMessageToChat('🎮 Water Conservation Game started! Collect water drops and avoid waste!', 'bot');
}

function pauseWaterGame() {
    gameState.isPaused = !gameState.isPaused;
    const pauseBtn = document.getElementById('pauseGame');
    pauseBtn.textContent = gameState.isPaused ? 'Resume' : 'Pause';
}

function stopWaterGame() {
    gameState.isRunning = false;
    gameState.isPaused = false;
    
    if (gameState.gameLoop) {
        clearInterval(gameState.gameLoop);
        gameState.gameLoop = null;
    }
    
    document.getElementById('startGame').disabled = false;
    document.getElementById('pauseGame').disabled = true;
    document.getElementById('pauseGame').textContent = 'Pause';
    
    if (gameState.ctx) {
        gameState.ctx.clearRect(0, 0, gameState.canvas.width, gameState.canvas.height);
    }
}

function gameLoop() {
    if (!gameState.isRunning || gameState.isPaused) return;
    
    gameState.ctx.clearRect(0, 0, gameState.canvas.width, gameState.canvas.height);
    
    if (Math.random() < 0.1) {
        spawnWaterDrop();
    }
    
    if (Math.random() < 0.05) {
        spawnWaste();
    }
    
    updateDrops();
    updateWaste();
    drawGame();
}

function spawnWaterDrop() {
    gameState.drops.push({
        x: Math.random() * (gameState.canvas.width - 20),
        y: -20,
        size: 15 + Math.random() * 10,
        speed: 2 + Math.random() * 3,
        value: 5 + Math.floor(Math.random() * 10)
    });
}

function spawnWaste() {
    gameState.waste.push({
        x: Math.random() * (gameState.canvas.width - 30),
        y: -30,
        size: 20 + Math.random() * 15,
        speed: 1 + Math.random() * 2,
        damage: 10 + Math.floor(Math.random() * 15)
    });
}

function updateDrops() {
    for (let i = gameState.drops.length - 1; i >= 0; i--) {
        const drop = gameState.drops[i];
        drop.y += drop.speed;
        
        if (drop.y > gameState.canvas.height) {
            gameState.drops.splice(i, 1);
            gameState.waterLevel -= 2;
        }
    }
}

function updateWaste() {
    for (let i = gameState.waste.length - 1; i >= 0; i--) {
        const waste = gameState.waste[i];
        waste.y += waste.speed;
        
        if (waste.y > gameState.canvas.height) {
            gameState.waste.splice(i, 1);
        }
    }
}

function drawGame() {
    const ctx = gameState.ctx;
    
    gameState.drops.forEach(drop => {
        ctx.fillStyle = '#2196F3';
        ctx.beginPath();
        ctx.arc(drop.x, drop.y, drop.size, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.fillStyle = '#87CEEB';
        ctx.beginPath();
        ctx.arc(drop.x - drop.size/3, drop.y - drop.size/3, drop.size/3, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.fillStyle = 'white';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`+${drop.value}`, drop.x, drop.y + 4);
    });
    
    gameState.waste.forEach(waste => {
        ctx.fillStyle = '#FF5722';
        ctx.fillRect(waste.x, waste.y, waste.size, waste.size);
        
        ctx.fillStyle = 'white';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('⚠️', waste.x + waste.size/2, waste.y + waste.size/2 + 6);
    });
    
    const waterHeight = (gameState.waterLevel / 100) * 50;
    ctx.fillStyle = '#2196F3';
    ctx.fillRect(10, gameState.canvas.height - waterHeight - 10, 30, waterHeight);
    
    ctx.strokeStyle = '#1976D2';
    ctx.lineWidth = 2;
    ctx.strokeRect(10, gameState.canvas.height - 60, 30, 50);
    
    ctx.fillStyle = 'black';
    ctx.font = '12px Arial';
    ctx.textAlign = 'left';
    ctx.fillText('Water', 45, gameState.canvas.height - 35);
}

function handleGameClick(event) {
    if (!gameState.isRunning || gameState.isPaused) return;
    
    const rect = gameState.canvas.getBoundingClientRect();
    const clickX = event.clientX - rect.left;
    const clickY = event.clientY - rect.top;
    
    for (let i = gameState.drops.length - 1; i >= 0; i--) {
        const drop = gameState.drops[i];
        const distance = Math.sqrt((clickX - drop.x) ** 2 + (clickY - drop.y) ** 2);
        
        if (distance <= drop.size) {
            gameState.score += drop.value;
            gameState.waterLevel = Math.min(100, gameState.waterLevel + drop.value);
            gameState.drops.splice(i, 1);
            return;
        }
    }
    
    for (let i = gameState.waste.length - 1; i >= 0; i--) {
        const waste = gameState.waste[i];
        
        if (clickX >= waste.x && clickX <= waste.x + waste.size &&
            clickY >= waste.y && clickY <= waste.y + waste.size) {
            gameState.waterLevel -= waste.damage;
            gameState.waste.splice(i, 1);
            return;
        }
    }
}

function updateGameStats() {
    const waterLevelEl = document.getElementById('waterLevel');
    const gameScoreEl = document.getElementById('gameScore');
    const gameTimeEl = document.getElementById('gameTime');
    
    if (waterLevelEl) waterLevelEl.textContent = Math.max(0, gameState.waterLevel);
    if (gameScoreEl) gameScoreEl.textContent = gameState.score;
    if (gameTimeEl) gameTimeEl.textContent = gameState.timeLeft;
}

function endWaterGame() {
    stopWaterGame();
    addMessageToChat(`🎮 Game Over! Final Score: ${gameState.score} points. Water Level: ${gameState.waterLevel}%`, 'bot');
}

// Crisis Predictor
function initializeCrisisPredictor() {
    const crisisBtn = document.getElementById('crisisBtn');
    const closeCrisisBtn = document.getElementById('closeCrisis');
    const predictBtn = document.getElementById('predictBtn');
    const alertsBtn = document.getElementById('alertsBtn');

    if (crisisBtn) {
        crisisBtn.addEventListener('click', toggleCrisisPredictor);
    }

    if (closeCrisisBtn) {
        closeCrisisBtn.addEventListener('click', closeCrisisPredictor);
    }

    if (predictBtn) {
        predictBtn.addEventListener('click', predictCrisis);
    }

    if (alertsBtn) {
        alertsBtn.addEventListener('click', viewCrisisAlerts);
    }
}

function toggleCrisisPredictor() {
    const crisisPanel = document.getElementById('crisisPanel');
    crisisPanel.style.display = (crisisPanel.style.display === 'none') ? 'block' : 'none';
}

function closeCrisisPredictor() {
    document.getElementById('crisisPanel').style.display = 'none';
}

async function predictCrisis() {
    const district = document.getElementById('crisisDistrict').value;
    if (!district) {
        alert('Please select a district');
        return;
    }

    try {
        // Use POST to /api/crisis/state for state-wise prediction
        const response = await fetch('/api/crisis/state', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ state: district })
        });
        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            // Adapt to displayCrisisResults format
            displayCrisisResults({
                district: data.location,
                prediction: {
                    severity: data.severity,
                    days_to_crisis: data.days_to_crisis,
                    probability: data.extraction_to_resource_ratio // Use ratio as probability
                },
                recommendations: data.recommendations
            });
        }
    } catch (error) {
        console.error('Error predicting crisis:', error);
        alert('Error predicting crisis. Please try again.');
    }
}

async function viewCrisisAlerts() {
    try {
        // Example: fetch all states and show critical/high alerts
        const response = await fetch('/api/crisis/alerts');
        const data = await response.json();

        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            displayCrisisAlerts(data.alerts);
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
        alert('Error loading alerts. Please try again.');
    }
}

function displayCrisisResults(prediction) {
    const resultsDiv = document.getElementById('crisisResults');

    const severityLevel = prediction.prediction.severity.toLowerCase();
    const severityIcon = getSeverityIcon(severityLevel);
    const severityColor = getSeverityColor(severityLevel);

    resultsDiv.innerHTML = `
        <div class="prediction-header">
            <h4>${severityIcon} Crisis Prediction for ${prediction.district}</h4>
            <div class="audio-controls">
                <button id="playAudio" class="audio-btn" title="Play Audio Summary">🔊</button>
                <button id="stopAudio" class="audio-btn" title="Stop Audio" style="display: none;">⏹️</button>
            </div>
        </div>
        <div class="prediction-cards">
            <div class="severity-card ${severityLevel}" style="border-left-color: ${severityColor};">
                <div class="card-icon">${severityIcon}</div>
                <div class="card-content">
                    <h5>Severity Level</h5>
                    <p class="severity-value">${prediction.prediction.severity}</p>
                </div>
            </div>
            <div class="timeline-card">
                <div class="card-icon">⏰</div>
                <div class="card-content">
                    <h5>Days to Crisis</h5>
                    <p class="timeline-value">${prediction.prediction.days_to_crisis}</p>
                </div>
            </div>
            <div class="probability-card">
                <div class="card-icon">📊</div>
                <div class="card-content">
                    <h5>Probability</h5>
                    <p class="probability-value">${(prediction.prediction.probability * 100).toFixed(1)}%</p>
                </div>
            </div>
        </div>
        <div class="recommendations-section">
            <h5>💡 Recommendations:</h5>
            <div class="recommendations-grid">
                ${prediction.recommendations.map((rec, index) => `
                    <div class="recommendation-item">
                        <span class="rec-number">${index + 1}</span>
                        <span class="rec-text">${rec}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `;

    setTimeout(() => {
        playPredictionAudio(prediction);
    }, 500);

    document.getElementById('playAudio').addEventListener('click', () => playPredictionAudio(prediction));
    document.getElementById('stopAudio').addEventListener('click', stopPredictionAudio);
}

function getSeverityIcon(severity) {
    const icons = {
        'low': '🟢',
        'moderate': '🟡',
        'high': '🟠',
        'critical': '🔴'
    };
    return icons[severity] || '⚪';
}

function getSeverityColor(severity) {
    const colors = {
        'low': '#10b981',
        'moderate': '#f59e0b',
        'high': '#f97316',
        'critical': '#ef4444'
    };
    return colors[severity] || '#6b7280';
}

let currentAudio = null;

function playPredictionAudio(prediction) {
    stopPredictionAudio();

    const severity = prediction.prediction.severity;
    const district = prediction.district;
    const days = prediction.prediction.days_to_crisis;
    const probability = (prediction.prediction.probability * 100).toFixed(1);

    let message = `Water crisis prediction for ${district}. `;
    message += `Severity level: ${severity}. `;
    message += `Estimated ${days} days to potential crisis. `;
    message += `Probability: ${probability} percent. `;

    if (severity.toLowerCase() === 'critical') {
        message += 'Immediate action required. ';
    } else if (severity.toLowerCase() === 'high') {
        message += 'Urgent attention needed. ';
    } else if (severity.toLowerCase() === 'moderate') {
        message += 'Monitor situation closely. ';
    } else {
        message += 'Continue current practices. ';
    }

    message += 'Check recommendations for detailed guidance.';

    if ('speechSynthesis' in window) {
        currentAudio = new SpeechSynthesisUtterance(message);
        currentAudio.rate = 0.9;
        currentAudio.pitch = 1;
        currentAudio.volume = 0.8;

        currentAudio.onstart = () => {
            document.getElementById('playAudio').style.display = 'none';
            document.getElementById('stopAudio').style.display = 'inline-block';
        };

        currentAudio.onend = () => {
            document.getElementById('playAudio').style.display = 'inline-block';
            document.getElementById('stopAudio').style.display = 'none';
        };

        speechSynthesis.speak(currentAudio);
    }
}

function stopPredictionAudio() {
    if (currentAudio) {
        speechSynthesis.cancel();
        document.getElementById('playAudio').style.display = 'inline-block';
        document.getElementById('stopAudio').style.display = 'none';
    }
}

function displayCrisisAlerts(alerts) {
    const resultsDiv = document.getElementById('crisisResults');

    if (!alerts || alerts.length === 0) {
        resultsDiv.innerHTML = `
            <div class="no-alerts">
                <div class="no-alerts-icon">✅</div>
                <h4>All Clear!</h4>
                <p>No critical water crisis alerts at this time.</p>
            </div>
        `;
        return;
    }

    resultsDiv.innerHTML = `
        <div class="alerts-header">
            <h4>🚨 Crisis Alerts (${alerts.length})</h4>
            <div class="audio-controls">
                <button id="playAlertsAudio" class="audio-btn" title="Play Alerts Summary">🔊</button>
                <button id="stopAlertsAudio" class="audio-btn" title="Stop Audio" style="display: none;">⏹️</button>
            </div>
        </div>
        <div class="alerts-grid">
            ${alerts.map((alert, index) => `
                <div class="alert-card ${alert.severity.toLowerCase()}">
                    <div class="alert-header">
                        <h5>${getSeverityIcon(alert.severity.toLowerCase())} ${alert.district}</h5>
                        <span class="alert-badge ${alert.severity.toLowerCase()}">${alert.severity}</span>
                    </div>
                    <div class="alert-details">
                        <div class="alert-stat">
                            <span class="stat-label">Timeline</span>
                            <span class="stat-value">${alert.days_to_crisis} days</span>
                        </div>
                        <div class="alert-stat">
                            <span class="stat-label">Probability</span>
                            <span class="stat-value">${(alert.probability * 100).toFixed(1)}%</span>
                        </div>
                        <div class="alert-stat">
                            <span class="stat-label">Water Level</span>
                            <span class="stat-value">${alert.current_water_level ? alert.current_water_level + 'm' : 'N/A'}</span>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    setTimeout(() => {
        playAlertsAudio(alerts);
    }, 500);

    document.getElementById('playAlertsAudio').addEventListener('click', () => playAlertsAudio(alerts));
    document.getElementById('stopAlertsAudio').addEventListener('click', stopAlertsAudio);
}

function playAlertsAudio(alerts) {
    stopAlertsAudio();

    let message = `Water crisis alerts summary. ${alerts.length} districts require attention. `;

    alerts.forEach((alert, index) => {
        message += `${alert.district}: ${alert.severity} severity, ${alert.days_to_crisis} days to crisis. `;
    });

    message += 'Please review detailed information and take appropriate action.';

    if ('speechSynthesis' in window) {
        currentAudio = new SpeechSynthesisUtterance(message);
        currentAudio.rate = 0.9;
        currentAudio.pitch = 1;
        currentAudio.volume = 0.8;

        currentAudio.onstart = () => {
            document.getElementById('playAlertsAudio').style.display = 'none';
            document.getElementById('stopAlertsAudio').style.display = 'inline-block';
        };

        currentAudio.onend = () => {
            document.getElementById('playAlertsAudio').style.display = 'inline-block';
            document.getElementById('stopAlertsAudio').style.display = 'none';
        };

        speechSynthesis.speak(currentAudio);
    }
}

function stopAlertsAudio() {
    if (currentAudio) {
        speechSynthesis.cancel();
        const playBtn = document.getElementById('playAlertsAudio');
        const stopBtn = document.getElementById('stopAlertsAudio');
        if (playBtn) playBtn.style.display = 'inline-block';
        if (stopBtn) stopBtn.style.display = 'none';
    }
}

console.log('🚀 INGRES Chatbot Initialized Successfully!');