from django.db import models
from collections import defaultdict


class Airport(models.Model):
    iata_code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=200)
    lat = models.FloatField()
    lon = models.FloatField()

    class Meta:
        verbose_name_plural = "Airports"
        ordering = ["iata_code"]
        indexes = [
            models.Index(fields=["iata_code"]),
        ]

    def __str__(self):
        return f"{self.iata_code} - {self.name}"


class Airline(models.Model):
    name = models.CharField(max_length=200)
    iata_code = models.CharField(max_length=2, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["iata_code"]

    def __str__(self):
        return f"{self.iata_code} - {self.name}"


class Route(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    origin = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="departure_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="arrival_routes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("airline", "origin", "destination")
        ordering = ["airline", "origin", "destination"]
        indexes = [
            models.Index(fields=["airline", "origin"]),
            models.Index(fields=["airline", "destination"]),
        ]

    def __str__(self):
        return f"{self.airline.iata_code}: {self.origin.iata_code} -> {self.destination.iata_code}"
