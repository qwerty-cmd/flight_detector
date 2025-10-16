"""
WSGI entry point for deployment platforms.
"""
import os
from src.dashboard import FlightTrackerDashboard

# Create dashboard instance
dashboard = FlightTrackerDashboard('config.yaml')

# Get the Flask app
app = dashboard.app

# Start background updates when in demo mode
if os.environ.get('DEMO_MODE') == 'true':
    print("Running in DEMO mode - using simulated data")
    dashboard.start_background_updates(interval=5)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
