// Flight Tracker Dashboard JavaScript

const API_BASE = '';
let updateInterval;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initialized');
    updateStatus();
    updateStats();
    updateAircraft();
    updateOverhead();
    updateRecent();
    updateConfig();

    // Auto-refresh every 5 seconds
    updateInterval = setInterval(() => {
        updateStatus();
        updateStats();
        updateAircraft();
        updateOverhead();
        updateRecent();
    }, 5000);
});

// Update system status
async function updateStatus() {
    try {
        const response = await fetch(`${API_BASE}/api/status`);
        const data = await response.json();

        document.getElementById('uptime').textContent = data.uptime_formatted;
        document.getElementById('lastUpdate').textContent = formatTime(data.last_update);
        document.getElementById('radius').textContent = `${data.overhead_zone.radius_km} km`;
        document.getElementById('altitudeRange').textContent =
            `${data.overhead_zone.min_altitude_m}m - ${data.overhead_zone.max_altitude_m || '∞'}m`;

        // Update status indicator
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        statusDot.classList.remove('error');
        statusText.textContent = 'Running';
    } catch (error) {
        console.error('Error updating status:', error);
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        statusDot.classList.add('error');
        statusText.textContent = 'Error';
    }
}

// Update statistics
async function updateStats() {
    try {
        const response = await fetch(`${API_BASE}/api/stats`);
        const data = await response.json();

        document.getElementById('totalSeen').textContent = data.total_aircraft_seen;
        document.getElementById('apiCalls').textContent = data.api_calls;

        // Get aircraft counts
        const aircraftResponse = await fetch(`${API_BASE}/api/aircraft`);
        const aircraftData = await aircraftResponse.json();

        document.getElementById('currentAircraft').textContent = aircraftData.total;
        document.getElementById('overheadCount').textContent = aircraftData.overhead;
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Update aircraft list
async function updateAircraft() {
    try {
        const response = await fetch(`${API_BASE}/api/aircraft`);
        const data = await response.json();

        const listElement = document.getElementById('aircraftList');

        if (data.aircraft.length === 0) {
            listElement.innerHTML = '<p class="empty-state">No aircraft detected</p>';
            return;
        }

        listElement.innerHTML = data.aircraft.map(aircraft => `
            <div class="aircraft-item">
                <div class="aircraft-header">
                    <div class="aircraft-callsign">
                        ${aircraft.callsign || aircraft.icao}
                    </div>
                    <div class="aircraft-distance">
                        ${aircraft.distance_km ? aircraft.distance_km + ' km' : 'Unknown'}
                    </div>
                </div>
                <div class="aircraft-details">
                    <div class="aircraft-detail">
                        <span class="detail-label">ICAO</span>
                        <span class="detail-value">${aircraft.icao}</span>
                    </div>
                    <div class="aircraft-detail">
                        <span class="detail-label">Altitude</span>
                        <span class="detail-value">${aircraft.altitude ? aircraft.altitude + ' ft' : 'Unknown'}</span>
                    </div>
                    <div class="aircraft-detail">
                        <span class="detail-label">Speed</span>
                        <span class="detail-value">${aircraft.velocity ? aircraft.velocity + ' kts' : 'Unknown'}</span>
                    </div>
                    <div class="aircraft-detail">
                        <span class="detail-label">Heading</span>
                        <span class="detail-value">${aircraft.track ? aircraft.track + '°' : 'Unknown'}</span>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error updating aircraft:', error);
    }
}

// Update overhead aircraft
async function updateOverhead() {
    try {
        const response = await fetch(`${API_BASE}/api/overhead`);
        const data = await response.json();

        const listElement = document.getElementById('overheadList');

        if (data.aircraft.length === 0) {
            listElement.innerHTML = '<p class="empty-state">Waiting for aircraft...</p>';
            return;
        }

        listElement.innerHTML = data.aircraft.map(aircraft => `
            <div class="aircraft-item overhead">
                <div class="aircraft-header">
                    <div class="aircraft-callsign">
                        ${aircraft.callsign || aircraft.icao}
                        ${aircraft.origin_country ? `<br><small>${aircraft.origin_country} → ${aircraft.destination_country || 'Unknown'}</small>` : ''}
                    </div>
                    <div class="aircraft-distance">
                        ${aircraft.distance_km ? aircraft.distance_km + ' km away' : ''}
                    </div>
                </div>
                <div class="aircraft-details">
                    <div class="aircraft-detail">
                        <span class="detail-label">Altitude</span>
                        <span class="detail-value">${aircraft.altitude ? aircraft.altitude + ' ft' : 'Unknown'}</span>
                    </div>
                    <div class="aircraft-detail">
                        <span class="detail-label">Speed</span>
                        <span class="detail-value">${aircraft.velocity ? aircraft.velocity + ' kts' : 'Unknown'}</span>
                    </div>
                    <div class="aircraft-detail">
                        <span class="detail-label">Heading</span>
                        <span class="detail-value">${aircraft.track ? aircraft.track + '°' : 'Unknown'}</span>
                    </div>
                    <div class="aircraft-detail">
                        <span class="detail-label">V/S</span>
                        <span class="detail-value">${aircraft.vertical_rate ? aircraft.vertical_rate + ' ft/min' : 'Level'}</span>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error updating overhead:', error);
    }
}

// Update recent flights
async function updateRecent() {
    try {
        const response = await fetch(`${API_BASE}/api/recent`);
        const data = await response.json();

        const listElement = document.getElementById('recentFlights');

        if (data.flights.length === 0) {
            listElement.innerHTML = '<p class="empty-state">No recent flights</p>';
            return;
        }

        listElement.innerHTML = data.flights.reverse().map(flight => `
            <div class="recent-item">
                <div class="recent-info">
                    <div class="recent-callsign">${flight.callsign}</div>
                    <div class="recent-route">${flight.origin} → ${flight.destination}</div>
                </div>
                <div class="recent-time">${formatTime(flight.timestamp)}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error updating recent flights:', error);
    }
}

// Update configuration display
async function updateConfig() {
    try {
        const response = await fetch(`${API_BASE}/api/config`);
        const data = await response.json();

        const configElement = document.getElementById('configDisplay');

        configElement.innerHTML = `
            <div class="config-item">
                <span class="config-label">Location</span>
                <span class="config-value">${data.location.latitude.toFixed(4)}, ${data.location.longitude.toFixed(4)}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Detection Radius</span>
                <span class="config-value">${data.overhead_zone.radius_km} km</span>
            </div>
            <div class="config-item">
                <span class="config-label">Min Altitude</span>
                <span class="config-value">${data.overhead_zone.min_altitude_m} m</span>
            </div>
            <div class="config-item">
                <span class="config-label">Max Altitude</span>
                <span class="config-value">${data.overhead_zone.max_altitude_m || 'Unlimited'}</span>
            </div>
            <div class="config-item">
                <span class="config-label">API Provider</span>
                <span class="config-value">${data.api.provider}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Data Source</span>
                <span class="config-value">${data.adsb.data_source}</span>
            </div>
            <div class="config-item">
                <span class="config-label">Update Interval</span>
                <span class="config-value">${data.adsb.update_interval}s</span>
            </div>
        `;
    } catch (error) {
        console.error('Error updating config:', error);
    }
}

// Manual data update
async function updateData() {
    try {
        const response = await fetch(`${API_BASE}/api/update`);
        const data = await response.json();

        if (data.success) {
            updateStats();
            updateAircraft();
            updateOverhead();
        }
    } catch (error) {
        console.error('Error updating data:', error);
    }
}

// Format timestamp
function formatTime(timestamp) {
    if (!timestamp) return '-';

    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);

    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;

    return date.toLocaleTimeString();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
