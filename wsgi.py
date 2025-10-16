"""
WSGI entry point for deployment platforms.
"""
import os
import sys

# Add the project root to the path
sys.path.insert(0, os.path.dirname(__file__))

from src.dashboard import FlightTrackerDashboard

# Create dashboard instance
try:
    dashboard = FlightTrackerDashboard('config.yaml')

    # Get the Flask app
    app = dashboard.app

    # Start background updates when in demo mode (not for Vercel serverless)
    if os.environ.get('DEMO_MODE') == 'true':
        print("Running in DEMO mode - using simulated data")
        # Only start background updates for non-serverless platforms
        if os.environ.get('VERCEL') != '1':
            dashboard.start_background_updates(interval=5)

except Exception as e:
    print(f"Error initializing dashboard: {e}")
    import traceback
    traceback.print_exc()

    # Create a minimal Flask app for error display
    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route('/')
    def error():
        return jsonify({
            'error': 'Dashboard initialization failed',
            'message': str(e),
            'demo_mode': os.environ.get('DEMO_MODE'),
            'vercel': os.environ.get('VERCEL')
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
