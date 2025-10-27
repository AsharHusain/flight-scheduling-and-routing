# constants.py
from datetime import timedelta

MINIMUM_LAYOVER_MINUTES: int = 45

AIRPORT_TIMEZONES: dict[str, timedelta] = {
    'JFK': timedelta(hours=-4), 'DFW': timedelta(hours=-5), 'SFO': timedelta(hours=-7),
    'LAX': timedelta(hours=-7), 'ATL': timedelta(hours=-4), 'LHR': timedelta(hours=+1),
    'CDG': timedelta(hours=+2), 'AMS': timedelta(hours=+2), 'DXB': timedelta(hours=+4),
    'BOM': timedelta(hours=+5.5), 'HND': timedelta(hours=+9), 'SYD': timedelta(hours=+11),
}

AIRLINE_NAMES: dict[str, str] = {
    'BA': 'British Airways', 'VS': 'Virgin Atlantic', 'AA': 'American Airlines',
    'AF': 'Air France', 'EK': 'Emirates', 'UA': 'United Airlines', 'DL': 'Delta Air Lines',
    'JL': 'Japan Airlines', 'NH': 'All Nippon Airways', 'AI': 'Air India',
    'KL': 'KLM Royal Dutch Airlines', 'QF': 'Qantas', 'SQ': 'Singapore Airlines',
    '6E': 'IndiGo', 'WF': 'Widerøe', '9W': 'Jet Airways'
}

AIRPORT_COORDINATES: dict[str, list[float]] = {
    'JFK': [40.6413, -73.7781], 'DFW': [32.8998, -97.0403], 'SFO': [37.6213, -122.3790],
    'LAX': [33.9416, -118.4085], 'ATL': [33.6407, -84.4277], 'LHR': [51.4700, -0.4543],
    'CDG': [49.0097, 2.5479], 'AMS': [52.3105, 4.7683], 'DXB': [25.2532, 55.3657],
    'BOM': [19.0896, 72.8656], 'HND': [35.5494, 139.7798], 'SYD': [ -33.9399, 151.1753]
}

# Airport full names for display
AIRPORT_NAMES: dict[str, str] = {
    'JFK': 'John F. Kennedy International Airport',
    'DFW': 'Dallas/Fort Worth International Airport', 
    'SFO': 'San Francisco International Airport',
    'LAX': 'Los Angeles International Airport',
    'ATL': 'Hartsfield-Jackson Atlanta International Airport',
    'LHR': 'London Heathrow Airport',
    'CDG': 'Charles de Gaulle Airport',
    'AMS': 'Amsterdam Airport Schiphol',
    'DXB': 'Dubai International Airport', 
    'BOM': 'Chhatrapati Shivaji Maharaj International Airport',
    'HND': 'Tokyo Haneda Airport',
    'SYD': 'Sydney Kingsford Smith Airport'
}