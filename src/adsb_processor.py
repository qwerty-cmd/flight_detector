"""
ADS-B data processor module.
Fetches and processes aircraft data from ADS-B sources.
"""
import json
import requests
from typing import List, Dict, Any
from src.utils import Aircraft


class ADSBProcessor:
    """Process ADS-B data from various sources."""

    def __init__(
        self,
        data_source: str = "http://localhost:8080/data/aircraft.json",
        max_age: int = 30
    ):
        """
        Initialize ADS-B processor.

        Args:
            data_source: URL or file path to aircraft data (JSON format)
            max_age: Maximum age of aircraft data in seconds
        """
        self.data_source = data_source
        self.max_age = max_age

    def _is_http_source(self) -> bool:
        """Check if data source is HTTP/HTTPS URL."""
        return self.data_source.startswith(('http://', 'https://'))

    def fetch_aircraft_data(self) -> List[Aircraft]:
        """
        Fetch aircraft data from configured source.

        Returns:
            List of Aircraft objects
        """
        try:
            if self._is_http_source():
                return self._fetch_from_http()
            else:
                return self._fetch_from_file()
        except Exception as e:
            print(f"Error fetching aircraft data: {e}")
            return []

    def _fetch_from_http(self) -> List[Aircraft]:
        """
        Fetch aircraft data from HTTP source.

        Returns:
            List of Aircraft objects
        """
        try:
            response = requests.get(self.data_source, timeout=10)
            response.raise_for_status()
            data = response.json()

            aircraft_list = []
            for aircraft_data in data.get('aircraft', []):
                aircraft = self.parse_aircraft(aircraft_data)
                aircraft_list.append(aircraft)

            # Filter by age
            return self.filter_by_age(aircraft_list)

        except requests.RequestException as e:
            print(f"HTTP request error: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def _fetch_from_file(self) -> List[Aircraft]:
        """
        Fetch aircraft data from local file.

        Returns:
            List of Aircraft objects
        """
        try:
            with open(self.data_source, 'r') as f:
                data = json.load(f)

            aircraft_list = []
            for aircraft_data in data.get('aircraft', []):
                aircraft = self.parse_aircraft(aircraft_data)
                aircraft_list.append(aircraft)

            # Filter by age
            return self.filter_by_age(aircraft_list)

        except FileNotFoundError:
            print(f"File not found: {self.data_source}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []

    def parse_aircraft(self, aircraft_data: Dict[str, Any]) -> Aircraft:
        """
        Parse raw aircraft data into Aircraft object.

        Args:
            aircraft_data: Raw aircraft data dictionary

        Returns:
            Aircraft object
        """
        icao = aircraft_data.get('hex', '')
        return Aircraft(icao=icao, data=aircraft_data)

    def filter_by_age(self, aircraft_list: List[Aircraft]) -> List[Aircraft]:
        """
        Filter aircraft by age (time since last message).

        Args:
            aircraft_list: List of Aircraft objects

        Returns:
            Filtered list of Aircraft objects
        """
        filtered = []
        for aircraft in aircraft_list:
            if aircraft.last_seen <= self.max_age:
                filtered.append(aircraft)

        return filtered
