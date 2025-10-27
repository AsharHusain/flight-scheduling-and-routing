"""
Collision Detection and Handling Module for Flight Scheduling System

This module handles:
1. Aircraft turnaround time conflicts
2. Airport gate capacity conflicts  
3. Runway time slot conflicts
4. Flight schedule validation
"""

from datetime import datetime, timedelta
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict

# Configuration constants
MINIMUM_TURNAROUND_MINUTES = 45  # Minimum time between flights for same aircraft
MINIMUM_RUNWAY_SEPARATION_MINUTES = 5  # Minimum time between runway operations
MAX_GATES_PER_AIRPORT = {
    'JFK': 128, 'LHR': 115, 'CDG': 76, 'AMS': 72, 'DXB': 97,
    'BOM': 62, 'HND': 78, 'SYD': 46, 'DFW': 165, 'SFO': 57,
    'LAX': 146, 'ATL': 195
}

class CollisionDetector:
    """Detects and manages flight scheduling conflicts."""
    
    def __init__(self):
        """Initialize collision tracking structures."""
        # Track aircraft schedules: aircraft_id -> list of (departure_time, arrival_time, route)
        self.aircraft_schedules: Dict[str, List[Tuple[datetime, datetime, str, str]]] = defaultdict(list)
        
        # Track runway usage: airport -> list of (time, operation_type, flight_number)
        self.runway_schedules: Dict[str, List[Tuple[datetime, str, str]]] = defaultdict(list)
        
        # Track gate usage: airport -> list of (start_time, end_time, flight_number)
        self.gate_schedules: Dict[str, List[Tuple[datetime, datetime, str]]] = defaultdict(list)
        
        # Track active flights by time slot
        self.active_flights: Set[str] = set()
    
    def check_aircraft_conflict(self, aircraft_id: str, flight_number: str, 
                                departure_airport: str, departure_time: datetime,
                                arrival_airport: str, arrival_time: datetime) -> Optional[str]:
        """
        Check if an aircraft has sufficient turnaround time between flights.
        
        Returns:
            Error message if conflict exists, None otherwise
        """
        if aircraft_id not in self.aircraft_schedules:
            return None
        
        # Sort existing flights by departure time for proper chronological checking
        sorted_flights = sorted(self.aircraft_schedules[aircraft_id], key=lambda x: x[0])
        
        for prev_dep, prev_arr, prev_dest, prev_flight in sorted_flights:
            # Check if there's temporal overlap (new flight departs before previous lands)
            if departure_time < prev_arr:
                time_diff = (prev_arr - departure_time).total_seconds() / 60
                return (f"❌ Aircraft conflict: {aircraft_id} is still flying {prev_flight} "
                       f"(lands at {prev_arr.strftime('%Y-%m-%d %H:%M')} UTC) but {flight_number} "
                       f"departs at {departure_time.strftime('%Y-%m-%d %H:%M')} UTC "
                       f"(conflict: {time_diff:.0f} min overlap)")
            
            # Only check turnaround if this flight is after the previous one
            if departure_time >= prev_arr:
                turnaround_time = (departure_time - prev_arr).total_seconds() / 60
                
                # Check if aircraft is at the right location and has sufficient turnaround
                if prev_dest == departure_airport:
                    if turnaround_time < MINIMUM_TURNAROUND_MINUTES:
                        return (f"❌ Insufficient turnaround: {aircraft_id} needs {MINIMUM_TURNAROUND_MINUTES} min, "
                               f"but only {turnaround_time:.0f} min available between {prev_flight} and {flight_number} "
                               f"at {departure_airport}")
                else:
                    # Aircraft is at different location - needs repositioning
                    # This is acceptable if enough time, but we'll flag if it's unrealistic
                    if turnaround_time < 120:  # Minimum 2 hours for repositioning flight
                        return (f"❌ Aircraft positioning conflict: {aircraft_id} is at {prev_dest} "
                               f"after {prev_flight} (lands {prev_arr.strftime('%H:%M')}) "
                               f"but needs to be at {departure_airport} for {flight_number} "
                               f"(departs {departure_time.strftime('%H:%M')}) - "
                               f"only {turnaround_time:.0f} min for repositioning (need 120 min)")
        
        return None
    
    def check_runway_conflict(self, airport: str, operation_time: datetime, 
                            operation_type: str, flight_number: str) -> Optional[str]:
        """
        Check if a runway operation conflicts with existing schedule.
        
        Args:
            airport: Airport code
            operation_time: Time of takeoff or landing
            operation_type: 'departure' or 'arrival'
            flight_number: Flight identifier
            
        Returns:
            Error message if conflict exists, None otherwise
        """
        if airport not in self.runway_schedules:
            return None
        
        for scheduled_time, scheduled_op, scheduled_flight in self.runway_schedules[airport]:
            time_diff = abs((operation_time - scheduled_time).total_seconds() / 60)
            
            if time_diff < MINIMUM_RUNWAY_SEPARATION_MINUTES:
                return (f"❌ Runway conflict at {airport}: {flight_number} ({operation_type}) at "
                       f"{operation_time.strftime('%H:%M')} conflicts with {scheduled_flight} "
                       f"({scheduled_op}) at {scheduled_time.strftime('%H:%M')} "
                       f"(only {time_diff:.1f} min separation, need {MINIMUM_RUNWAY_SEPARATION_MINUTES} min)")
        
        return None
    
    def check_gate_capacity(self, airport: str, arrival_time: datetime, 
                           departure_time: datetime, flight_number: str) -> Optional[str]:
        """
        Check if airport has gate capacity for the flight.
        
        Args:
            airport: Airport code
            arrival_time: When flight arrives (or scheduled departure for origin airport)
            departure_time: When flight departs
            flight_number: Flight identifier
            
        Returns:
            Error message if no gates available, None otherwise
        """
        max_gates = MAX_GATES_PER_AIRPORT.get(airport, 50)  # Default 50 gates
        
        # Count overlapping gate usage
        overlapping_count = 0
        for gate_start, gate_end, gate_flight in self.gate_schedules[airport]:
            # Check if time ranges overlap
            # Two ranges overlap if: start1 < end2 AND start2 < end1
            if arrival_time < gate_end and gate_start < departure_time:
                overlapping_count += 1
        
        if overlapping_count >= max_gates:
            return (f"❌ Gate capacity exceeded at {airport}: {overlapping_count + 1}/{max_gates} gates needed "
                   f"when adding {flight_number}'s gate time "
                   f"({arrival_time.strftime('%H:%M')}-{departure_time.strftime('%H:%M')})")
        
        return None
    
    def register_flight(self, flight_data: Dict[str, Any]) -> List[str]:
        """
        Register a flight and check for all types of conflicts.
        
        Args:
            flight_data: Dictionary containing flight information
            
        Returns:
            List of conflict messages (empty if no conflicts)
        """
        conflicts = []
        
        # Extract flight details
        flight_num = flight_data.get('flight_number', 'UNKNOWN')
        aircraft = flight_data.get('aircraft', 'UNKNOWN')
        airline = flight_data.get('airline', 'XX')
        source = flight_data.get('source_airport', '')
        dest = flight_data.get('destination_airport', '')
        dep_time = flight_data.get('departure_time')
        arr_time = flight_data.get('arrival_time')
        
        # Validate times
        if not dep_time or not arr_time:
            conflicts.append(f"❌ Missing departure or arrival time for {flight_num}")
            return conflicts
            
        if arr_time <= dep_time:
            conflicts.append(f"❌ Invalid times for {flight_num}: arrival ({arr_time}) before/equal departure ({dep_time})")
            return conflicts
        
        # Create unique aircraft identifier
        # Format: Airline-Aircraft-FlightNumber to ensure each physical aircraft is unique
        # This handles cases where same airline/aircraft fly different routes
        aircraft_id = f"{airline}-{aircraft}-{flight_num}"
        
        # Check aircraft conflicts
        aircraft_conflict = self.check_aircraft_conflict(
            aircraft_id, flight_num, source, dep_time, dest, arr_time
        )
        if aircraft_conflict:
            conflicts.append(aircraft_conflict)
        
        # Check departure runway conflict
        dep_runway_conflict = self.check_runway_conflict(
            source, dep_time, 'departure', flight_num
        )
        if dep_runway_conflict:
            conflicts.append(dep_runway_conflict)
        
        # Check arrival runway conflict
        arr_runway_conflict = self.check_runway_conflict(
            dest, arr_time, 'arrival', flight_num
        )
        if arr_runway_conflict:
            conflicts.append(arr_runway_conflict)
        
        # Check departure gate capacity
        gate_buffer = timedelta(minutes=30)  # Gate occupied 30 min before departure
        dep_gate_conflict = self.check_gate_capacity(
            source, dep_time - gate_buffer, dep_time, flight_num
        )
        if dep_gate_conflict:
            conflicts.append(dep_gate_conflict)
        
        # Check arrival gate capacity (gate occupied for 45 min after arrival)
        arr_gate_buffer = timedelta(minutes=45)
        arr_gate_conflict = self.check_gate_capacity(
            dest, arr_time, arr_time + arr_gate_buffer, flight_num
        )
        if arr_gate_conflict:
            conflicts.append(arr_gate_conflict)
        
        # If no conflicts, register the flight
        if not conflicts:
            self.aircraft_schedules[aircraft_id].append((dep_time, arr_time, dest, flight_num))
            self.runway_schedules[source].append((dep_time, 'departure', flight_num))
            self.runway_schedules[dest].append((arr_time, 'arrival', flight_num))
            self.gate_schedules[source].append((dep_time - gate_buffer, dep_time, flight_num))
            self.gate_schedules[dest].append((arr_time, arr_time + arr_gate_buffer, flight_num))
            self.active_flights.add(flight_num)
        
        return conflicts
    
    def validate_flight_schedule(self, flights: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate an entire flight schedule for conflicts.
        
        Args:
            flights: List of flight dictionaries
            
        Returns:
            Dictionary with validation results
        """
        all_conflicts = []
        successful_flights = []
        failed_flights = []
        
        # Sort flights by departure time to process in chronological order
        sorted_flights = sorted(flights, key=lambda f: f.get('departure_time', datetime.min))
        
        for flight in sorted_flights:
            conflicts = self.register_flight(flight)
            
            if conflicts:
                failed_flights.append({
                    'flight': flight.get('flight_number'),
                    'conflicts': conflicts
                })
                all_conflicts.extend(conflicts)
            else:
                successful_flights.append(flight.get('flight_number'))
        
        return {
            'total_flights': len(flights),
            'successful': len(successful_flights),
            'failed': len(failed_flights),
            'conflicts': all_conflicts,
            'successful_flights': successful_flights,
            'failed_flights': failed_flights,
            'conflict_summary': self._generate_conflict_summary(all_conflicts)
        }
    
    def _generate_conflict_summary(self, conflicts: List[str]) -> Dict[str, int]:
        """Generate a summary of conflict types."""
        summary = {
            'aircraft_conflicts': 0,
            'runway_conflicts': 0,
            'gate_conflicts': 0,
            'positioning_conflicts': 0
        }
        
        for conflict in conflicts:
            if 'Aircraft conflict' in conflict or 'turnaround' in conflict:
                summary['aircraft_conflicts'] += 1
            elif 'Runway conflict' in conflict:
                summary['runway_conflicts'] += 1
            elif 'Gate capacity' in conflict:
                summary['gate_conflicts'] += 1
            elif 'positioning' in conflict:
                summary['positioning_conflicts'] += 1
        
        return summary
    
    def get_airport_statistics(self, airport: str) -> Dict[str, Any]:
        """Get statistics for a specific airport."""
        runway_ops = len(self.runway_schedules.get(airport, []))
        gate_usage = len(self.gate_schedules.get(airport, []))
        max_gates = MAX_GATES_PER_AIRPORT.get(airport, 50)
        
        return {
            'airport': airport,
            'runway_operations': runway_ops,
            'gate_reservations': gate_usage,
            'max_gates': max_gates,
            'utilization': f"{(gate_usage / max_gates * 100):.1f}%" if max_gates > 0 else "N/A"
        }
    
    def reset(self):
        """Clear all tracked schedules."""
        self.aircraft_schedules.clear()
        self.runway_schedules.clear()
        self.gate_schedules.clear()
        self.active_flights.clear()


def validate_csv_schedule(csv_file: str) -> Dict[str, Any]:
    """
    Load and validate a complete flight schedule from CSV.
    
    Args:
        csv_file: Path to CSV file containing flight data
        
    Returns:
        Dictionary with validation results
    """
    import csv
    from datetime import datetime
    
    detector = CollisionDetector()
    flights = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                flight = {
                    'flight_number': row['FlightNumber'],
                    'airline': row['Airline'],
                    'aircraft': row['AircraftType'],
                    'source_airport': row['SourceAirport'],
                    'destination_airport': row['DestinationAirport'],
                    'departure_time': datetime.fromisoformat(row['DepartureDateTimeUTC'].replace('Z', '+00:00')),
                    'arrival_time': datetime.fromisoformat(row['ArrivalDateTimeUTC'].replace('Z', '+00:00')),
                    'cost': row['Cost']
                }
                flights.append(flight)
        
        return detector.validate_flight_schedule(flights)
        
    except Exception as e:
        return {
            'error': f"Failed to validate schedule: {str(e)}",
            'total_flights': 0,
            'successful': 0,
            'failed': 0
        }
