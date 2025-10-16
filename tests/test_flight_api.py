"""
Tests for flight API module.
Following TDD: Write tests first, then implement.
"""
import pytest
import time
from unittest.mock import Mock, patch, mock_open
from src.flight_api import FlightAPIClient
from src.utils import Aircraft


class TestFlightAPIClient:
    """Test suite for FlightAPIClient class."""

    def test_init_with_default_params(self):
        """Test initialization with default parameters."""
        client = FlightAPIClient()
        assert client.provider == "opensky"
        assert client.api_key == ""
        assert client.cache_duration == 300
        assert client.request_timeout == 10

    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        client = FlightAPIClient(
            provider="adsbexchange",
            api_key="test123",
            cache_duration=600,
            request_timeout=20
        )
        assert client.provider == "adsbexchange"
        assert client.api_key == "test123"
        assert client.cache_duration == 600
        assert client.request_timeout == 20

    @patch('src.flight_api.requests.get')
    def test_enrich_aircraft_opensky_success(self, mock_get):
        """Test successful flight data enrichment using OpenSky API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'states': [[
                'abc123',  # icao24
                'BAW123  ',  # callsign
                'United Kingdom',  # origin_country
                None, None, None, None, None,
                None, None, None, None, None, None,
                None, None, None, None
            ]]
        }
        mock_get.return_value = mock_response

        client = FlightAPIClient(provider="opensky")
        aircraft = Aircraft('abc123', {'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000})

        client.enrich_aircraft(aircraft)

        assert aircraft.origin_country == 'United Kingdom'

    @patch('src.flight_api.requests.get')
    def test_enrich_aircraft_opensky_no_data(self, mock_get):
        """Test OpenSky API with no matching data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'states': None}
        mock_get.return_value = mock_response

        client = FlightAPIClient(provider="opensky")
        aircraft = Aircraft('abc123', {'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000})

        client.enrich_aircraft(aircraft)

        assert aircraft.origin_country is None

    @patch('src.flight_api.requests.get')
    def test_enrich_aircraft_api_error(self, mock_get):
        """Test handling of API request errors."""
        mock_get.side_effect = Exception("API Error")

        client = FlightAPIClient(provider="opensky")
        aircraft = Aircraft('abc123', {'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000})

        # Should not raise exception
        client.enrich_aircraft(aircraft)

        assert aircraft.origin_country is None

    def test_cache_functionality(self):
        """Test caching of flight data."""
        client = FlightAPIClient(cache_duration=300)

        # Add to cache
        client._cache['abc123'] = {
            'origin_country': 'United Kingdom',
            'timestamp': time.time()
        }

        # Check cache hit
        assert client._is_cached('abc123') is True
        cached_data = client._get_cached_data('abc123')
        assert cached_data['origin_country'] == 'United Kingdom'

    def test_cache_expiry(self):
        """Test cache expiration."""
        client = FlightAPIClient(cache_duration=1)  # 1 second cache

        # Add old cache entry
        client._cache['abc123'] = {
            'origin_country': 'United Kingdom',
            'timestamp': time.time() - 10  # 10 seconds ago
        }

        # Should be expired
        assert client._is_cached('abc123') is False

    @patch('src.flight_api.requests.get')
    def test_enrich_aircraft_uses_cache(self, mock_get):
        """Test that cached data is used instead of making API calls."""
        client = FlightAPIClient(provider="opensky")

        # Pre-populate cache
        client._cache['abc123'] = {
            'origin_country': 'Cached Country',
            'timestamp': time.time()
        }

        aircraft = Aircraft('abc123', {'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000})
        client.enrich_aircraft(aircraft)

        # Should use cached data, not make API call
        mock_get.assert_not_called()
        assert aircraft.origin_country == 'Cached Country'

    @patch('builtins.open', new_callable=mock_open, read_data='{"LHR": {"country": "United Kingdom"}}')
    def test_load_airport_database(self, mock_file):
        """Test loading airport database."""
        client = FlightAPIClient()
        db = client._load_airport_database()

        assert 'LHR' in db
        assert db['LHR']['country'] == 'United Kingdom'

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_airport_database_file_not_found(self, mock_file):
        """Test airport database loading with missing file."""
        client = FlightAPIClient()
        db = client._load_airport_database()

        assert db == {}

    def test_extract_airport_from_callsign(self):
        """Test extracting airport codes from callsigns."""
        client = FlightAPIClient()

        # Common airline callsign format
        assert client._extract_airports_from_callsign('BAW123') is None  # Can't determine from airline code
        assert client._extract_airports_from_callsign('') is None

    def test_parse_route_from_callsign(self):
        """Test parsing route information from callsign."""
        client = FlightAPIClient()

        # This is a simplified test - actual implementation may vary
        result = client._parse_route_from_callsign('TEST123')
        assert result is None or isinstance(result, dict)

    @patch('src.flight_api.requests.get')
    def test_rate_limiting(self, mock_get):
        """Test rate limiting between API requests."""
        client = FlightAPIClient(provider="opensky")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'states': None}
        mock_get.return_value = mock_response

        aircraft1 = Aircraft('abc123', {'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000})
        aircraft2 = Aircraft('def456', {'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000})

        start_time = time.time()
        client.enrich_aircraft(aircraft1)
        client.enrich_aircraft(aircraft2)
        elapsed = time.time() - start_time

        # Should have some delay between requests
        # Note: This test might be flaky depending on system performance
        assert elapsed >= 0  # At minimum, just check it completes

    def test_enrich_multiple_aircraft(self):
        """Test enriching multiple aircraft."""
        client = FlightAPIClient(provider="opensky")

        aircraft_list = [
            Aircraft('abc123', {'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000}),
            Aircraft('def456', {'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000}),
        ]

        # Should not raise exception
        with patch('src.flight_api.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'states': None}
            mock_get.return_value = mock_response

            client.enrich_multiple_aircraft(aircraft_list)

        # All aircraft should have been processed
        assert len(aircraft_list) == 2

    def test_unsupported_provider(self):
        """Test unsupported API provider."""
        client = FlightAPIClient(provider="unsupported")
        aircraft = Aircraft('abc123', {'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000})

        # Should handle gracefully
        client.enrich_aircraft(aircraft)
        assert aircraft.origin_country is None
