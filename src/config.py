"""
Configuration module for flight tracker.
Handles loading and accessing configuration from YAML file.
"""
import yaml
from typing import Any, Dict, Optional
from pathlib import Path


class Config:
    """Configuration manager for flight tracker."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration.

        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path
        self.config_data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        """Load configuration from YAML file."""
        with open(self.config_path, 'r') as f:
            self.config_data = yaml.safe_load(f)

        # Set convenience properties
        self.location = self.config_data.get('location', {})
        self.overhead_zone = self.config_data.get('overhead_zone', {})
        self.display = self.config_data.get('display', {})
        self.api = self.config_data.get('api', {})
        self.adsb = self.config_data.get('adsb', {})
        self.logging = self.config_data.get('logging', {})

    def reload(self) -> None:
        """Reload configuration from file."""
        self.load()

    def get_location(self) -> Dict[str, Any]:
        """
        Get location configuration.

        Returns:
            Location configuration dictionary
        """
        return self.location

    def get_overhead_zone(self) -> Dict[str, Any]:
        """
        Get overhead zone configuration.

        Returns:
            Overhead zone configuration dictionary
        """
        return self.overhead_zone

    def get_display_config(self) -> Dict[str, Any]:
        """
        Get display configuration.

        Returns:
            Display configuration dictionary
        """
        return self.display

    def get_api_config(self) -> Dict[str, Any]:
        """
        Get API configuration.

        Returns:
            API configuration dictionary
        """
        return self.api

    def get_adsb_config(self) -> Dict[str, Any]:
        """
        Get ADS-B configuration.

        Returns:
            ADS-B configuration dictionary
        """
        return self.adsb

    def get_logging_config(self) -> Dict[str, Any]:
        """
        Get logging configuration.

        Returns:
            Logging configuration dictionary
        """
        return self.logging

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path.

        Args:
            key: Dot-separated key path (e.g., 'location.latitude')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def validate_required_fields(self) -> bool:
        """
        Validate that required configuration fields are present.

        Returns:
            True if all required fields present, False otherwise
        """
        required_fields = [
            'location.latitude',
            'location.longitude',
        ]

        for field in required_fields:
            if self.get(field) is None:
                return False

        return True
