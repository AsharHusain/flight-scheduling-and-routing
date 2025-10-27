// static/script.js
document.addEventListener('DOMContentLoaded', () => {
    const map = L.map('map').setView([20, 0], 2);
    // Use the light-themed map tile layer
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        subdomains: 'abcd', maxZoom: 19
    }).addTo(map);
    let routeLayer = L.layerGroup().addTo(map);

    const form = document.getElementById('flight-form');
    const loadingSpinner = document.getElementById('loading-spinner');
    const resultsTabs = document.getElementById('results-tabs');
    const collisionPanel = document.getElementById('collision-panel');
    const viewCollisionsBtn = document.getElementById('view-collisions-btn');
    const closeCollisionBtn = document.getElementById('close-collision-btn');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    let currentResults = {};

    // Collision panel handlers
    viewCollisionsBtn.addEventListener('click', async () => {
        resultsTabs.classList.add('hidden');
        collisionPanel.classList.remove('hidden');
        await loadCollisionData();
    });

    closeCollisionBtn.addEventListener('click', () => {
        collisionPanel.classList.add('hidden');
        if (Object.keys(currentResults).length > 0) {
            resultsTabs.classList.remove('hidden');
        }
    });

    async function loadCollisionData() {
        const collisionLoading = document.getElementById('collision-loading');
        const collisionData = document.getElementById('collision-data');
        
        collisionLoading.classList.remove('hidden');
        collisionData.innerHTML = '';

        try {
            const response = await fetch('/api/collision-report');
            if (!response.ok) throw new Error('Failed to fetch collision data');
            
            const data = await response.json();
            displayCollisionData(data);
        } catch (error) {
            collisionData.innerHTML = `<p class="error">❌ Error loading collision data: ${error.message}</p>`;
        } finally {
            collisionLoading.classList.add('hidden');
        }
    }

    function displayCollisionData(data) {
        const collisionData = document.getElementById('collision-data');
        const summary = data.summary;
        const breakdown = summary.conflict_breakdown;

        let html = `
            <div class="collision-summary">
                <h3>📊 Overall Statistics</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${summary.total_flights}</div>
                        <div class="stat-label">Total Flights</div>
                    </div>
                    <div class="stat-card success">
                        <div class="stat-value">${summary.successful}</div>
                        <div class="stat-label">✅ Conflict-Free</div>
                    </div>
                    <div class="stat-card error">
                        <div class="stat-value">${summary.failed}</div>
                        <div class="stat-label">❌ With Conflicts</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${((summary.successful / summary.total_flights) * 100).toFixed(1)}%</div>
                        <div class="stat-label">Success Rate</div>
                    </div>
                </div>
            </div>

            <div class="conflict-breakdown">
                <h3>🔍 Conflict Types</h3>
                <div class="breakdown-list">
                    <div class="breakdown-item">
                        <span class="breakdown-label">✈️ Aircraft Conflicts</span>
                        <span class="breakdown-value">${breakdown.aircraft_conflicts}</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">🛫 Runway Conflicts</span>
                        <span class="breakdown-value">${breakdown.runway_conflicts}</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">🏢 Gate Capacity Issues</span>
                        <span class="breakdown-value">${breakdown.gate_conflicts}</span>
                    </div>
                    <div class="breakdown-item">
                        <span class="breakdown-label">📍 Positioning Conflicts</span>
                        <span class="breakdown-value">${breakdown.positioning_conflicts}</span>
                    </div>
                </div>
            </div>

            <div class="failed-flights-section">
                <h3>⚠️ Flights with Conflicts (${data.failed_flights.length} total)</h3>
                <div class="failed-flights-list">
                    ${data.failed_flights.slice(0, 20).map(flight => 
                        `<span class="failed-flight-badge">${flight}</span>`
                    ).join('')}
                    ${data.failed_flights.length > 20 ? 
                        `<span class="more-indicator">+${data.failed_flights.length - 20} more</span>` 
                        : ''}
                </div>
            </div>

            <div class="conflict-details">
                <h3>📝 Sample Conflicts (First 10)</h3>
                <div class="conflicts-list">
                    ${data.conflicts.slice(0, 10).map(conflict => 
                        `<div class="conflict-item">${conflict}</div>`
                    ).join('')}
                </div>
            </div>
        `;

        collisionData.innerHTML = html;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        loadingSpinner.classList.remove('hidden');
        resultsTabs.classList.add('hidden');
        collisionPanel.classList.add('hidden');
        routeLayer.clearLayers();
        
        const requestData = {
            start: document.getElementById('start-airport').value.toUpperCase(),
            end: document.getElementById('end-airport').value.toUpperCase(),
            preferences: {
                preferred_airline: document.getElementById('preferred-airline').value || null,
                avoid_airline: document.getElementById('avoid-airline').value || null,
            },
        };

        console.log('Sending request:', requestData);
        
        try {
            const response = await fetch('/api/find-routes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData),
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            currentResults = await response.json();
            
            console.log('Received results:', currentResults);
            
            // Check if any routes were found
            const hasAnyRoute = Object.values(currentResults).some(result => result.status === 'found');
            
            if (!hasAnyRoute) {
                alert(`No routes found between ${requestData.start} and ${requestData.end}. This may be due to:\n• No connecting flights available\n• Avoided airline blocking all routes\n• Insufficient layover times\n\nTry adjusting your preferences or selecting different airports.`);
                return;
            }
            
            displayAllResults(currentResults, requestData.start);
            resultsTabs.classList.remove('hidden');
            
            // Validate path for collisions
            await validateCurrentPath(currentResults);
        } catch (error) {
            alert(`Error: Could not fetch flight data. ${error.message}`);
        } finally {
            loadingSpinner.classList.add('hidden');
        }
    });

    async function validateCurrentPath(results) {
        // Get all flight numbers from all routes
        const allFlightNumbers = new Set();
        ['cheapest', 'fastest', 'best'].forEach(type => {
            if (results[type]?.path) {
                results[type].path.forEach(leg => allFlightNumbers.add(leg.flight_number));
            }
        });

        if (allFlightNumbers.size === 0) return;

        try {
            const response = await fetch('/api/validate-path', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ flight_numbers: Array.from(allFlightNumbers) }),
            });

            if (response.ok) {
                const validation = await response.json();
                if (validation.conflicts_detected) {
                    showCollisionWarning(validation.conflicted_flights);
                }
            }
        } catch (error) {
            console.error('Error validating path:', error);
        }
    }

    function showCollisionWarning(conflicts) {
        // Add warning to results panel
        const warning = document.createElement('div');
        warning.className = 'collision-warning';
        warning.innerHTML = `
            <div class="warning-header">⚠️ Schedule Conflicts Detected</div>
            <p>${conflicts.length} flight(s) in your routes have scheduling conflicts:</p>
            <div class="conflict-flights">
                ${conflicts.map(c => `<span class="conflict-badge">${c.flight}</span>`).join(' ')}
            </div>
            <p class="warning-note">These flights may have aircraft turnaround, runway, or gate conflicts. View details in Schedule Conflicts panel.</p>
        `;
        
        const resultsPanel = document.getElementById('results-tabs');
        resultsPanel.insertBefore(warning, resultsPanel.firstChild);
    }
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            const tabId = button.dataset.tab;
            tabPanes.forEach(pane => pane.classList.toggle('active', pane.id === tabId));
            const startNode = document.getElementById('start-airport').value.toUpperCase();
            drawMapRoute(currentResults[tabId]?.path, startNode);
        });
    });

    function displayAllResults(results, startNode) {
        for (const [type, result] of Object.entries(results)) {
            const pane = document.getElementById(type);
            let content = '';
            if (result.status === 'found') {
                const totalCost = result.path.reduce((acc, leg) => acc + leg.cost, 0);
                const firstLeg = result.path[0];
                const lastLeg = result.path[result.path.length - 1];
                const totalDuration = (new Date(lastLeg.arrival_utc) - new Date(firstLeg.departure_utc)) / (1000 * 60 * 60);

                // Check for negative duration (data error)
                if (totalDuration < 0) {
                    content = '<p class="error">⚠️ This route contains flights with invalid times (arrival before departure). Please contact support.</p>';
                    pane.innerHTML = content;
                    continue;
                }

                content += `<p><strong>Total Cost:</strong> $${totalCost.toFixed(2)} | <strong>Total Time:</strong> ${Math.floor(totalDuration)}h ${Math.round((totalDuration % 1) * 60)}m | <strong>Stops:</strong> ${result.path.length - 1}</p>`;
                result.path.forEach((leg, index) => {
                    const airlineName = airlineNames[leg.airline] || 'Unknown Airline';
                    const airlineHTML = `<span class="airline-code" title="${airlineName}">${leg.airline}</span>`;
                    const origin = index === 0 ? startNode : result.path[index - 1].destination;
                    const originName = airportNames[origin] || origin;
                    const destName = airportNames[leg.destination] || leg.destination;
                    
                    const depTime = new Date(leg.departure_utc);
                    const arrTime = new Date(leg.arrival_utc);
                    const duration = (arrTime - depTime) / (1000 * 60 * 60);
                    
                    // Skip flights with negative duration (data errors)
                    if (duration < 0) {
                        content += `
                            <div class="leg error-leg">
                                <div class="leg-header">
                                    <strong>${airlineHTML} ${leg.flight_number}</strong>
                                    <span class="error-badge">⚠️ Invalid Times</span>
                                </div>
                                <p class="error">This flight has arrival time before departure time (data error)</p>
                            </div>
                        `;
                        return; // Skip to next iteration
                    }
                    
                    content += `
                        <div class="leg">
                            <div class="leg-header">
                                <strong>${airlineHTML} ${leg.flight_number}</strong>
                                <span class="leg-cost">$${leg.cost}</span>
                            </div>
                            <div class="leg-route">
                                <span class="airport-info">${originName} (${origin})</span>
                                <span class="route-arrow">→</span>
                                <span class="airport-info">${destName} (${leg.destination})</span>
                            </div>
                            <div class="leg-details">
                                <span>🛫 ${depTime.toUTCString()}</span>
                                <span>🛬 ${arrTime.toUTCString()}</span>
                                <span>⏱️ ${Math.floor(duration)}h ${Math.round((duration % 1) * 60)}m</span>
                                <span>✈️ ${leg.aircraft}</span>
                            </div>
                        </div>
                    `;
                });
            } else {
                content = '<p class="no-route">❌ No route found for this option.</p>';
            }
            pane.innerHTML = content;
        }
        // Activate the first tab to show initial results
        document.querySelector('.tab-btn[data-tab="cheapest"]').click();
    }
    
    function drawMapRoute(path, startNode) {
        routeLayer.clearLayers();
        if (!path || !airportCoordinates[startNode]) return;

        const points = [airportCoordinates[startNode], ...path.map(leg => airportCoordinates[leg.destination])];
        
        points.forEach((p, index) => {
            if(!p) return; // Skip if coordinates are missing
            const marker = L.marker(p).addTo(routeLayer);
            let airportCode = '';
            if (index === 0) airportCode = startNode;
            else airportCode = path[index - 1].destination;
            
            const airportName = airportNames[airportCode] || airportCode;
            
            if (index === 0) marker.bindPopup(`<b>🛫 Origin</b><br>${airportName}<br>(${airportCode})`);
            else if (index === points.length - 1) marker.bindPopup(`<b>🛬 Destination</b><br>${airportName}<br>(${airportCode})`);
            else marker.bindPopup(`<b>🔄 Layover</b><br>${airportName}<br>(${airportCode})`);
        });

        const polyline = L.polyline(points.filter(p => p), { color: 'var(--primary-color)', weight: 3 }).addTo(routeLayer);
        
        if (polyline.getBounds().isValid()) {
            map.fitBounds(polyline.getBounds().pad(0.2));
        }
    }
});