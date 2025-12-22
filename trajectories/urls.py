from django.urls import path
from .views import find_trajectory

urlpatterns = [path("find", find_trajectory)]
