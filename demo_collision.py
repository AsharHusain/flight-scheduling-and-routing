"""
Interactive demonstration of collision detection system.
Shows examples of different types of conflicts.
"""

from datetime import datetime, timedelta
from collision_handler import CollisionDetector

def demo_collision_detection():
    print("=" * 80)
    print("COLLISION DETECTION SYSTEM - INTERACTIVE DEMO")
    print("=" * 80)
    print()
    
    detector = CollisionDetector()
    
    # Example 1: Successful flight registration
    print("📋 Example 1: Valid Flight Registration")
    print("-" * 80)
    flight1 = {
        'flight_number': 'BA112',
        'airline': 'BA',
        'aircraft': 'B777',
        'source_airport': 'JFK',
        'destination_airport': 'LHR',
        'departure_time': datetime(2025, 10, 28, 11, 0),
        'arrival_time': datetime(2025, 10, 28, 23, 0)
    }
    conflicts = detector.register_flight(flight1)
    if conflicts:
        print("❌ Conflicts:")
        for c in conflicts:
            print(f"   {c}")
    else:
        print(f"✅ {flight1['flight_number']} registered successfully!")
        print(f"   Route: {flight1['source_airport']} → {flight1['destination_airport']}")
        print(f"   Departure: {flight1['departure_time'].strftime('%Y-%m-%d %H:%M')} UTC")
        print(f"   Arrival: {flight1['arrival_time'].strftime('%Y-%m-%d %H:%M')} UTC")
    print()
    
    # Example 2: Aircraft conflict - same aircraft, overlapping time
    print("📋 Example 2: Aircraft Conflict (Temporal Overlap)")
    print("-" * 80)
    flight2 = {
        'flight_number': 'BA113',
        'airline': 'BA',
        'aircraft': 'B777',
        'source_airport': 'LHR',
        'destination_airport': 'JFK',
        'departure_time': datetime(2025, 10, 28, 15, 0),  # Before BA112 lands!
        'arrival_time': datetime(2025, 10, 28, 18, 0)
    }
    conflicts = detector.register_flight(flight2)
    if conflicts:
        print("❌ Conflicts detected:")
        for c in conflicts:
            print(f"   {c}")
    else:
        print(f"✅ {flight2['flight_number']} registered successfully!")
    print()
    
    # Example 3: Insufficient turnaround time
    print("📋 Example 3: Insufficient Turnaround Time")
    print("-" * 80)
    flight3 = {
        'flight_number': 'BA114',
        'airline': 'BA',
        'aircraft': 'B777',
        'source_airport': 'LHR',
        'destination_airport': 'CDG',
        'departure_time': datetime(2025, 10, 28, 23, 10),  # Only 10 min after landing!
        'arrival_time': datetime(2025, 10, 29, 1, 25)
    }
    conflicts = detector.register_flight(flight3)
    if conflicts:
        print("❌ Conflicts detected:")
        for c in conflicts:
            print(f"   {c}")
    else:
        print(f"✅ {flight3['flight_number']} registered successfully!")
    print()
    
    # Example 4: Valid with sufficient turnaround
    print("📋 Example 4: Valid Registration with Sufficient Turnaround")
    print("-" * 80)
    flight4 = {
        'flight_number': 'BA115',
        'airline': 'BA',
        'aircraft': 'B777',
        'source_airport': 'LHR',
        'destination_airport': 'CDG',
        'departure_time': datetime(2025, 10, 29, 0, 0),  # 1 hour after landing
        'arrival_time': datetime(2025, 10, 29, 2, 15)
    }
    conflicts = detector.register_flight(flight4)
    if conflicts:
        print("❌ Conflicts detected:")
        for c in conflicts:
            print(f"   {c}")
    else:
        print(f"✅ {flight4['flight_number']} registered successfully!")
        print(f"   Route: {flight4['source_airport']} → {flight4['destination_airport']}")
        print(f"   Turnaround time: 60 minutes (sufficient)")
    print()
    
    # Example 5: Runway conflict
    print("📋 Example 5: Runway Conflict (Too Close Departure Times)")
    print("-" * 80)
    flight5a = {
        'flight_number': 'AA100',
        'airline': 'AA',
        'aircraft': 'A321',
        'source_airport': 'JFK',
        'destination_airport': 'LAX',
        'departure_time': datetime(2025, 10, 28, 8, 0),
        'arrival_time': datetime(2025, 10, 28, 11, 30)
    }
    flight5b = {
        'flight_number': 'DL200',
        'airline': 'DL',
        'aircraft': 'B737',
        'source_airport': 'JFK',
        'destination_airport': 'ATL',
        'departure_time': datetime(2025, 10, 28, 8, 2),  # Only 2 min apart!
        'arrival_time': datetime(2025, 10, 28, 10, 30)
    }
    
    # Reset detector for this example
    detector2 = CollisionDetector()
    detector2.register_flight(flight5a)
    print(f"✅ {flight5a['flight_number']} registered (departs {flight5a['departure_time'].strftime('%H:%M')})")
    
    conflicts = detector2.register_flight(flight5b)
    if conflicts:
        print("❌ Conflicts detected:")
        for c in conflicts:
            print(f"   {c}")
    else:
        print(f"✅ {flight5b['flight_number']} registered successfully!")
    print()
    
    # Example 6: Valid runway spacing
    print("📋 Example 6: Valid Runway Spacing")
    print("-" * 80)
    flight6 = {
        'flight_number': 'UA300',
        'airline': 'UA',
        'aircraft': 'B757',
        'source_airport': 'JFK',
        'destination_airport': 'SFO',
        'departure_time': datetime(2025, 10, 28, 8, 10),  # 10 min after first flight
        'arrival_time': datetime(2025, 10, 28, 11, 0)
    }
    
    conflicts = detector2.register_flight(flight6)
    if conflicts:
        print("❌ Conflicts detected:")
        for c in conflicts:
            print(f"   {c}")
    else:
        print(f"✅ {flight6['flight_number']} registered successfully!")
        print(f"   Runway separation: 10 minutes (sufficient)")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Aircraft schedules tracked: {len(detector2.aircraft_schedules)} aircraft types")
    print(f"Active flights registered: {len(detector2.active_flights)} flights")
    print()
    
    # Airport statistics
    print("Airport Statistics:")
    for airport in ['JFK', 'LHR', 'CDG']:
        stats = detector2.get_airport_statistics(airport)
        if stats['runway_operations'] > 0:
            print(f"  {airport}: {stats['runway_operations']} runway ops, "
                  f"{stats['gate_reservations']} gate reservations, "
                  f"utilization: {stats['utilization']}")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    demo_collision_detection()
