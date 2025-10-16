"""
Flight API client module.
Enriches aircraft data with flight information from various APIs.
"""
import time
import json
import requests
from typing import Dict, Any, Optional, List
from pathlib import Path
from src.utils import Aircraft


class FlightAPIClient:
    """Client for flight information APIs."""

    def __init__(
        self,
        provider: str = "opensky",
        api_key: str = "",
        cache_duration: int = 300,
        request_timeout: int = 10
    ):
        """
        Initialize flight API client.

        Args:
            provider: API provider name (opensky, adsbexchange, etc.)
            api_key: API key if required
            cache_duration: Cache duration in seconds
            request_timeout: Request timeout in seconds
        """
        self.provider = provider
        self.api_key = api_key
        self.cache_duration = cache_duration
        self.request_timeout = request_timeout
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._last_request_time = 0
        self._airport_db = self._load_airport_database()

    def _load_airport_database(self) -> Dict[str, Dict[str, Any]]:
        """
        Load airport database from local file.

        Returns:
            Dictionary of airport data
        """
        try:
            airport_file = Path(__file__).parent.parent / 'data' / 'airports.json'
            with open(airport_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Airport database not found")
            return {}
        except Exception as e:
            print(f"Error loading airport database: {e}")
            return {}

    def _is_cached(self, icao: str) -> bool:
        """
        Check if aircraft data is cached and not expired.

        Args:
            icao: Aircraft ICAO code

        Returns:
            True if cached and valid, False otherwise
        """
        if icao not in self._cache:
            return False

        cache_entry = self._cache[icao]
        age = time.time() - cache_entry['timestamp']
        return age < self.cache_duration

    def _get_cached_data(self, icao: str) -> Dict[str, Any]:
        """
        Get cached data for aircraft.

        Args:
            icao: Aircraft ICAO code

        Returns:
            Cached data dictionary
        """
        return self._cache.get(icao, {})

    def _cache_data(self, icao: str, data: Dict[str, Any]) -> None:
        """
        Cache flight data for aircraft.

        Args:
            icao: Aircraft ICAO code
            data: Data to cache
        """
        self._cache[icao] = {
            **data,
            'timestamp': time.time()
        }

    def _rate_limit(self, delay: float = 1.0) -> None:
        """
        Implement rate limiting between requests.

        Args:
            delay: Minimum delay between requests in seconds
        """
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < delay:
            time.sleep(delay - time_since_last)
        self._last_request_time = time.time()

    def enrich_aircraft(self, aircraft: Aircraft) -> None:
        """
        Enrich aircraft with flight information from API.

        Args:
            aircraft: Aircraft object to enrich
        """
        # Check cache first
        if self._is_cached(aircraft.icao):
            cached_data = self._get_cached_data(aircraft.icao)
            aircraft.origin_country = cached_data.get('origin_country')
            aircraft.destination_country = cached_data.get('destination_country')
            aircraft.origin_airport = cached_data.get('origin_airport')
            aircraft.destination_airport = cached_data.get('destination_airport')
            aircraft.flight_number = cached_data.get('flight_number')
            return

        # Fetch from API based on provider
        if self.provider == "opensky":
            self._enrich_from_opensky(aircraft)
        elif self.provider == "adsbexchange":
            self._enrich_from_adsbexchange(aircraft)
        else:
            print(f"Unsupported provider: {self.provider}")

    def _enrich_from_opensky(self, aircraft: Aircraft) -> None:
        """
        Enrich aircraft data using OpenSky Network API.

        Args:
            aircraft: Aircraft object to enrich
        """
        try:
            self._rate_limit(1.0)

            url = f"https://opensky-network.org/api/states/all?icao24={aircraft.icao.lower()}"
            response = requests.get(url, timeout=self.request_timeout)
            response.raise_for_status()

            data = response.json()
            states = data.get('states')

            if states and len(states) > 0:
                state = states[0]
                # OpenSky state vector format:
                # [0] icao24, [1] callsign, [2] origin_country, ...
                origin_country = state[2] if len(state) > 2 else None

                aircraft.origin_country = origin_country

                # Cache the data
                self._cache_data(aircraft.icao, {
                    'origin_country': origin_country
                })

        except Exception as e:
            print(f"Error enriching from OpenSky: {e}")

    def _enrich_from_adsbexchange(self, aircraft: Aircraft) -> None:
        """
        Enrich aircraft data using ADS-B Exchange API.

        Args:
            aircraft: Aircraft object to enrich
        """
        # Placeholder for ADS-B Exchange implementation
        print("ADS-B Exchange integration not yet implemented")

    def _extract_airports_from_callsign(self, callsign: str) -> Optional[Dict[str, str]]:
        """
        Attempt to extract airport codes from callsign.

        Args:
            callsign: Aircraft callsign

        Returns:
            Dictionary with origin/destination if found, None otherwise
        """
        if not callsign:
            return None

        # This is a simplified implementation
        # Real implementation would need airline route databases
        return None

    def _parse_route_from_callsign(self, callsign: str) -> Optional[Dict[str, Any]]:
        """
        Parse route information from callsign.

        Args:
            callsign: Aircraft callsign

        Returns:
            Route information if available, None otherwise
        """
        if not callsign:
            return None

        # Placeholder - actual implementation would need route database
        return None

    def enrich_multiple_aircraft(self, aircraft_list: List[Aircraft]) -> None:
        """
        Enrich multiple aircraft with flight information.

        Args:
            aircraft_list: List of Aircraft objects to enrich
        """
        for aircraft in aircraft_list:
            self.enrich_aircraft(aircraft)
