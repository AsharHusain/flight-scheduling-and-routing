import csv
import heapq
import itertools

def time_to_minutes(time_str):
    """Convert HH:MM string into total minutes"""
    hours, minutes = map(int, time_str.split(":"))
    return hours * 60 + minutes

def flight_duration(departure, arrival):
    """Calculate flight duration, including overnight flights"""
    dep_mins = time_to_minutes(departure)
    arr_mins = time_to_minutes(arrival)
    if arr_mins <= dep_mins:
        return (24 * 60 - dep_mins) + arr_mins
    else:
        return arr_mins - dep_mins

def build_flight_graph(csv_file):
    """Create graph from CSV file with airports as nodes"""
    graph = {}
    airports = set()
    try:
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                origin = row["SourceAirport"].strip().upper()
                destination = row["DestinationAirport"].strip().upper()
                cost = int(row["Cost"])
                flight_no = row["FlightNumber"]
                duration = flight_duration(row["DepartureTime"], row["ArrivalTime"])

                airports.add(origin)
                airports.add(destination)

                if origin not in graph:
                    graph[origin] = []
                graph[origin].append({
                    "destination": destination,
                    "cost": cost,
                    "duration": duration,
                    "flight_no": flight_no
                })
        return graph, airports
    except FileNotFoundError:
        print("Error: flights.csv not found!")
        exit(1)
    except KeyError as e:
        print(f"CSV missing expected column: {e}")
        exit(1)

def dijkstra(graph, start, end, weight_type="cost"):
    """Find shortest path using Dijkstra's algorithm"""
    counter = itertools.count()
    pq = [(0, next(counter), start, [], [])]  # total, tiebreaker, current, path, flights
    visited = set()

    while pq:
        total, _, current_airport, path, flights = heapq.heappop(pq)
        if current_airport in visited:
            continue
        visited.add(current_airport)
        path = path + [current_airport]

        if current_airport == end:
            return path, total, flights

        for flight in graph.get(current_airport, []):
            weight = flight[weight_type]
            heapq.heappush(pq, (total + weight, next(counter), flight["destination"], path, flights + [flight]))

    return None, float("inf"), []

def format_duration(minutes):
    """Format minutes into hours and minutes string"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"

if __name__ == "__main__":
    graph, airports = build_flight_graph("flights.csv")

    start_airport = input("Enter starting airport code: ").strip().upper()
    end_airport = input("Enter destination airport code: ").strip().upper()

    if start_airport not in airports:
        print(f"{start_airport} not found in airport list.")
    elif end_airport not in airports:
        print(f"{end_airport} not found in airport list.")
    else:
        # Cheapest path
        cheapest_path, total_cost, cheapest_flights = dijkstra(graph, start_airport, end_airport, "cost")
        print("\n=== Cheapest Route ===")
        if cheapest_path:
            for idx, flight in enumerate(cheapest_flights):
                print(f"{flight['flight_no']}: {cheapest_path[idx]} -> {flight['destination']}, Cost: ${flight['cost']}, Duration: {format_duration(flight['duration'])}")
            print(f"Total cost: ${total_cost}")
        else:
            print("No route found.")

        # Fastest path
        fastest_path, total_duration, fastest_flights = dijkstra(graph, start_airport, end_airport, "duration")
        print("\n=== Fastest Route ===")
        if fastest_path:
            for idx, flight in enumerate(fastest_flights):
                print(f"{flight['flight_no']}: {fastest_path[idx]} -> {flight['destination']}, Cost: ${flight['cost']}, Duration: {format_duration(flight['duration'])}")
            print(f"Total time: {format_duration(total_duration)}")
        else:
            print("No route found.")

        # Most efficient path (Cost per minute)
        print("\n=== Best Value Route (Cost/Time) ===")
        if not cheapest_path and not fastest_path:
            print("No routes available.")
        else:
            cheapest_duration = sum(f["duration"] for f in cheapest_flights) if cheapest_path else 0
            fastest_total_cost = sum(f["cost"] for f in fastest_flights) if fastest_path else float("inf")

            efficiency_cheapest = total_cost / cheapest_duration if cheapest_duration > 0 else float("inf")
            efficiency_fastest = fastest_total_cost / total_duration if total_duration > 0 else float("inf")

            if efficiency_cheapest <= efficiency_fastest and cheapest_path:
                print(f"Efficiency: ${efficiency_cheapest:.2f}/min")
                for idx, flight in enumerate(cheapest_flights):
                    print(f"{flight['flight_no']}: {cheapest_path[idx]} -> {flight['destination']}, Cost: ${flight['cost']}, Duration: {format_duration(flight['duration'])}")
                print(f"Total cost: ${total_cost}")
                print(f"Total time: {format_duration(cheapest_duration)}")
            elif fastest_path:
                print(f"Efficiency: ${efficiency_fastest:.2f}/min")
                for idx, flight in enumerate(fastest_flights):
                    print(f"{flight['flight_no']}: {fastest_path[idx]} -> {flight['destination']}, Cost: ${flight['cost']}, Duration: {format_duration(flight['duration'])}")
                print(f"Total cost: ${fastest_total_cost}")
                print(f"Total time: {format_duration(total_duration)}")
