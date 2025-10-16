#!/bin/bash
# Installation script for Flight Tracker LED Display
# Run with: bash install.sh

set -e  # Exit on error

echo "=========================================="
echo "  Flight Tracker LED Display Installer"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   LED display features will not be available"
    echo ""
fi

# Update system
echo "📦 Updating system packages..."
sudo apt-get update

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt

# Ask about hardware components
echo ""
echo "Hardware Setup Questions:"
echo "========================="
echo ""

read -p "Do you have an RTL-SDR dongle? (y/n): " has_rtlsdr
read -p "Do you have an RGB LED matrix? (y/n): " has_led

# Install RTL-SDR tools if needed
if [ "$has_rtlsdr" = "y" ]; then
    echo ""
    echo "📡 Installing RTL-SDR tools..."
    sudo apt-get install -y rtl-sdr

    echo ""
    read -p "Install ADS-B decoder (readsb)? (y/n): " install_readsb

    if [ "$install_readsb" = "y" ]; then
        echo "📻 Installing readsb..."
        sudo apt-get install -y readsb

        echo ""
        echo "⚙️  Configure readsb location:"
        read -p "Enter your latitude: " lat
        read -p "Enter your longitude: " lon

        # Update readsb config
        sudo bash -c "cat > /etc/default/readsb << EOF
RECEIVER_OPTIONS=\"--device-index 0 --gain -10 --ppm 0\"
DECODER_OPTIONS=\"--max-range 300\"
NET_OPTIONS=\"--net --net-heartbeat 60 --net-ro-size 1280 --net-ro-interval 0.2 --net-http-port 8080 --net-ri-port 30001 --net-ro-port 30002 --net-sbs-port 30003 --net-bi-port 30004,30104\"
JSON_OPTIONS=\"--json-location-accuracy 2\"
RECEIVER_LOCATION=\"--lat $lat --lon $lon\"
EOF"

        echo "✅ readsb configured"
        sudo systemctl enable readsb
        sudo systemctl restart readsb
    fi
else
    echo "⏭️  Skipping RTL-SDR installation"
fi

# Install LED matrix library if needed
if [ "$has_led" = "y" ]; then
    echo ""
    echo "💡 Installing RGB LED Matrix library..."

    if [ ! -d ~/rpi-rgb-led-matrix ]; then
        sudo apt-get install -y python3-dev python3-pillow
        cd ~
        git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
        cd rpi-rgb-led-matrix
        make
        cd bindings/python
        sudo pip3 install .
        cd -
        echo "✅ RGB Matrix library installed"
    else
        echo "✅ RGB Matrix library already installed"
    fi
else
    echo "⏭️  Skipping LED matrix installation"
    echo "   Setting display.enabled to false in config.yaml"
    sed -i 's/enabled: true/enabled: false/g' config.yaml
fi

# Update config.yaml with location
echo ""
echo "⚙️  Updating configuration..."
read -p "Enter your latitude (for overhead detection): " user_lat
read -p "Enter your longitude: " user_lon
read -p "Enter overhead radius in km (default 3.0): " radius
radius=${radius:-3.0}

# Update config.yaml
cat > config_temp.yaml << EOF
location:
  latitude: $user_lat
  longitude: $user_lon
  altitude: 50

overhead_zone:
  radius_km: $radius
  min_altitude_m: 500
  max_altitude_m: 12000

display:
  led_rows: 32
  led_cols: 64
  led_chain: 1
  led_parallel: 1
  brightness: 80
  rotation_seconds: 8
  font_path: "fonts/7x13.bdf"
  enabled: $([[ "$has_led" == "y" ]] && echo "true" || echo "false")

api:
  provider: "opensky"
  api_key: ""
  cache_duration: 300
  request_timeout: 10
  rate_limit_delay: 1

adsb:
  data_source: "http://localhost:8080/data/aircraft.json"
  update_interval: 2
  max_age: 30

logging:
  level: "INFO"
  file: "logs/flight-tracker.log"
  max_bytes: 10485760
  backup_count: 5
EOF

mv config_temp.yaml config.yaml

# Create logs directory
mkdir -p logs

# Run tests
echo ""
echo "🧪 Running tests..."
if python3 -m pytest tests/ -v --tb=short; then
    echo "✅ All tests passed!"
else
    echo "⚠️  Some tests failed. Check configuration."
fi

# Ask about systemd service
echo ""
read -p "Install as systemd service (auto-start on boot)? (y/n): " install_service

if [ "$install_service" = "y" ]; then
    INSTALL_DIR=$(pwd)

    sudo bash -c "cat > /etc/systemd/system/flight-tracker.service << EOF
[Unit]
Description=Flight Tracker LED Display
After=network.target readsb.service

[Service]
ExecStart=/usr/bin/python3 $INSTALL_DIR/src/main.py
WorkingDirectory=$INSTALL_DIR
User=root
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

    sudo systemctl daemon-reload
    sudo systemctl enable flight-tracker

    echo "✅ Systemd service installed"
    echo ""
    read -p "Start service now? (y/n): " start_now

    if [ "$start_now" = "y" ]; then
        sudo systemctl start flight-tracker
        echo "✅ Service started"
        echo ""
        echo "Check status with: sudo systemctl status flight-tracker"
        echo "View logs with: sudo journalctl -u flight-tracker -f"
    fi
fi

echo ""
echo "=========================================="
echo "  Installation Complete! 🎉"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Review config.yaml and adjust settings"
echo "  2. Test: python3 src/main.py"
if [ "$has_led" = "y" ]; then
    echo "  3. Run with LED: sudo python3 src/main.py"
fi
echo ""
echo "Troubleshooting:"
echo "  - Check logs: tail -f logs/flight-tracker.log"
echo "  - Test RTL-SDR: rtl_test"
echo "  - View ADS-B data: curl http://localhost:8080/data/aircraft.json"
echo ""
echo "Happy flight tracking! ✈️"
