import json
from collections import deque, defaultdict
from django.http import HttpRequest, JsonResponse
from .models import Airport, Airline


def find_trajectory(request: HttpRequest):
    """
    Find a trajectory between two airports for a given airline using BFS.

    Query parameters:
    - airline_iata: IATA code of the airline
    - origin: IATA code of origin airport
    - destination: IATA code of destination airport
    """
    airline_iata = request.GET.get("airline_iata")
    origin_code = request.GET.get("origin")
    destination_code = request.GET.get("destination")

    # Validate parameters
    if not all([airline_iata, origin_code, destination_code]):
        return JsonResponse(
            {"error": "Missing required parameters: airline_iata, origin, destination"},
            status=400,
        )

    try:
        airline = Airline.objects.get(iata_code=airline_iata)
    except Airline.DoesNotExist:
        return JsonResponse({"error": f"Airline {airline_iata} not found"}, status=404)

    # Get all airports for this airline through Route model
    routes = airline.route_set.all()
    airports = [route.airport for route in routes]
    airport_dict = {airport.iata_code: airport for airport in airports}

    # Check if both origin and destination exist in airline's network
    if origin_code not in airport_dict:
        return JsonResponse(
            {"error": f"Origin airport {origin_code} not in {airline_iata} network"},
            status=400,
        )
    if destination_code not in airport_dict:
        return JsonResponse(
            {
                "error": f"Destination airport {destination_code} not in {airline_iata} network"
            },
            status=400,
        )

    # Build adjacency list (all airports connected to each other)
    adjacency_list = defaultdict(list)
    airport_codes = list(airport_dict.keys())

    for code in airport_codes:
        for other_code in airport_codes:
            if code != other_code:
                adjacency_list[code].append(other_code)

    # BFS to find trajectory
    def bfs_trajectory(start, end, graph):
        if start == end:
            return [start]

        visited = set()
        queue = deque([(start, [start])])
        visited.add(start)

        while queue:
            current, path = queue.popleft()

            for neighbor in graph[current]:
                if neighbor == end:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    trajectory = bfs_trajectory(origin_code, destination_code, adjacency_list)

    return JsonResponse(
        {
            "airline": {
                "iata_code": airline.iata_code,
                "name": airline.name,
            },
            "origin": origin_code,
            "destination": destination_code,
            "adjacency_list": dict(adjacency_list),
            "trajectory": trajectory,
            "trajectory_length": len(trajectory) if trajectory else 0,
            "airports_count": len(airports),
        }
    )
