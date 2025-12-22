"""Graph traversal and trajectory finding services."""

import random
from collections import deque, defaultdict
from math import radians, sin, cos, sqrt, atan2
from typing import Dict, List, Optional, Set, Tuple

from django.http import HttpRequest, JsonResponse

from .models import Airline, Airport


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers using Haversine formula.

    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate

    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in km

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c


def calculate_route_distance(airports: List[Airport], route: List[int]) -> float:
    """Calculate total distance for a route visiting airports in given order.

    Args:
        airports: List of Airport objects
        route: List of indices representing order to visit airports

    Returns:
        Total distance in kilometers
    """
    total_distance = 0
    for i in range(len(route)):
        current_idx = route[i]
        next_idx = route[(i + 1) % len(route)]  # Loop back to start

        current = airports[current_idx]
        next_airport = airports[next_idx]

        distance = haversine_distance(
            current.lat, current.lon, next_airport.lat, next_airport.lon
        )
        total_distance += distance

    return total_distance


def genetic_algorithm_tsp(
    airports: List[Airport],
    population_size: int = 100,
    generations: int = 500,
    mutation_rate: float = 0.02,
) -> Tuple[List[str], float]:
    """Solve TSP using genetic algorithm.

    Args:
        airports: List of Airport objects to visit
        population_size: Number of routes in each generation
        generations: Number of generations to evolve
        mutation_rate: Probability of mutation per individual

    Returns:
        Tuple of (best route as airport codes, total distance)
    """
    n = len(airports)

    # Initialize population with random routes
    population = [list(range(n)) for _ in range(population_size)]
    random.shuffle(population[0])

    best_route = None
    best_distance = float("inf")

    for _ in range(generations):
        # Calculate fitness (distance) for each route
        distances = [calculate_route_distance(airports, route) for route in population]

        # Track best route
        min_distance = min(distances)
        min_idx = distances.index(min_distance)

        if min_distance < best_distance:
            best_distance = min_distance
            best_route = population[min_idx]

        # Selection: keep best routes (elitism)
        sorted_indices = sorted(range(len(distances)), key=lambda i: distances[i])
        elite_size = max(2, population_size // 10)
        elite = [population[i] for i in sorted_indices[:elite_size]]

        # Create new population through crossover and mutation
        new_population = elite.copy()

        while len(new_population) < population_size:
            # Select two parents
            parent1 = random.choice(elite)
            parent2 = random.choice(elite)

            # Crossover (Order Crossover)
            if len(parent1) > 1:
                point1, point2 = sorted(random.sample(range(n), 2))
                child = [-1] * n
                child[point1:point2] = parent1[point1:point2]

                pointer = point2
                for city in parent2:
                    if city not in child:
                        if pointer >= n:
                            pointer = 0
                        if child[pointer] == -1:
                            child[pointer] = city
                        pointer += 1
            else:
                child = parent1.copy()

            # Mutation (swap random cities)
            if random.random() < mutation_rate:
                idx1, idx2 = random.sample(range(n), 2)
                child[idx1], child[idx2] = child[idx2], child[idx1]

            new_population.append(child)

        population = new_population[:population_size]

    # Convert indices to airport codes
    best_route_codes = [airports[i].iata_code for i in best_route]

    return best_route_codes, best_distance


class AirlineGraph:
    """Represents an airline's route network as a graph."""

    def __init__(self, airline: Airline):
        self.airline = airline
        self.adjacency_list: Dict[str, List[str]] = defaultdict(list)
        self.all_airports: Set[str] = set()
        self._build_graph()

    def _build_graph(self) -> None:
        routes = self.airline.route_set.all()
        for route in routes:
            origin_code = route.origin.iata_code
            destination_code = route.destination.iata_code

            self.adjacency_list[origin_code].append(destination_code)
            self.all_airports.add(origin_code)
            self.all_airports.add(destination_code)

    def has_airport(self, airport_code: str) -> bool:
        return airport_code in self.all_airports

    def get_adjacency_list(self) -> Dict[str, List[str]]:
        return dict(self.adjacency_list)


class TrajectoryFinder:
    @staticmethod
    def find_shortest_path(
        graph: Dict[str, List[str]], start: str, end: str
    ) -> Optional[List[str]]:
        """Find shortest path with BFS"""
        if start == end:
            return [start]

        visited: Set[str] = set()
        queue: deque = deque([(start, [start])])
        visited.add(start)

        while queue:
            current, path = queue.popleft()

            for neighbor in graph.get(current, []):
                if neighbor == end:
                    return path + [neighbor]

                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))

        return None

    @staticmethod
    def find_trajectory(
        airline: Airline, origin: str, destination: str
    ) -> Tuple[Optional[List[str]], Optional[str]]:
        graph = AirlineGraph(airline)

        if not graph.has_airport(origin):
            return None, f"Origin airport {origin} not in {airline.iata_code} network"

        if not graph.has_airport(destination):
            return (
                None,
                f"Destination airport {destination} not in {airline.iata_code} network",
            )

        path = TrajectoryFinder.find_shortest_path(
            graph.get_adjacency_list(), origin, destination
        )

        if path is None:
            return (
                None,
                f"No route found from {origin} to {destination} on {airline.iata_code}",
            )

        return path, None


