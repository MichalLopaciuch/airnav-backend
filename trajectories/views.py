"""API views for trajectory finding."""

from typing import Optional

from django.http import HttpRequest, JsonResponse

from .models import Airline
from .services import TrajectoryFinder


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


def find_trajectory(request: HttpRequest) -> JsonResponse:
    return TrajectoryAPI.find_trajectory(request)
