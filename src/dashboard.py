"""
Web dashboard for flight tracker monitoring.
Provides real-time status, statistics, and control interface.
"""
import os
import time
import json
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from src.config import Config
from src.adsb_processor import ADSBProcessor
from src.geo_filter import GeoFilter
from src.flight_api import FlightAPIClient


class FlightTrackerDashboard:
    """Web dashboard for flight tracker."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize dashboard.

        Args:
            config_path: Path to configuration file
        """
        self.app = Flask(__name__,
                        template_folder='../dashboard/templates',
                        static_folder='../dashboard/static')
        CORS(self.app)

        # Load configuration
        self.config = Config(config_path)

        # Initialize components
        self._init_components()

        # Dashboard state
        self.stats = {
            'total_aircraft_seen': 0,
            'overhead_aircraft_count': 0,
            'last_update': None,
            'uptime_start': time.time(),
            'api_calls': 0,
            'errors': 0
        }

        self.current_aircraft = []
        self.overhead_aircraft = []
        self.recent_flights = []

        # Setup routes
        self._setup_routes()

    def _init_components(self) -> None:
        """Initialize flight tracker components."""
        location = self.config.get_location()
        overhead_zone = self.config.get_overhead_zone()
        adsb_config = self.config.get_adsb_config()
        api_config = self.config.get_api_config()

        self.adsb_processor = ADSBProcessor(
            data_source=adsb_config.get('data_source'),
            max_age=adsb_config.get('max_age', 30)
        )

        self.geo_filter = GeoFilter(
            latitude=location['latitude'],
            longitude=location['longitude'],
            radius_km=overhead_zone.get('radius_km', 3.0),
            min_altitude_m=overhead_zone.get('min_altitude_m', 500),
            max_altitude_m=overhead_zone.get('max_altitude_m')
        )

        self.flight_api = FlightAPIClient(
            provider=api_config.get('provider', 'opensky'),
            api_key=api_config.get('api_key', ''),
            cache_duration=api_config.get('cache_duration', 300)
        )

    def _setup_routes(self) -> None:
        """Setup Flask routes."""

        @self.app.route('/')
        def index():
            """Dashboard home page."""
            return render_template('dashboard.html')

        @self.app.route('/api/status')
        def status():
            """Get system status."""
            uptime = time.time() - self.stats['uptime_start']
            return jsonify({
                'status': 'running',
                'uptime_seconds': int(uptime),
                'uptime_formatted': self._format_uptime(uptime),
                'last_update': self.stats['last_update'],
                'location': {
                    'latitude': self.config.get('location.latitude'),
                    'longitude': self.config.get('location.longitude'),
                    'name': 'Footscray, Melbourne, VIC'
                },
                'overhead_zone': {
                    'radius_km': self.config.get('overhead_zone.radius_km'),
                    'min_altitude_m': self.config.get('overhead_zone.min_altitude_m'),
                    'max_altitude_m': self.config.get('overhead_zone.max_altitude_m')
                }
            })

        @self.app.route('/api/stats')
        def stats():
            """Get statistics."""
            return jsonify(self.stats)

        @self.app.route('/api/aircraft')
        def aircraft():
            """Get current aircraft list."""
            return jsonify({
                'total': len(self.current_aircraft),
                'overhead': len(self.overhead_aircraft),
                'aircraft': [self._aircraft_to_dict(a) for a in self.current_aircraft]
            })

        @self.app.route('/api/overhead')
        def overhead():
            """Get overhead aircraft."""
            return jsonify({
                'count': len(self.overhead_aircraft),
                'aircraft': [self._aircraft_to_dict(a) for a in self.overhead_aircraft]
            })

        @self.app.route('/api/recent')
        def recent():
            """Get recent flights."""
            return jsonify({
                'flights': self.recent_flights[-20:]  # Last 20 flights
            })

        @self.app.route('/api/update')
        def update():
            """Trigger manual update."""
            try:
                self._update_data()
                return jsonify({'success': True, 'message': 'Updated successfully'})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.app.route('/api/config')
        def config():
            """Get configuration."""
            return jsonify({
                'location': self.config.get_location(),
                'overhead_zone': self.config.get_overhead_zone(),
                'api': {
                    'provider': self.config.get('api.provider'),
                    'cache_duration': self.config.get('api.cache_duration')
                },
                'adsb': {
                    'data_source': self.config.get('adsb.data_source'),
                    'update_interval': self.config.get('adsb.update_interval')
                }
            })

    def _aircraft_to_dict(self, aircraft) -> dict:
        """Convert Aircraft object to dictionary."""
        distance = None
        if aircraft.latitude and aircraft.longitude:
            distance = round(self.geo_filter.calculate_distance(
                aircraft.latitude, aircraft.longitude
            ), 2)

        return {
            'icao': aircraft.icao,
            'callsign': aircraft.callsign,
            'latitude': aircraft.latitude,
            'longitude': aircraft.longitude,
            'altitude': aircraft.altitude,
            'velocity': aircraft.velocity,
            'track': aircraft.track,
            'vertical_rate': aircraft.vertical_rate,
            'distance_km': distance,
            'origin_country': aircraft.origin_country,
            'destination_country': aircraft.destination_country,
            'flight_number': aircraft.flight_number,
            'last_seen': aircraft.last_seen
        }

    def _format_uptime(self, seconds: float) -> str:
        """Format uptime seconds to human readable."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours}h {minutes}m {secs}s"

    def _update_data(self) -> None:
        """Update aircraft data."""
        try:
            # Fetch aircraft data
            aircraft_list = self.adsb_processor.fetch_aircraft_data()
            self.current_aircraft = aircraft_list

            if aircraft_list:
                self.stats['total_aircraft_seen'] += len(aircraft_list)

            # Filter overhead aircraft
            overhead = self.geo_filter.filter_overhead_aircraft(aircraft_list)

            # Track new overhead aircraft
            for aircraft in overhead:
                if aircraft.icao not in [a['icao'] for a in self.recent_flights]:
                    # Enrich with flight data
                    self.flight_api.enrich_aircraft(aircraft)
                    self.stats['api_calls'] += 1

                    # Add to recent flights
                    self.recent_flights.append({
                        'icao': aircraft.icao,
                        'callsign': aircraft.callsign or 'Unknown',
                        'origin': aircraft.origin_country or 'Unknown',
                        'destination': aircraft.destination_country or 'Unknown',
                        'timestamp': datetime.now().isoformat(),
                        'altitude': aircraft.altitude
                    })

            self.overhead_aircraft = overhead
            self.stats['overhead_aircraft_count'] = len(overhead)
            self.stats['last_update'] = datetime.now().isoformat()

        except Exception as e:
            self.stats['errors'] += 1
            print(f"Error updating data: {e}")

    def start_background_updates(self, interval: int = 5):
        """
        Start background data updates.

        Args:
            interval: Update interval in seconds
        """
        def update_loop():
            while True:
                self._update_data()
                time.sleep(interval)

        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """
        Run the dashboard server.

        Args:
            host: Host address
            port: Port number
            debug: Debug mode
        """
        # Start background updates
        update_interval = self.config.get('adsb.update_interval', 5)
        self.start_background_updates(interval=update_interval)

        print(f"Dashboard running at http://{host}:{port}")
        print("Press Ctrl+C to stop")

        self.app.run(host=host, port=port, debug=debug, use_reloader=False)


def main():
    """Main entry point for dashboard."""
    import sys

    config_path = "config.yaml"
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    dashboard = FlightTrackerDashboard(config_path)
    dashboard.run(debug=True)


if __name__ == '__main__':
    main()
