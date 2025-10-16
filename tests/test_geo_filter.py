"""
Tests for geographic filtering module.
Following TDD: Write tests first, then implement.
"""
import pytest
from src.geo_filter import GeoFilter
from src.utils import Aircraft


class TestGeoFilter:
    """Test suite for GeoFilter class."""

    def test_calculate_distance_same_point(self):
        """Test distance calculation for same point returns 0."""
        geo_filter = GeoFilter(latitude=51.5074, longitude=-0.1278)
        distance = geo_filter.calculate_distance(51.5074, -0.1278)
        assert distance == 0.0

    def test_calculate_distance_known_points(self):
        """Test distance calculation between London and Paris (~344 km)."""
        geo_filter = GeoFilter(latitude=51.5074, longitude=-0.1278)  # London
        distance = geo_filter.calculate_distance(48.8566, 2.3522)  # Paris
        assert 340 < distance < 350  # Approximately 344 km

    def test_calculate_distance_across_prime_meridian(self):
        """Test distance calculation across the prime meridian."""
        geo_filter = GeoFilter(latitude=51.5074, longitude=-0.1278)  # London
        distance = geo_filter.calculate_distance(51.5074, 0.1278)  # Just east of London
        assert 15 < distance < 25  # Approximately 20 km

    def test_is_overhead_within_radius(self):
        """Test aircraft within radius is considered overhead."""
        geo_filter = GeoFilter(
            latitude=51.5074,
            longitude=-0.1278,
            radius_km=5.0,
            min_altitude_m=500,
            max_altitude_m=12000
        )

        aircraft_data = {
            'lat': 51.51,  # Very close to base location
            'lon': -0.13,
            'alt_baro': 3000  # 3000 feet (~914 meters)
        }
        aircraft = Aircraft(icao='ABC123', data=aircraft_data)

        assert geo_filter.is_overhead(aircraft) is True

    def test_is_overhead_outside_radius(self):
        """Test aircraft outside radius is not considered overhead."""
        geo_filter = GeoFilter(
            latitude=51.5074,
            longitude=-0.1278,
            radius_km=5.0,
            min_altitude_m=500,
            max_altitude_m=12000
        )

        aircraft_data = {
            'lat': 51.6,  # About 10km away
            'lon': -0.1,
            'alt_baro': 3000
        }
        aircraft = Aircraft(icao='ABC123', data=aircraft_data)

        assert geo_filter.is_overhead(aircraft) is False

    def test_is_overhead_below_min_altitude(self):
        """Test aircraft below minimum altitude is not considered overhead."""
        geo_filter = GeoFilter(
            latitude=51.5074,
            longitude=-0.1278,
            radius_km=5.0,
            min_altitude_m=500,
            max_altitude_m=12000
        )

        aircraft_data = {
            'lat': 51.51,
            'lon': -0.13,
            'alt_baro': 1000  # 1000 feet (~305 meters) - below min
        }
        aircraft = Aircraft(icao='ABC123', data=aircraft_data)

        assert geo_filter.is_overhead(aircraft) is False

    def test_is_overhead_above_max_altitude(self):
        """Test aircraft above maximum altitude is not considered overhead."""
        geo_filter = GeoFilter(
            latitude=51.5074,
            longitude=-0.1278,
            radius_km=5.0,
            min_altitude_m=500,
            max_altitude_m=12000
        )

        aircraft_data = {
            'lat': 51.51,
            'lon': -0.13,
            'alt_baro': 45000  # 45000 feet (~13716 meters) - above max
        }
        aircraft = Aircraft(icao='ABC123', data=aircraft_data)

        assert geo_filter.is_overhead(aircraft) is False

    def test_is_overhead_no_max_altitude(self):
        """Test overhead detection with no maximum altitude limit."""
        geo_filter = GeoFilter(
            latitude=51.5074,
            longitude=-0.1278,
            radius_km=5.0,
            min_altitude_m=500,
            max_altitude_m=None  # No max altitude
        )

        aircraft_data = {
            'lat': 51.51,
            'lon': -0.13,
            'alt_baro': 45000  # Very high altitude
        }
        aircraft = Aircraft(icao='ABC123', data=aircraft_data)

        assert geo_filter.is_overhead(aircraft) is True

    def test_is_overhead_missing_position(self):
        """Test aircraft with missing position data is not overhead."""
        geo_filter = GeoFilter(
            latitude=51.5074,
            longitude=-0.1278,
            radius_km=5.0,
            min_altitude_m=500,
            max_altitude_m=12000
        )

        aircraft_data = {
            'lat': None,
            'lon': None,
            'alt_baro': 3000
        }
        aircraft = Aircraft(icao='ABC123', data=aircraft_data)

        assert geo_filter.is_overhead(aircraft) is False

    def test_feet_to_meters_conversion(self):
        """Test conversion from feet to meters."""
        geo_filter = GeoFilter(latitude=0, longitude=0)

        assert geo_filter.feet_to_meters(0) == 0
        assert abs(geo_filter.feet_to_meters(1000) - 304.8) < 0.1
        assert abs(geo_filter.feet_to_meters(10000) - 3048.0) < 0.1

    def test_get_bearing(self):
        """Test bearing calculation between two points."""
        geo_filter = GeoFilter(latitude=51.5074, longitude=-0.1278)  # London

        # Bearing from London to Paris (roughly southeast, ~145 degrees)
        bearing = geo_filter.get_bearing(48.8566, 2.3522)
        assert 140 < bearing < 150

    def test_filter_overhead_aircraft_multiple(self):
        """Test filtering multiple aircraft for overhead status."""
        geo_filter = GeoFilter(
            latitude=51.5074,
            longitude=-0.1278,
            radius_km=5.0,
            min_altitude_m=500,
            max_altitude_m=12000
        )

        aircraft_list = [
            Aircraft(icao='A1', data={'lat': 51.51, 'lon': -0.13, 'alt_baro': 3000}),  # Overhead
            Aircraft(icao='A2', data={'lat': 51.6, 'lon': -0.1, 'alt_baro': 3000}),    # Too far
            Aircraft(icao='A3', data={'lat': 51.51, 'lon': -0.13, 'alt_baro': 500}),   # Too low
            Aircraft(icao='A4', data={'lat': 51.50, 'lon': -0.12, 'alt_baro': 5000}),  # Overhead
        ]

        overhead = geo_filter.filter_overhead_aircraft(aircraft_list)

        assert len(overhead) == 2
        assert overhead[0].icao == 'A1'
        assert overhead[1].icao == 'A4'

    def test_filter_overhead_aircraft_sorted_by_distance(self):
        """Test that overhead aircraft are sorted by distance (closest first)."""
        geo_filter = GeoFilter(
            latitude=51.5074,
            longitude=-0.1278,
            radius_km=10.0,
            min_altitude_m=500,
            max_altitude_m=12000
        )

        aircraft_list = [
            Aircraft(icao='FAR', data={'lat': 51.55, 'lon': -0.15, 'alt_baro': 3000}),    # ~5km
            Aircraft(icao='NEAR', data={'lat': 51.51, 'lon': -0.13, 'alt_baro': 3000}),   # ~0.5km
            Aircraft(icao='MID', data={'lat': 51.53, 'lon': -0.14, 'alt_baro': 3000}),    # ~2.5km
        ]

        overhead = geo_filter.filter_overhead_aircraft(aircraft_list)

        assert len(overhead) == 3
        assert overhead[0].icao == 'NEAR'  # Closest first
        assert overhead[1].icao == 'MID'
        assert overhead[2].icao == 'FAR'
