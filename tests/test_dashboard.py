"""
Tests for web dashboard module.
Following TDD: Write tests first, then implement.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from src.dashboard import FlightTrackerDashboard


class TestFlightTrackerDashboard:
    """Test suite for FlightTrackerDashboard class."""

    @patch('src.dashboard.Config')
    def test_dashboard_initialization(self, mock_config):
        """Test dashboard initialization."""
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.get_location.return_value = {
            'latitude': -37.7964,
            'longitude': 144.9008
        }
        mock_config_instance.get_overhead_zone.return_value = {
            'radius_km': 3.0,
            'min_altitude_m': 500,
            'max_altitude_m': 12000
        }
        mock_config_instance.get_adsb_config.return_value = {
            'data_source': 'http://localhost:8080/data/aircraft.json',
            'max_age': 30
        }
        mock_config_instance.get_api_config.return_value = {
            'provider': 'opensky',
            'api_key': '',
            'cache_duration': 300
        }
        mock_config_instance.get.return_value = 5

        dashboard = FlightTrackerDashboard('test_config.yaml')

        assert dashboard.app is not None
        assert dashboard.config is not None
        assert dashboard.stats['total_aircraft_seen'] == 0

    @patch('src.dashboard.Config')
    def test_status_endpoint(self, mock_config):
        """Test /api/status endpoint."""
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.get_location.return_value = {
            'latitude': -37.7964,
            'longitude': 144.9008
        }
        mock_config_instance.get_overhead_zone.return_value = {
            'radius_km': 3.0,
            'min_altitude_m': 500,
            'max_altitude_m': 12000
        }
        mock_config_instance.get_adsb_config.return_value = {
            'data_source': 'http://localhost:8080/data/aircraft.json',
            'max_age': 30
        }
        mock_config_instance.get_api_config.return_value = {
            'provider': 'opensky',
            'api_key': '',
            'cache_duration': 300
        }
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'location.latitude': -37.7964,
            'location.longitude': 144.9008,
            'overhead_zone.radius_km': 3.0,
            'overhead_zone.min_altitude_m': 500,
            'overhead_zone.max_altitude_m': 12000
        }.get(key, default)

        dashboard = FlightTrackerDashboard('test_config.yaml')

        with dashboard.app.test_client() as client:
            response = client.get('/api/status')
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data['status'] == 'running'
            assert 'uptime_seconds' in data
            assert data['location']['latitude'] == -37.7964

    @patch('src.dashboard.Config')
    def test_stats_endpoint(self, mock_config):
        """Test /api/stats endpoint."""
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.get_location.return_value = {
            'latitude': -37.7964,
            'longitude': 144.9008
        }
        mock_config_instance.get_overhead_zone.return_value = {
            'radius_km': 3.0
        }
        mock_config_instance.get_adsb_config.return_value = {
            'data_source': 'http://localhost:8080/data/aircraft.json'
        }
        mock_config_instance.get_api_config.return_value = {
            'provider': 'opensky'
        }
        mock_config_instance.get.return_value = 5

        dashboard = FlightTrackerDashboard('test_config.yaml')

        with dashboard.app.test_client() as client:
            response = client.get('/api/stats')
            assert response.status_code == 200

            data = json.loads(response.data)
            assert 'total_aircraft_seen' in data
            assert 'overhead_aircraft_count' in data

    @patch('src.dashboard.Config')
    def test_aircraft_endpoint(self, mock_config):
        """Test /api/aircraft endpoint."""
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.get_location.return_value = {
            'latitude': -37.7964,
            'longitude': 144.9008
        }
        mock_config_instance.get_overhead_zone.return_value = {
            'radius_km': 3.0
        }
        mock_config_instance.get_adsb_config.return_value = {
            'data_source': 'http://localhost:8080/data/aircraft.json'
        }
        mock_config_instance.get_api_config.return_value = {
            'provider': 'opensky'
        }
        mock_config_instance.get.return_value = 5

        dashboard = FlightTrackerDashboard('test_config.yaml')

        with dashboard.app.test_client() as client:
            response = client.get('/api/aircraft')
            assert response.status_code == 200

            data = json.loads(response.data)
            assert 'total' in data
            assert 'overhead' in data
            assert 'aircraft' in data

    @patch('src.dashboard.Config')
    def test_config_endpoint(self, mock_config):
        """Test /api/config endpoint."""
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.get_location.return_value = {
            'latitude': -37.7964,
            'longitude': 144.9008
        }
        mock_config_instance.get_overhead_zone.return_value = {
            'radius_km': 3.0
        }
        mock_config_instance.get_adsb_config.return_value = {
            'data_source': 'http://localhost:8080/data/aircraft.json'
        }
        mock_config_instance.get_api_config.return_value = {
            'provider': 'opensky'
        }
        mock_config_instance.get.side_effect = lambda key, default=None: {
            'api.provider': 'opensky',
            'api.cache_duration': 300,
            'adsb.data_source': 'http://localhost:8080/data/aircraft.json',
            'adsb.update_interval': 5
        }.get(key, default)

        dashboard = FlightTrackerDashboard('test_config.yaml')

        with dashboard.app.test_client() as client:
            response = client.get('/api/config')
            assert response.status_code == 200

            data = json.loads(response.data)
            assert 'location' in data
            assert 'overhead_zone' in data
            assert 'api' in data

    @patch('src.dashboard.Config')
    def test_aircraft_to_dict(self, mock_config):
        """Test aircraft conversion to dictionary."""
        from src.utils import Aircraft

        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.get_location.return_value = {
            'latitude': -37.7964,
            'longitude': 144.9008
        }
        mock_config_instance.get_overhead_zone.return_value = {
            'radius_km': 3.0
        }
        mock_config_instance.get_adsb_config.return_value = {
            'data_source': 'http://localhost:8080/data/aircraft.json'
        }
        mock_config_instance.get_api_config.return_value = {
            'provider': 'opensky'
        }
        mock_config_instance.get.return_value = 5

        dashboard = FlightTrackerDashboard('test_config.yaml')

        aircraft = Aircraft('abc123', {
            'flight': 'TEST123',
            'lat': -37.80,
            'lon': 144.90,
            'alt_baro': 5000,
            'gs': 250
        })

        aircraft_dict = dashboard._aircraft_to_dict(aircraft)

        assert aircraft_dict['icao'] == 'abc123'
        assert aircraft_dict['callsign'] == 'TEST123'
        assert aircraft_dict['latitude'] == -37.80
        assert 'distance_km' in aircraft_dict

    @patch('src.dashboard.Config')
    def test_format_uptime(self, mock_config):
        """Test uptime formatting."""
        mock_config_instance = MagicMock()
        mock_config.return_value = mock_config_instance
        mock_config_instance.get_location.return_value = {
            'latitude': -37.7964,
            'longitude': 144.9008
        }
        mock_config_instance.get_overhead_zone.return_value = {
            'radius_km': 3.0
        }
        mock_config_instance.get_adsb_config.return_value = {
            'data_source': 'http://localhost:8080/data/aircraft.json'
        }
        mock_config_instance.get_api_config.return_value = {
            'provider': 'opensky'
        }
        mock_config_instance.get.return_value = 5

        dashboard = FlightTrackerDashboard('test_config.yaml')

        formatted = dashboard._format_uptime(3665)  # 1h 1m 5s
        assert 'h' in formatted
        assert 'm' in formatted
        assert 's' in formatted
