from django.urls import path
from .views import find_trajectory, visit_trajectories


urlpatterns = [
    path("find", find_trajectory),
    path("visit", visit_trajectories),
]
