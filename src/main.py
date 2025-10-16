"""
Main application for flight tracker LED display.
"""
import time
import logging
from pathlib import Path
from src.config import Config
from src.adsb_processor import ADSBProcessor
from src.geo_filter import GeoFilter
from src.flight_api import FlightAPIClient
from src.led_display import LEDDisplay


class FlightTracker:
    """Main flight tracker application."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize flight tracker.

        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        self.config = Config(config_path)

        # Validate configuration
        if not self.config.validate_required_fields():
            raise ValueError("Invalid configuration: missing required fields")

        # Initialize components
        self._init_logging()
        self._init_components()

    def _init_logging(self) -> None:
        """Initialize logging system."""
        log_config = self.config.get_logging_config()
        log_level = log_config.get('level', 'INFO')
        log_file = log_config.get('file', 'logs/flight-tracker.log')

        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

        self.logger = logging.getLogger('FlightTracker')
        self.logger.info("Flight Tracker initialized")

    def _init_components(self) -> None:
        """Initialize all application components."""
        # Get configuration sections
        location = self.config.get_location()
        overhead_zone = self.config.get_overhead_zone()
        adsb_config = self.config.get_adsb_config()
        api_config = self.config.get_api_config()
        display_config = self.config.get_display_config()

        # Initialize ADS-B processor
        self.adsb_processor = ADSBProcessor(
            data_source=adsb_config.get('data_source'),
            max_age=adsb_config.get('max_age', 30)
        )

        # Initialize geographic filter
        self.geo_filter = GeoFilter(
            latitude=location['latitude'],
            longitude=location['longitude'],
            radius_km=overhead_zone.get('radius_km', 3.0),
            min_altitude_m=overhead_zone.get('min_altitude_m', 500),
            max_altitude_m=overhead_zone.get('max_altitude_m')
        )

        # Initialize flight API client
        self.flight_api = FlightAPIClient(
            provider=api_config.get('provider', 'opensky'),
            api_key=api_config.get('api_key', ''),
            cache_duration=api_config.get('cache_duration', 300),
            request_timeout=api_config.get('request_timeout', 10)
        )

        # Initialize LED display
        self.led_display = LEDDisplay(display_config)

        self.logger.info("All components initialized successfully")

    def run(self) -> None:
        """Run the main application loop."""
        self.logger.info("Starting flight tracker main loop")

        update_interval = self.config.get('adsb.update_interval', 2)
        rotation_seconds = self.config.get('display.rotation_seconds', 8)

        current_overhead = []
        last_display_update = time.time()

        try:
            while True:
                # Fetch aircraft data
                aircraft_list = self.adsb_processor.fetch_aircraft_data()
                self.logger.debug(f"Fetched {len(aircraft_list)} aircraft")

                # Filter for overhead aircraft
                overhead_aircraft = self.geo_filter.filter_overhead_aircraft(aircraft_list)
                self.logger.debug(f"Found {len(overhead_aircraft)} overhead aircraft")

                if overhead_aircraft:
                    # Enrich with flight information if new aircraft
                    for aircraft in overhead_aircraft:
                        if aircraft.icao not in [a.icao for a in current_overhead]:
                            self.flight_api.enrich_aircraft(aircraft)
                            self.logger.info(
                                f"New overhead aircraft: {aircraft.callsign or aircraft.icao}"
                            )

                    # Update display queue
                    self.led_display.update_queue(overhead_aircraft)
                    current_overhead = overhead_aircraft

                    # Rotate display
                    if time.time() - last_display_update >= rotation_seconds:
                        next_aircraft = self.led_display.get_next_aircraft()
                        if next_aircraft:
                            self.led_display.show_flight(next_aircraft)
                            last_display_update = time.time()

                else:
                    # No aircraft overhead
                    if current_overhead:
                        self.logger.info("No aircraft overhead")
                        current_overhead = []

                    self.led_display.show_waiting_message()

                # Wait before next update
                time.sleep(update_interval)

        except KeyboardInterrupt:
            self.logger.info("Shutting down flight tracker")
            self.shutdown()

    def shutdown(self) -> None:
        """Clean shutdown of the application."""
        self.logger.info("Cleaning up...")
        self.led_display.clear()
        self.logger.info("Flight tracker stopped")


def main():
    """Main entry point."""
    import sys

    config_path = "config.yaml"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    try:
        tracker = FlightTracker(config_path)
        tracker.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
