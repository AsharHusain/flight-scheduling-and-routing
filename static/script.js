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
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    let currentResults = {};

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        loadingSpinner.classList.remove('hidden');
        resultsTabs.classList.add('hidden');
        routeLayer.clearLayers();
        const requestData = {
            start: document.getElementById('start-airport').value.toUpperCase(),
            end: document.getElementById('end-airport').value.toUpperCase(),
            preferences: {
                preferred_airline: document.getElementById('preferred-airline').value || null,
                avoid_airline: document.getElementById('avoid-airline').value || null,
            },
        };
        try {
            const response = await fetch('/api/find-routes', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData),
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            currentResults = await response.json();
            displayAllResults(currentResults, requestData.start);
            resultsTabs.classList.remove('hidden');
        } catch (error) {
            alert(`Error: Could not fetch flight data. ${error.message}`);
        } finally {
            loadingSpinner.classList.add('hidden');
        }
    });
    
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

                content += `<p><strong>Total Cost:</strong> $${totalCost.toFixed(2)} | <strong>Total Time:</strong> ${Math.floor(totalDuration)}h ${Math.round((totalDuration % 1) * 60)}m</p>`;
                result.path.forEach((leg, index) => {
                    const airlineName = airlineNames[leg.airline] || 'Unknown Airline';
                    const airlineHTML = `<span class="airline-code" title="${airlineName}">${leg.airline}</span>`;
                    const origin = index === 0 ? startNode : result.path[index - 1].destination;
                    content += `<div class="leg"><strong>${airlineHTML} ${leg.flight_number}</strong>: ${origin} → ${leg.destination}</div>`;
                });
            } else {
                content = '<p>No route found for this option.</p>';
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
            
            if (index === 0) marker.bindPopup(`<b>Origin</b><br>${airportCode}`);
            else if (index === points.length - 1) marker.bindPopup(`<b>Destination</b><br>${airportCode}`);
            else marker.bindPopup(`<b>Layover</b><br>${airportCode}`);
        });

        const polyline = L.polyline(points.filter(p => p), { color: 'var(--primary-color)', weight: 3 }).addTo(routeLayer);
        
        if (polyline.getBounds().isValid()) {
            map.fitBounds(polyline.getBounds().pad(0.2));
        }
    }
});