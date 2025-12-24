# Airnav | Airline Trajectory Finder

A Django-based API for finding optimal airline routes and solving the Traveling Salesman Problem (TSP) across airport networks.

## Overview

This project provides two main services for airline route optimization:

1. **Route Finding** - Find the shortest path between two airports within an airline's network
2. **TSP Solver** - Optimize a route visiting all airports in an airline's network or a specific country using metaheuristic

## API Endpoints

### `GET /trajectories/find`

Find the shortest route between two airports on a specific airline.

**Parameters:**

- `airline_iata` - Airline IATA code (e.g., "UA", "LH")
- `origin` - Departure airport IATA code (e.g., "JFK")
- `destination` - Arrival airport IATA code (e.g., "LAX")

**Example:**

```
GET /trajectories/find?airline_iata=UA&origin=JFK&destination=LAX
```

**Response:**

```json
{
  "airline": {
    "iata_code": "UA",
    "name": "United Airlines"
  },
  "route": {
    "origin": "JFK",
    "destination": "LAX",
    "stops": 2
  },
  "trajectory": ["JFK", "ORD", "LAX"]
}
```

Uses BFS (Breadth-First Search) algorithm for finding the shortest path through the airline's route network.

---

### `GET /trajectories/visit`

Solve the TSP to find an optimal route visiting all airports in an airline's network or a country.

**Parameters:**

- `airline_iata` - (Optional) Airline IATA code to visit its airports
- `iso_country` - (Optional) ISO country code to visit its airports (e.g., "US", "GB")

At least one parameter must be provided.

**Examples:**

```
GET /trajectories/visit?airline_iata=UA
GET /trajectories/visit?iso_country=US
```

**Response:**

```json
{
  "airline": {
    "iata_code": "UA",
    "name": "United Airlines"
  },
  "route": ["JFK", "ORD", "LAX", "SFO", "DEN"],
  "total_distance_km": 8432.45,
  "airports_count": 5,
  "computation_time_seconds": 1.234
}
```

Uses a **Genetic Algorithm** with:

- Population-based evolution
- Elitism (preserving best routes)
- Order Crossover for breeding
- Random mutations for exploration
- Default: 500 generations, 100 population size

## Key Features

- **BFS Shortest Path** - Efficient route finding through airline networks
- **Genetic Algorithm TSP** - Evolutionary optimization for visiting multiple airports
- **Distance Calculation** - Haversine formula for real-world airport distances
- **Multiple Filters** - Search by airline or country
- **Performance Metrics** - Returns computation time for TSP solutions

## Installation & Setup

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Load airport data
python manage.py loaddata trajectories/fixtures/airports.json

# Load test airlines
python manage.py loaddata trajectories/fixtures/airlines.json

# Run server
python manage.py runserver
```

## Project Stack

- **Django** - Web framework and ORM
- **Python** - Algorithms and business logic
- **SQLite** - Database (default Django setup)
