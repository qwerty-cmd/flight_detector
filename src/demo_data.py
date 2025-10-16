"""
Demo data generator for dashboard deployment.
Simulates aircraft data for demonstration purposes.
"""
import random
import time
from typing import List
from src.utils import Aircraft


class DemoDataGenerator:
    """Generate demo aircraft data for display."""

    DEMO_FLIGHTS = [
        {'icao': 'C39B82', 'callsign': 'QFA94', 'origin': 'United States', 'dest': 'Australia'},
        {'icao': 'C40A3D', 'callsign': 'VOZ863', 'origin': 'Australia', 'dest': 'New Zealand'},
        {'icao': 'C3BA12', 'callsign': 'QFA432', 'origin': 'Australia', 'dest': 'Australia'},
        {'icao': 'C3D5F8', 'callsign': 'JST724', 'origin': 'Australia', 'dest': 'Australia'},
        {'icao': 'C45821', 'callsign': 'QFA7', 'origin': 'United Kingdom', 'dest': 'Australia'},
        {'icao': 'C51A22', 'callsign': 'SIA231', 'origin': 'Singapore', 'dest': 'Australia'},
    ]

    def __init__(self, center_lat: float = -37.7964, center_lon: float = 144.9008):
        """
        Initialize demo data generator.

        Args:
            center_lat: Center latitude (Footscray, Melbourne)
            center_lon: Center longitude
        """
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.aircraft_pool = []
        self._initialize_aircraft()

    def _initialize_aircraft(self):
        """Initialize pool of demo aircraft."""
        for flight in self.DEMO_FLIGHTS:
            # Random position within 50km
            lat_offset = random.uniform(-0.5, 0.5)
            lon_offset = random.uniform(-0.5, 0.5)

            aircraft_data = {
                'flight': flight['callsign'],
                'lat': self.center_lat + lat_offset,
                'lon': self.center_lon + lon_offset,
                'alt_baro': random.randint(5000, 35000),
                'gs': random.randint(200, 500),
                'track': random.randint(0, 359),
                'baro_rate': random.randint(-1000, 1000),
                'seen': random.randint(0, 5)
            }

            aircraft = Aircraft(flight['icao'], aircraft_data)
            aircraft.origin_country = flight['origin']
            aircraft.destination_country = flight['dest']
            aircraft.flight_number = flight['callsign']

            self.aircraft_pool.append(aircraft)

    def get_aircraft(self) -> List[Aircraft]:
        """
        Get current demo aircraft list.

        Returns:
            List of Aircraft objects
        """
        # Update positions slightly
        for aircraft in self.aircraft_pool:
            if aircraft.latitude and aircraft.longitude:
                # Simulate movement
                aircraft.latitude += random.uniform(-0.01, 0.01)
                aircraft.longitude += random.uniform(-0.01, 0.01)
                aircraft.altitude += random.randint(-100, 100)
                aircraft.last_seen = random.randint(0, 5)

        # Randomly return 3-5 aircraft
        count = random.randint(3, len(self.aircraft_pool))
        return random.sample(self.aircraft_pool, count)

    def get_overhead_aircraft(self) -> List[Aircraft]:
        """
        Get demo overhead aircraft.

        Returns:
            List of Aircraft objects that appear overhead
        """
        # Return 1-2 aircraft as "overhead"
        overhead_count = random.randint(0, 2)
        if overhead_count == 0:
            return []

        candidates = []
        for aircraft in self.aircraft_pool[:overhead_count]:
            # Position close to center
            aircraft_data = {
                'flight': aircraft.callsign,
                'lat': self.center_lat + random.uniform(-0.02, 0.02),
                'lon': self.center_lon + random.uniform(-0.02, 0.02),
                'alt_baro': random.randint(3000, 10000),
                'gs': random.randint(250, 450),
                'track': random.randint(0, 359),
                'baro_rate': random.randint(-500, 500),
                'seen': random.randint(0, 2)
            }

            overhead = Aircraft(aircraft.icao, aircraft_data)
            overhead.origin_country = aircraft.origin_country
            overhead.destination_country = aircraft.destination_country
            overhead.flight_number = aircraft.flight_number

            candidates.append(overhead)

        return candidates
