"""
This module runs the Flask web server for the flight router.
It serves the main HTML page and provides the API endpoint for finding flight paths.
"""
from typing import Dict, Any, List, Optional
from flask import Flask, render_template, request, jsonify
from flight_engine import build_graph, find_optimal_path
from constants import AIRPORT_COORDINATES, AIRLINE_NAMES, AIRPORT_NAMES

app = Flask(__name__)

# Load data and build graph on startup
print("Loading flight data and building graph...")
FLIGHT_DATA_FILE = "data/advanced_flights.csv"
FLIGHT_GRAPH, AVAILABLE_AIRPORTS = build_graph(FLIGHT_DATA_FILE)
print("Graph built successfully. Server is ready.")

def format_path_for_json(path: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
    """Converts datetime objects in a path to ISO 8601 strings for JSON serialization."""
    if not path:
        return None
    formatted_path = []
    for leg in path:
        new_leg = leg.copy()
        new_leg['departure_utc'] = leg['departure_utc'].isoformat()
        new_leg['arrival_utc'] = leg['arrival_utc'].isoformat()
        formatted_path.append(new_leg)
    return formatted_path

@app.route('/')
def index() -> str:
    """Renders the main user interface page."""
    return render_template(
        'index.html', 
        airports=sorted(list(AVAILABLE_AIRPORTS or [])),
        airline_data=AIRLINE_NAMES,
        coordinate_data=AIRPORT_COORDINATES,
        airport_name_data=AIRPORT_NAMES
    )

@app.route('/api/constants')
def get_constants():
    """API endpoint to serve JavaScript constants as JSON."""
    return jsonify({
        'airlineNames': AIRLINE_NAMES,
        'airportCoordinates': AIRPORT_COORDINATES,
        'airportNames': AIRPORT_NAMES
    })

@app.route('/api/find-routes', methods=['POST'])
def find_routes_api() -> Any:
    """API endpoint that receives flight search criteria and returns results."""
    data = request.json
    start, end = data.get('start', '').upper(), data.get('end', '').upper()
    prefs = data.get('preferences', {})

    print(f"API call received: Find routes from {start} to {end} with prefs: {prefs}")

    if not FLIGHT_GRAPH or not start or not end:
        return jsonify({"error": "Invalid input or graph not loaded"}), 400

    results: Dict[str, Any] = {}
    for r_type in ['cost', 'time', 'best']:
        priority_name = 'cheapest' if r_type == 'cost' else 'fastest' if r_type == 'time' else 'best'
        path, value = find_optimal_path(FLIGHT_GRAPH, start, end, r_type, prefs)
        results[priority_name] = {"path": format_path_for_json(path), "value": value, "status": "found" if path else "not_found"}

    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5001)