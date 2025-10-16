"""
Tests for configuration module.
Following TDD: Write tests first, then implement.
"""
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from src.config import Config


class TestConfig:
    """Test suite for Config class."""

    def test_load_default_config(self):
        """Test loading default configuration."""
        yaml_content = """
location:
  latitude: 51.5074
  longitude: -0.1278
  altitude: 50

overhead_zone:
  radius_km: 3.0
  min_altitude_m: 500
  max_altitude_m: 12000
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = Config('test.yaml')

            assert config.location['latitude'] == 51.5074
            assert config.location['longitude'] == -0.1278
            assert config.overhead_zone['radius_km'] == 3.0

    def test_config_file_not_found(self):
        """Test behavior when config file is not found."""
        with patch('builtins.open', side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                Config('missing.yaml')

    def test_get_location(self):
        """Test getting location configuration."""
        yaml_content = """
location:
  latitude: 40.7128
  longitude: -74.0060
  altitude: 10
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = Config('test.yaml')

            assert config.get_location() == {
                'latitude': 40.7128,
                'longitude': -74.0060,
                'altitude': 10
            }

    def test_get_overhead_zone_config(self):
        """Test getting overhead zone configuration."""
        yaml_content = """
overhead_zone:
  radius_km: 5.0
  min_altitude_m: 1000
  max_altitude_m: 15000
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = Config('test.yaml')

            zone = config.get_overhead_zone()
            assert zone['radius_km'] == 5.0
            assert zone['min_altitude_m'] == 1000
            assert zone['max_altitude_m'] == 15000

    def test_get_display_config(self):
        """Test getting display configuration."""
        yaml_content = """
display:
  led_rows: 64
  led_cols: 128
  brightness: 90
  rotation_seconds: 10
  enabled: true
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = Config('test.yaml')

            display = config.get_display_config()
            assert display['led_rows'] == 64
            assert display['led_cols'] == 128
            assert display['brightness'] == 90
            assert display['enabled'] is True

    def test_get_api_config(self):
        """Test getting API configuration."""
        yaml_content = """
api:
  provider: "adsbexchange"
  api_key: "test123"
  cache_duration: 600
  request_timeout: 20
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = Config('test.yaml')

            api = config.get_api_config()
            assert api['provider'] == 'adsbexchange'
            assert api['api_key'] == 'test123'
            assert api['cache_duration'] == 600

    def test_get_adsb_config(self):
        """Test getting ADS-B configuration."""
        yaml_content = """
adsb:
  data_source: "http://custom:9090/data.json"
  update_interval: 5
  max_age: 60
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = Config('test.yaml')

            adsb = config.get_adsb_config()
            assert adsb['data_source'] == 'http://custom:9090/data.json'
            assert adsb['update_interval'] == 5
            assert adsb['max_age'] == 60

    def test_get_logging_config(self):
        """Test getting logging configuration."""
        yaml_content = """
logging:
  level: "DEBUG"
  file: "test.log"
  max_bytes: 5242880
  backup_count: 3
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = Config('test.yaml')

            logging = config.get_logging_config()
            assert logging['level'] == 'DEBUG'
            assert logging['file'] == 'test.log'
            assert logging['max_bytes'] == 5242880

    def test_get_value_with_default(self):
        """Test getting configuration value with default."""
        yaml_content = """
test:
  value: 123
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = Config('test.yaml')

            assert config.get('test.value', 999) == 123
            assert config.get('missing.value', 999) == 999

    def test_nested_config_access(self):
        """Test accessing nested configuration values."""
        yaml_content = """
level1:
  level2:
    level3:
      value: "deep"
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = Config('test.yaml')

            assert config.get('level1.level2.level3.value') == 'deep'

    def test_validate_required_fields(self):
        """Test validation of required configuration fields."""
        yaml_content = """
location:
  latitude: 51.5074
  longitude: -0.1278
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = Config('test.yaml')

            # Should have required location fields
            assert config.validate_required_fields() is True

    def test_validate_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        yaml_content = """
overhead_zone:
  radius_km: 3.0
"""
        with patch('builtins.open', mock_open(read_data=yaml_content)):
            config = Config('test.yaml')

            # Should fail - missing location
            assert config.validate_required_fields() is False

    def test_reload_config(self):
        """Test reloading configuration from file."""
        yaml_content_1 = """
location:
  latitude: 51.5074
"""
        yaml_content_2 = """
location:
  latitude: 40.7128
"""
        with patch('builtins.open', mock_open(read_data=yaml_content_1)):
            config = Config('test.yaml')
            assert config.location['latitude'] == 51.5074

        with patch('builtins.open', mock_open(read_data=yaml_content_2)):
            config.reload()
            assert config.location['latitude'] == 40.7128
