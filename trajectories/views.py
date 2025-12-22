"""API views for trajectory finding."""

from django.http import HttpRequest, JsonResponse

from .services import TrajectoryAPI


def find_trajectory(request: HttpRequest) -> JsonResponse:
    return TrajectoryAPI.find_trajectory(request)


def visit_trajectories(request: HttpRequest) -> JsonResponse:
    return TrajectoryAPI.solve_tsp(request)
