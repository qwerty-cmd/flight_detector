"""
Utility functions for the flight tracker system.
"""
from typing import Dict, Any


class Aircraft:
    """Represents an aircraft with its current state."""

    def __init__(self, icao: str, data: Dict[str, Any]):
        self.icao = icao
        # ADS-B data uses 'flight' field, but also support 'callsign'
        callsign = data.get('flight', data.get('callsign', ''))
        self.callsign = callsign.strip() if callsign else ''
        self.latitude = data.get('lat')
        self.longitude = data.get('lon')
        self.altitude = data.get('alt_baro')  # Barometric altitude in feet
        self.velocity = data.get('gs')  # Ground speed in knots
        self.track = data.get('track')  # Heading in degrees
        self.vertical_rate = data.get('baro_rate')  # ft/min
        self.last_seen = data.get('seen', 0)  # Seconds since last message

        # Flight information (to be filled by API)
        self.flight_number = None
        self.origin_country = None
        self.destination_country = None
        self.origin_airport = None
        self.destination_airport = None

    def has_position(self) -> bool:
        """Check if aircraft has valid position data."""
        return (self.latitude is not None and
                self.longitude is not None and
                self.altitude is not None)

    def __repr__(self) -> str:
        return (f"Aircraft(icao={self.icao}, callsign={self.callsign}, "
                f"lat={self.latitude}, lon={self.longitude}, alt={self.altitude})")