class TrajectoryAPI:
    """API endpoints for trajectory finding."""

    @staticmethod
    def _get_query_param(request: HttpRequest, param: str) -> Optional[str]:
        value = request.GET.get(param, "").strip()
        return value if value else None

    @staticmethod
    def find_trajectory(request: HttpRequest) -> JsonResponse:
        """Find shortest trajectory between two airports for given airline.

        Query Parameters:
            - airline_iata: (e.g. "UA")
            - origin: (e.g. "JFK")
            - destination: (e.g. "LAX")

        Returns:
            JSON response with trajectory

        Example:
            GET trajectories/find?airline_iata=UA&origin=JFK&destination=LAX
        """

        airline_iata = TrajectoryAPI._get_query_param(request, "airline_iata")
        origin = TrajectoryAPI._get_query_param(request, "origin")
        destination = TrajectoryAPI._get_query_param(request, "destination")

        if not all([airline_iata, origin, destination]):
            return JsonResponse(
                {
                    "error": "Missing required parameters",
                    "required": ["airline_iata", "origin", "destination"],
                },
                status=400,
            )

        try:
            airline = Airline.objects.get(iata_code=airline_iata)
        except Airline.DoesNotExist:
            return JsonResponse(
                {"error": f"Airline '{airline_iata}' not found"},
                status=404,
            )

        trajectory, error = TrajectoryFinder.find_trajectory(
            airline, origin, destination
        )

        if error:
            return JsonResponse({"error": error}, status=400)

        return JsonResponse(
            {
                "airline": {
                    "iata_code": airline.iata_code,
                    "name": airline.name,
                },
                "route": {
                    "origin": origin,
                    "destination": destination,
                    "stops": len(trajectory) - 2,  # Minus dep+dest
                },
                "trajectory": trajectory,
            },
            status=200,
        )

    @staticmethod
    def solve_tsp(request: HttpRequest) -> JsonResponse:
        """Solve TSP to find optimal route visiting airports.

        Must provide either airline_iata or iso_country parameter.

        Query Parameters:
            - airline_iata: (optional) IATA code of airline (e.g., "UA", "LH")
            - iso_country: (optional) 2-letter ISO country code (e.g., "US", "GB")

        Returns:
            JSON with optimal route and total distance

        Examples:
            GET trajectories/visit/?airline_iata=UA
            GET trajectories/visit/?iso_country=US
        """
        airline_iata = TrajectoryAPI._get_query_param(request, "airline_iata")
        iso_country = TrajectoryAPI._get_query_param(request, "iso_country")
        airline = None

        if not airline_iata and not iso_country:
            return JsonResponse(
                {
                    "error": "Must provide either airline_iata or iso_country",
                    "parameters": ["airline_iata", "iso_country"],
                },
                status=400,
            )

        if airline_iata:
            try:
                airline = Airline.objects.get(iata_code=airline_iata)
            except Airline.DoesNotExist:
                return JsonResponse(
                    {"error": f"Airline '{airline_iata}' not found"},
                    status=404,
                )

            routes = airline.route_set.all()
            airport_ids = set()

            for route in routes:
                airport_ids.add(route.origin_id)
                airport_ids.add(route.destination_id)

            if not airport_ids:
                return JsonResponse(
                    {"error": f"No airports found for airline '{airline_iata}'"},
                    status=400,
                )

            airports = list(Airport.objects.filter(id__in=airport_ids))
        else:
            airports = list(Airport.objects.filter(iso_country=iso_country))

            if not airports:
                return JsonResponse(
                    {"error": f"No airports found for country '{iso_country}'"},
                    status=404,
                )

        if len(airports) < 2:
            return JsonResponse(
                {"error": "Need at least 2 airports to solve TSP"},
                status=400,
            )

        best_route, total_distance = genetic_algorithm_tsp(airports)

        response_data = {
            "route": best_route,
            "total_distance_km": round(total_distance, 2),
            "airports_count": len(airports),
        }

        if airline:
            response_data["airline"] = {
                "iata_code": airline.iata_code,
                "name": airline.name,
            }
        elif iso_country:
            response_data["country"] = iso_country

        return JsonResponse(response_data, status=200)
