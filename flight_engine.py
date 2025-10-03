# flight_engine.py
import csv
import heapq
import itertools
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Set, Tuple, Optional, Any
from constants import MINIMUM_LAYOVER_MINUTES

Graph = Dict[str, List[Dict[str, Any]]]
Path = List[Dict[str, Any]]
UserPreferences = Dict[str, Optional[str]]

def build_graph(csv_file: str) -> Tuple[Optional[Graph], Optional[Set[str]]]:
    """Reads flight data from a CSV and builds a graph representation."""
    graph: Graph = {}
    airports: Set[str] = set()
    try:
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                source, dest = row["SourceAirport"].strip().upper(), row["DestinationAirport"].strip().upper()
                dep_str, arr_str = row["DepartureDateTimeUTC"].replace('Z', '+00:00'), row["ArrivalDateTimeUTC"].replace('Z', '+00:00')
                
                flight_details = {
                    "destination": dest, "flight_number": row["FlightNumber"], "airline": row["Airline"],
                    "departure_utc": datetime.fromisoformat(dep_str), "arrival_utc": datetime.fromisoformat(arr_str),
                    "cost": int(row["Cost"]), "aircraft": row["AircraftType"],
                }
                airports.add(source)
                airports.add(dest)
                graph.setdefault(source, []).append(flight_details)
        return graph, airports
    except (FileNotFoundError, KeyError) as e:
        print(f"Error reading or parsing flight data: {e}")
        return None, None

def _calculate_priority_score(flight: Dict[str, Any], layover: timedelta, prefs: UserPreferences) -> float:
    """Calculates a 'best' score based on duration, cost, and user preferences."""
    score = (flight['arrival_utc'] - flight['departure_utc'] + layover).total_seconds() / 60
    score += flight['cost'] * 2.0  # Weight cost heavily in the 'best' score
    
    if prefs.get('preferred_airline') and flight['airline'] == prefs['preferred_airline']:
        score *= 0.8  # 20% score reduction for preferred airline
    if prefs.get('avoid_airline') and flight['airline'] == prefs['avoid_airline']:
        score *= 1.5  # 50% score penalty for avoided airline
        
    return score

def find_optimal_path(graph: Graph, start: str, end: str, priority_type: str, prefs: UserPreferences) -> Tuple[Optional[Path], float]:
    """Finds the best flight path using a Dijkstra-like algorithm."""
    aware_min_time = datetime.min.replace(tzinfo=timezone.utc)
    pq: List[Tuple[float, int, datetime, str, Path]] = [(0.0, 0, aware_min_time, start, [])]
    visited: Dict[Tuple[str, datetime], float] = {}
    tie_breaker = itertools.count()

    while pq:
        priority_val, _, arr_time, airport, path = heapq.heappop(pq)

        if visited.get((airport, arr_time), float('inf')) <= priority_val:
            continue
        visited[(airport, arr_time)] = priority_val

        if airport == end:
            return path, priority_val

        for flight in graph.get(airport, []):
            layover = flight["departure_utc"] - arr_time
            if path and layover.total_seconds() / 60 < MINIMUM_LAYOVER_MINUTES:
                continue

            new_path = path + [flight]
            
            if priority_type == 'cost':
                new_priority_val = priority_val + flight["cost"]
            elif priority_type == 'time':
                total_duration = flight["arrival_utc"] - new_path[0]["departure_utc"]
                new_priority_val = total_duration.total_seconds() / 60
            else: # 'best'
                score = _calculate_priority_score(flight, layover if path else timedelta(0), prefs)
                new_priority_val = priority_val + score

            # Add a large penalty for avoided airlines in cost/time mode to effectively block them
            if prefs.get('avoid_airline') and flight['airline'] == prefs['avoid_airline'] and priority_type != 'best':
                new_priority_val += 100000 
            
            heapq.heappush(pq, (new_priority_val, next(tie_breaker), flight["arrival_utc"], flight["destination"], new_path))
            
    return None, float('inf')