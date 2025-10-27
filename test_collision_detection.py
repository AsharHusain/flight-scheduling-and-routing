"""
Test script for collision detection system.
Validates the flight schedule from CSV for various conflicts.
"""

from collision_handler import validate_csv_schedule, CollisionDetector

def main():
    print("=" * 80)
    print("FLIGHT SCHEDULE COLLISION DETECTION")
    print("=" * 80)
    print()
    
    # Validate the schedule
    results = validate_csv_schedule("data/advanced_flights.csv")
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Print summary
    print(f"📊 VALIDATION SUMMARY")
    print(f"{'─' * 80}")
    print(f"Total Flights Analyzed:     {results['total_flights']}")
    print(f"✅ Successfully Scheduled:   {results['successful']}")
    print(f"❌ Conflicts Detected:       {results['failed']}")
    print()
    
    # Print conflict breakdown
    if results.get('conflict_summary'):
        print(f"🔍 CONFLICT BREAKDOWN")
        print(f"{'─' * 80}")
        summary = results['conflict_summary']
        print(f"Aircraft/Turnaround Conflicts:  {summary['aircraft_conflicts']}")
        print(f"Runway Time Conflicts:          {summary['runway_conflicts']}")
        print(f"Gate Capacity Conflicts:        {summary['gate_conflicts']}")
        print(f"Aircraft Positioning Conflicts: {summary['positioning_conflicts']}")
        print()
    
    # Print detailed conflicts if any
    if results['failed'] > 0:
        print(f"⚠️  DETAILED CONFLICTS (showing first 10)")
        print(f"{'─' * 80}")
        
        for i, failed in enumerate(results['failed_flights'][:10], 1):
            print(f"\n{i}. Flight: {failed['flight']}")
            for conflict in failed['conflicts']:
                print(f"   {conflict}")
        
        if results['failed'] > 10:
            print(f"\n... and {results['failed'] - 10} more flights with conflicts")
    else:
        print("✅ No conflicts detected! Schedule is valid.")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
