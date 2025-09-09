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
    const query = document.getElementById('mapSearch').value.trim();
    if (!query) {
        alert('Please enter a location to search.');
        return;
    }
    const mapDiv = document.getElementById('interactiveMap');
    if (!window.google || !window.google.maps || !mapDiv) {
        alert('Map is not loaded yet.');
        return;
    }
    const geocoder = new google.maps.Geocoder();
    geocoder.geocode({ address: query }, function(results, status) {
        if (status === 'OK' && results[0]) {
            const location = results[0].geometry.location;
            // Always initialize mapInstance if undefined
            if (!window.mapInstance) {
                window.mapInstance = new google.maps.Map(mapDiv, {
                    center: location,
                    zoom: 12
                });
                mapDiv.dataset.mapInitialized = 'true';
            } else {
                window.mapInstance.setCenter(location);
                window.mapInstance.setZoom(12);
            }
            // Remove previous marker
            if (window.mapMarker) {
                window.mapMarker.setMap(null);
            }
            window.mapMarker = new google.maps.Marker({
                map: window.mapInstance,
                position: location,
                title: query
            });
            document.getElementById('mapInfo').innerHTML = `<strong>Location:</strong> ${results[0].formatted_address}`;
        } else {
            alert('Location not found. Please try another search.');
        }
    });
}


function toggleMapLayer(layer, enabled) {
    if (layer === 'groundwater_levels') {
        if (enabled) {
            showWaterLevelMarkers();
        } else {
            hideWaterLevelMarkers();
        }
    } else if (layer === 'quality_zones') {
        if (enabled) {
            showQualityZoneMarkers();
        } else {
            hideQualityZoneMarkers();
        }
    } else if (layer === 'monitoring_wells') {
        if (enabled) {
            showWellMarkers();
        } else {
            hideWellMarkers();
        }
    } else if (layer === 'crisis_alerts') {
        if (enabled) {
            showAlertMarkers();
        } else {
            hideAlertMarkers();
        }
    }
}


// Store markers globally for each layer
window.waterLevelMarkers = [];
window.qualityZoneMarkers = [];
window.wellMarkers = [];
window.alertMarkers = [];

function showWaterLevelMarkers() {
    const district = document.getElementById('mapSearch').value.trim();
    fetch('static/data/groundwater_data.json')
        .then(res => res.json())
        .then(data => {
            const stations = data.monitoring_stations.filter(s => s.district.toLowerCase() === district.toLowerCase());
            stations.forEach(station => {
                if (window.mapInstance) {
                    const marker = new google.maps.Marker({
                        map: window.mapInstance,
                        position: { lat: station.coordinates.latitude, lng: station.coordinates.longitude },
                        label: `${station.measurements.water_level_mbgl}m`,
                        title: `Water Level: ${station.measurements.water_level_mbgl}m\nStation: ${station.station_id}`,
                        icon: {
                            url: 'https://maps.google.com/mapfiles/ms/icons/blue-dot.png'
                        }
                    });
                    window.waterLevelMarkers.push(marker);
                }
            });
        });
}

function hideWaterLevelMarkers() {
    window.waterLevelMarkers.forEach(marker => marker.setMap(null));
    window.waterLevelMarkers = [];
}

function showQualityZoneMarkers() {
    const district = document.getElementById('mapSearch').value.trim();
    fetch('static/data/groundwater_data.json')
        .then(res => res.json())
        .then(data => {
            const stations = data.monitoring_stations.filter(s => s.district.toLowerCase() === district.toLowerCase());
            stations.forEach(station => {
                if (window.mapInstance) {
                    // Color by water_quality_index
                    let color = 'green';
                    const wqi = station.measurements.water_quality_index;
                    if (wqi >= 90) color = 'darkgreen';
                    else if (wqi >= 70) color = 'green';
                    else if (wqi >= 50) color = 'orange';
                    else if (wqi >= 25) color = 'red';
                    else color = 'purple';
                    const marker = new google.maps.Marker({
                        map: window.mapInstance,
                        position: { lat: station.coordinates.latitude, lng: station.coordinates.longitude },
                        label: `${wqi}`,
                        title: `Quality Index: ${wqi}\nStation: ${station.station_id}`,
                        icon: {
                            url: `https://maps.google.com/mapfiles/ms/icons/${color}-dot.png`
                        }
                    });
                    window.qualityZoneMarkers.push(marker);
                }
            });
        });
}

function hideQualityZoneMarkers() {
    window.qualityZoneMarkers.forEach(marker => marker.setMap(null));
    window.qualityZoneMarkers = [];
}

function showWellMarkers() {
    const district = document.getElementById('mapSearch').value.trim();
    fetch('static/data/groundwater_data.json')
        .then(res => res.json())
        .then(data => {
            const stations = data.monitoring_stations.filter(s => s.district.toLowerCase() === district.toLowerCase());
            stations.forEach(station => {
                if (window.mapInstance) {
                    const marker = new google.maps.Marker({
                        map: window.mapInstance,
                        position: { lat: station.coordinates.latitude, lng: station.coordinates.longitude },
                        label: 'W',
                        title: `Well Station: ${station.station_id}`,
                        icon: {
                            url: 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png'
                        }
                    });
                    window.wellMarkers.push(marker);
                }
            });
        });
}

function hideWellMarkers() {
    window.wellMarkers.forEach(marker => marker.setMap(null));
    window.wellMarkers = [];
}

function showAlertMarkers() {
    const district = document.getElementById('mapSearch').value.trim();
    fetch('static/data/groundwater_data.json')
        .then(res => res.json())
        .then(data => {
            const stations = data.monitoring_stations.filter(s => s.district.toLowerCase() === district.toLowerCase());
            stations.forEach(station => {
                if (window.mapInstance) {
                    // Show alert if status is Critical or Declining
                    const status = station.trend_analysis.status;
                    if (status === 'Critical' || status === 'Declining') {
                        const marker = new google.maps.Marker({
                            map: window.mapInstance,
                            position: { lat: station.coordinates.latitude, lng: station.coordinates.longitude },
                            label: '!',
                            title: `Alert: ${status}\nStation: ${station.station_id}`,
                            icon: {
                                url: 'https://maps.google.com/mapfiles/ms/icons/red-dot.png'
                            }
                        });
                        window.alertMarkers.push(marker);
                    }
                }
            });
        });
}

function hideAlertMarkers() {
    window.alertMarkers.forEach(marker => marker.setMap(null));
    window.alertMarkers = [];
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