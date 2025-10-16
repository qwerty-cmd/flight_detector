"""
Geographic filtering module for aircraft detection.
Determines if aircraft are overhead based on location and altitude.
"""
import math
from typing import List, Optional, Tuple
from src.utils import Aircraft


class GeoFilter:
    """Filter aircraft based on geographic location and altitude."""

    def __init__(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 3.0,
        min_altitude_m: float = 500,
        max_altitude_m: Optional[float] = 12000
    ):
        """
        Initialize geographic filter.

        Args:
            latitude: Base location latitude in degrees
            longitude: Base location longitude in degrees
            radius_km: Overhead radius in kilometers
            min_altitude_m: Minimum altitude in meters
            max_altitude_m: Maximum altitude in meters (None for no limit)
        """
        self.latitude = latitude
        self.longitude = longitude
        self.radius_km = radius_km
        self.min_altitude_m = min_altitude_m
        self.max_altitude_m = max_altitude_m

    def calculate_distance(self, lat: float, lon: float) -> float:
        """
        Calculate great circle distance between base location and given point.
        Uses Haversine formula.

        Args:
            lat: Target latitude in degrees
            lon: Target longitude in degrees

        Returns:
            Distance in kilometers
        """
        # Earth radius in kilometers
        R = 6371.0

        # Convert to radians
        lat1 = math.radians(self.latitude)
        lon1 = math.radians(self.longitude)
        lat2 = math.radians(lat)
        lon2 = math.radians(lon)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (math.sin(dlat / 2) ** 2 +
             math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))

        distance = R * c
        return distance

    def get_bearing(self, lat: float, lon: float) -> float:
        """
        Calculate bearing from base location to target point.

        Args:
            lat: Target latitude in degrees
            lon: Target longitude in degrees

        Returns:
            Bearing in degrees (0-360)
        """
        lat1 = math.radians(self.latitude)
        lon1 = math.radians(self.longitude)
        lat2 = math.radians(lat)
        lon2 = math.radians(lon)

        dlon = lon2 - lon1

        x = math.sin(dlon) * math.cos(lat2)
        y = (math.cos(lat1) * math.sin(lat2) -
             math.sin(lat1) * math.cos(lat2) * math.cos(dlon))

        bearing = math.atan2(x, y)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360

        return bearing

    @staticmethod
    def feet_to_meters(feet: float) -> float:
        """
        Convert feet to meters.

        Args:
            feet: Altitude in feet

        Returns:
            Altitude in meters
        """
        return feet * 0.3048

    def is_overhead(self, aircraft: Aircraft) -> bool:
        """
        Determine if aircraft is overhead based on position and altitude.

        Args:
            aircraft: Aircraft object with position data

        Returns:
            True if aircraft is overhead, False otherwise
        """
        # Check if aircraft has valid position
        if not aircraft.has_position():
            return False

        # Calculate distance
        distance = self.calculate_distance(aircraft.latitude, aircraft.longitude)

        # Check if within radius
        if distance > self.radius_km:
            return False

        # Convert altitude from feet to meters
        altitude_m = self.feet_to_meters(aircraft.altitude)

        # Check minimum altitude
        if altitude_m < self.min_altitude_m:
            return False

        # Check maximum altitude (if specified)
        if self.max_altitude_m is not None and altitude_m > self.max_altitude_m:
            return False

        return True

    def filter_overhead_aircraft(self, aircraft_list: List[Aircraft]) -> List[Aircraft]:
        """
        Filter aircraft list for overhead aircraft and sort by distance.

        Args:
            aircraft_list: List of Aircraft objects

        Returns:
            List of overhead aircraft sorted by distance (closest first)
        """
        overhead = []

        for aircraft in aircraft_list:
            if self.is_overhead(aircraft):
                distance = self.calculate_distance(aircraft.latitude, aircraft.longitude)
                overhead.append((distance, aircraft))

        # Sort by distance (closest first)
        overhead.sort(key=lambda x: x[0])

        # Return just the aircraft objects
        return [aircraft for _, aircraft in overhead]
