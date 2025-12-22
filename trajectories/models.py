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
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("airline", "airport")
        ordering = ["airline", "airport"]
        indexes = [
            models.Index(fields=["airline", "airport"]),
        ]

    def __str__(self):
        return f"{self.airline.iata_code} -> {self.airport.iata_code}"
