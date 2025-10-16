"""
Tests for ADS-B data processor module.
Following TDD: Write tests first, then implement.
"""
import pytest
import json
from unittest.mock import Mock, patch, mock_open
from src.adsb_processor import ADSBProcessor
from src.utils import Aircraft


class TestADSBProcessor:
    """Test suite for ADSBProcessor class."""

    def test_init_with_default_params(self):
        """Test initialization with default parameters."""
        processor = ADSBProcessor()
        assert processor.data_source == "http://localhost:8080/data/aircraft.json"
        assert processor.max_age == 30

    def test_init_with_custom_params(self):
        """Test initialization with custom parameters."""
        processor = ADSBProcessor(
            data_source="http://custom:9090/data.json",
            max_age=60
        )
        assert processor.data_source == "http://custom:9090/data.json"
        assert processor.max_age == 60

    @patch('requests.get')
    def test_fetch_aircraft_data_http_success(self, mock_get):
        """Test successful HTTP fetch of aircraft data."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'aircraft': [
                {
                    'hex': 'abc123',
                    'flight': 'BA142   ',
                    'lat': 51.5,
                    'lon': -0.1,
                    'alt_baro': 5000,
                    'gs': 250,
                    'track': 180,
                    'seen': 2
                }
            ]
        }
        mock_get.return_value = mock_response

        processor = ADSBProcessor(data_source="http://localhost:8080/data/aircraft.json")
        aircraft_list = processor.fetch_aircraft_data()

        assert len(aircraft_list) == 1
        assert aircraft_list[0].icao == 'abc123'
        assert aircraft_list[0].callsign == 'BA142'
        assert aircraft_list[0].latitude == 51.5

    @patch('requests.get')
    def test_fetch_aircraft_data_http_error(self, mock_get):
        """Test HTTP fetch with connection error."""
        mock_get.side_effect = Exception("Connection error")

        processor = ADSBProcessor(data_source="http://localhost:8080/data/aircraft.json")
        aircraft_list = processor.fetch_aircraft_data()

        assert aircraft_list == []

    def test_fetch_aircraft_data_file_source(self):
        """Test fetching aircraft data from local file."""
        json_data = json.dumps({
            'aircraft': [
                {
                    'hex': 'def456',
                    'flight': 'LH789',
                    'lat': 52.0,
                    'lon': 1.0,
                    'alt_baro': 10000,
                    'seen': 1
                }
            ]
        })

        with patch('builtins.open', mock_open(read_data=json_data)):
            processor = ADSBProcessor(data_source="/path/to/aircraft.json")
            aircraft_list = processor.fetch_aircraft_data()

            assert len(aircraft_list) == 1
            assert aircraft_list[0].icao == 'def456'
            assert aircraft_list[0].callsign == 'LH789'

    def test_fetch_aircraft_data_file_not_found(self):
        """Test file source with missing file."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            processor = ADSBProcessor(data_source="/path/to/missing.json")
            aircraft_list = processor.fetch_aircraft_data()

            assert aircraft_list == []

    def test_parse_aircraft_valid_data(self):
        """Test parsing valid aircraft data."""
        processor = ADSBProcessor()
        aircraft_data = {
            'hex': '123abc',
            'flight': 'TEST123 ',
            'lat': 50.0,
            'lon': -1.0,
            'alt_baro': 15000,
            'gs': 300,
            'track': 270,
            'baro_rate': 500,
            'seen': 3
        }

        aircraft = processor.parse_aircraft(aircraft_data)

        assert aircraft.icao == '123abc'
        assert aircraft.callsign == 'TEST123'
        assert aircraft.latitude == 50.0
        assert aircraft.longitude == -1.0
        assert aircraft.altitude == 15000
        assert aircraft.velocity == 300
        assert aircraft.track == 270
        assert aircraft.vertical_rate == 500
        assert aircraft.last_seen == 3

    def test_parse_aircraft_missing_fields(self):
        """Test parsing aircraft with missing optional fields."""
        processor = ADSBProcessor()
        aircraft_data = {
            'hex': '456def',
            'lat': 51.0,
            'lon': 0.0
        }

        aircraft = processor.parse_aircraft(aircraft_data)

        assert aircraft.icao == '456def'
        assert aircraft.callsign == ''
        assert aircraft.latitude == 51.0
        assert aircraft.longitude == 0.0
        assert aircraft.altitude is None

    def test_filter_by_age(self):
        """Test filtering aircraft by age."""
        processor = ADSBProcessor(max_age=10)

        aircraft_list = [
            Aircraft('A1', {'lat': 51.0, 'lon': 0.0, 'alt_baro': 5000, 'seen': 5}),  # OK
            Aircraft('A2', {'lat': 51.0, 'lon': 0.0, 'alt_baro': 5000, 'seen': 15}), # Too old
            Aircraft('A3', {'lat': 51.0, 'lon': 0.0, 'alt_baro': 5000, 'seen': 2}),  # OK
        ]

        filtered = processor.filter_by_age(aircraft_list)

        assert len(filtered) == 2
        assert filtered[0].icao == 'A1'
        assert filtered[1].icao == 'A3'

    def test_filter_by_age_default_seen(self):
        """Test filtering when aircraft has no 'seen' timestamp."""
        processor = ADSBProcessor(max_age=10)

        aircraft = Aircraft('TEST', {'lat': 51.0, 'lon': 0.0, 'alt_baro': 5000})
        # 'seen' defaults to 0 in Aircraft class

        filtered = processor.filter_by_age([aircraft])

        assert len(filtered) == 1  # Should include aircraft with seen=0

    @patch('requests.get')
    def test_fetch_aircraft_data_filters_old_aircraft(self, mock_get):
        """Test that fetch_aircraft_data automatically filters old aircraft."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'aircraft': [
                {'hex': 'new1', 'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000, 'seen': 5},
                {'hex': 'old1', 'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000, 'seen': 100},
                {'hex': 'new2', 'lat': 51.5, 'lon': -0.1, 'alt_baro': 5000, 'seen': 1},
            ]
        }
        mock_get.return_value = mock_response

        processor = ADSBProcessor(
            data_source="http://localhost:8080/data/aircraft.json",
            max_age=30
        )
        aircraft_list = processor.fetch_aircraft_data()

        assert len(aircraft_list) == 2
        assert aircraft_list[0].icao == 'new1'
        assert aircraft_list[1].icao == 'new2'

    @patch('requests.get')
    def test_fetch_aircraft_data_empty_response(self, mock_get):
        """Test handling of empty aircraft list in response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'aircraft': []}
        mock_get.return_value = mock_response

        processor = ADSBProcessor(data_source="http://localhost:8080/data/aircraft.json")
        aircraft_list = processor.fetch_aircraft_data()

        assert aircraft_list == []

    @patch('requests.get')
    def test_fetch_aircraft_data_malformed_json(self, mock_get):
        """Test handling of malformed JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("error", "doc", 0)
        mock_get.return_value = mock_response

        processor = ADSBProcessor(data_source="http://localhost:8080/data/aircraft.json")
        aircraft_list = processor.fetch_aircraft_data()

        assert aircraft_list == []

    def test_is_http_source(self):
        """Test detection of HTTP data sources."""
        processor_http = ADSBProcessor(data_source="http://localhost:8080/data.json")
        processor_https = ADSBProcessor(data_source="https://example.com/data.json")
        processor_file = ADSBProcessor(data_source="/path/to/file.json")

        assert processor_http._is_http_source() is True
        assert processor_https._is_http_source() is True
        assert processor_file._is_http_source() is False
