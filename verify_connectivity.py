"""
Script to verify that all airports have paths to all other airports.
This checks the connectivity of the flight network.
"""
from flight_engine import build_graph, find_optimal_path
from constants import AIRPORT_COORDINATES

def verify_network_connectivity(csv_file: str) -> dict:
    """Verifies that every airport can reach every other airport."""
    graph, airports = build_graph(csv_file)
    
    if not graph or not airports:
        print("Failed to build graph!")
        return {}
    
    airports_list = sorted(list(airports))
    print(f"\nFound {len(airports_list)} airports: {airports_list}\n")
    
    connectivity_matrix = {}
    missing_routes = []
    
    for start in airports_list:
        connectivity_matrix[start] = {}
        for end in airports_list:
            if start == end:
                connectivity_matrix[start][end] = "SAME"
                continue
            
            # Try to find a path
            path, value = find_optimal_path(graph, start, end, 'cost', {})
            
            if path:
                hops = len(path)
                connectivity_matrix[start][end] = f"✓ ({hops} hop{'s' if hops > 1 else ''})"
            else:
                connectivity_matrix[start][end] = "✗ NO PATH"
                missing_routes.append((start, end))
    
    # Print results
    print("=" * 80)
    print("CONNECTIVITY MATRIX")
    print("=" * 80)
    
    header = "FROM\\TO".ljust(8) + " ".join([a.ljust(12) for a in airports_list])
    print(header)
    print("-" * 80)
    
    for start in airports_list:
        row = start.ljust(8)
        for end in airports_list:
            row += connectivity_matrix[start][end].ljust(12)
        print(row)
    
    print("\n" + "=" * 80)
    if missing_routes:
        print(f"⚠️  MISSING ROUTES: {len(missing_routes)}")
        print("=" * 80)
        for start, end in missing_routes:
            print(f"  {start} → {end}")
    else:
        print("✓ ALL AIRPORTS CONNECTED!")
        print("=" * 80)
    
    return connectivity_matrix

if __name__ == "__main__":
    verify_network_connectivity("data/advanced_flights.csv")
