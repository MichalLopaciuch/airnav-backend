"""Graph traversal and trajectory finding services."""

from collections import deque, defaultdict
from typing import Dict, List, Optional, Set, Tuple

from .models import Airline


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
