"""
Test script to verify UI features work correctly
"""

from flight_engine import find_optimal_path, build_graph

# Build graph
print("Building graph...")
graph, airports = build_graph("data/advanced_flights.csv")
print(f"✅ Graph built: {len(airports)} airports")

# Test 1: Preferred airline
print("\n" + "="*80)
print("TEST 1: Preferred Airline (British Airways - BA)")
print("="*80)
prefs = {'preferred_airline': 'BA', 'avoid_airline': None}
path_ba, cost_ba = find_optimal_path(graph, 'JFK', 'LHR', 'cost', prefs)
if path_ba:
    airlines_used = [leg['airline'] for leg in path_ba]
    print(f"Route: {' -> '.join([leg['flight_number'] for leg in path_ba])}")
    print(f"Airlines: {airlines_used}")
    print(f"Cost: ${cost_ba:.2f}")
    ba_count = airlines_used.count('BA')
    print(f"✅ BA flights used: {ba_count}/{len(path_ba)}")
else:
    print("❌ No path found")

# Test 2: Avoid airline
print("\n" + "="*80)
print("TEST 2: Avoid Airline (Emirates - EK)")
print("="*80)
prefs = {'preferred_airline': None, 'avoid_airline': 'EK'}
path_no_ek, cost_no_ek = find_optimal_path(graph, 'JFK', 'DXB', 'cost', prefs)
if path_no_ek:
    airlines_used = [leg['airline'] for leg in path_no_ek]
    print(f"Route: {' -> '.join([leg['flight_number'] for leg in path_no_ek])}")
    print(f"Airlines: {airlines_used}")
    print(f"Cost: ${cost_no_ek:.2f}")
    if 'EK' in airlines_used:
        print("❌ ERROR: EK should be avoided but was used!")
    else:
        print("✅ EK successfully avoided")
else:
    print("❌ No path found")

# Test 3: Comparison without preferences
print("\n" + "="*80)
print("TEST 3: Same route WITHOUT avoiding EK")
print("="*80)
prefs = {'preferred_airline': None, 'avoid_airline': None}
path_normal, cost_normal = find_optimal_path(graph, 'JFK', 'DXB', 'cost', prefs)
if path_normal:
    airlines_used = [leg['airline'] for leg in path_normal]
    print(f"Route: {' -> '.join([leg['flight_number'] for leg in path_normal])}")
    print(f"Airlines: {airlines_used}")
    print(f"Cost: ${cost_normal:.2f}")
    if 'EK' in airlines_used:
        print("✅ EK available when not avoided")
else:
    print("❌ No path found")

# Test 4: Both preferences
print("\n" + "="*80)
print("TEST 4: Prefer BA and Avoid EK")
print("="*80)
prefs = {'preferred_airline': 'BA', 'avoid_airline': 'EK'}
path_both, cost_both = find_optimal_path(graph, 'JFK', 'BOM', 'best', prefs)
if path_both:
    airlines_used = [leg['airline'] for leg in path_both]
    print(f"Route: {' -> '.join([leg['flight_number'] for leg in path_both])}")
    print(f"Airlines: {airlines_used}")
    print(f"Score: {cost_both:.2f}")
    
    errors = []
    if 'EK' in airlines_used:
        errors.append("❌ EK should be avoided but was used!")
    else:
        print("✅ EK successfully avoided")
    
    ba_count = airlines_used.count('BA')
    if ba_count > 0:
        print(f"✅ BA preferred and used: {ba_count} times")
    else:
        print("⚠️ BA preferred but not used (may not be available on this route)")
    
    if not errors:
        print("✅ All preferences respected!")
else:
    print("❌ No path found")

print("\n" + "="*80)
print("ALL TESTS COMPLETED")
print("="*80)
