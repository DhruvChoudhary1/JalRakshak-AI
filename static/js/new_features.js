// Essential functions for new features
function closePanel(panelId) {
    document.getElementById(panelId).style.display = 'none';
}

function showReportsTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('#reportsPanel .tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('#reportsPanel .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').style.display = 'block';
    event.target.classList.add('active');
}

function showAnalyticsTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('#analyticsPanel .tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('#analyticsPanel .tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').style.display = 'block';
    event.target.classList.add('active');
}

// Placeholder functions to prevent errors
function searchLocation() {
    alert('Map search feature - coming soon!');
}

function toggleMapLayer(layer, enabled) {
    console.log(`Toggle layer ${layer}: ${enabled}`);
}

function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            document.getElementById('reportLocation').value = `${lat}, ${lon}`;
        });
    } else {
        alert('Geolocation not supported');
    }
}

function submitReport(event) {
    event.preventDefault();
    alert('Report submission feature - coming soon!');
}

function filterReports() {
    alert('Report filtering feature - coming soon!');
}

function predictWaterLevels() {
    alert('Water level prediction feature - coming soon!');
}

function analyzeTrends() {
    alert('Trend analysis feature - coming soon!');
}

function compareDistricts() {
    alert('District comparison feature - coming soon!');
}

// Initialize new features - use setTimeout to avoid conflicts
setTimeout(function() {
    // Add event listeners for new feature buttons
    const mapBtn = document.getElementById('mapBtn');
    const reportsBtn = document.getElementById('reportsBtn');
    const analyticsBtn = document.getElementById('analyticsBtn');
    
    if (mapBtn) {
        mapBtn.addEventListener('click', function() {
            const panel = document.getElementById('mapPanel');
            if (panel) panel.style.display = 'block';
        });
    }
    
    if (reportsBtn) {
        reportsBtn.addEventListener('click', function() {
            const panel = document.getElementById('reportsPanel');
            if (panel) panel.style.display = 'block';
        });
    }
    
    if (analyticsBtn) {
        analyticsBtn.addEventListener('click', function() {
            document.getElementById('analyticsPanel').style.display = 'block';
        });
    }
});