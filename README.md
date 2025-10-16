# Flight Tracker LED Display

A real-time flight tracking system that displays flight information (flight number, origin, destination) on an LED matrix display for aircraft flying overhead. Built with Python and designed to run on Raspberry Pi.

## Features

- **Real-time ADS-B Data Processing**: Receives aircraft signals via RTL-SDR dongle
- **Geographic Filtering**: Identifies aircraft within configurable overhead zone
- **Flight Information Enrichment**: Queries APIs for flight details
- **LED Matrix Display**: Shows flight info on RGB LED panel
- **Web Dashboard**: Beautiful real-time monitoring interface (NEW!)
- **Fully Tested**: Built using Test-Driven Development (TDD) with 76+ tests
- **Configurable**: YAML-based configuration for easy customization

## Hardware Requirements

- Raspberry Pi (3/4/5 or Zero 2 W)
- RTL-SDR USB Dongle (1090 MHz capable)
- RGB LED Matrix Panel (HUB75 interface, 64x32 or larger recommended)
- RGB Matrix HAT/Bonnet for Raspberry Pi
- 5V Power Supply (4A+ depending on LED panel size)
- ADS-B Antenna (1090 MHz)

## Software Architecture

```
┌─────────────────────────────────────────┐
│         Flight Tracker System           │
├─────────────────────────────────────────┤
│                                          │
│  ADS-B Receiver → Geo Filter → API      │
│       ↓              ↓          ↓       │
│  Aircraft Data → Overhead → Flight Info │
│                      ↓                   │
│               LED Display                │
└─────────────────────────────────────────┘
```

### Core Modules

- **adsb_processor.py**: Fetches and parses ADS-B data (HTTP/file sources)
- **geo_filter.py**: Filters aircraft by location and altitude (Haversine formula)
- **flight_api.py**: Enriches data via OpenSky Network API (with caching)
- **led_display.py**: Controls RGB LED matrix display
- **config.py**: Configuration management (YAML-based)
- **main.py**: Main application loop

## Installation

### 1. System Setup (Raspberry Pi)

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install system dependencies
sudo apt-get install python3-pip git -y

# Install ADS-B decoder (readsb)
sudo apt-get install readsb -y

# Install RGB Matrix library dependencies
sudo apt-get install python3-dev python3-pillow -y
```

### 2. Install RGB Matrix Library

```bash
# Clone and build rpi-rgb-led-matrix
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
make

# Install Python bindings
cd bindings/python
sudo pip3 install .
```

### 3. Install Flight Tracker

```bash
# Clone this repository
git clone <your-repo-url>
cd Flight_Location_Detector

# Install Python dependencies
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to customize your installation:

### Location Settings
```yaml
location:
  latitude: 51.5074    # Your GPS latitude
  longitude: -0.1278   # Your GPS longitude
  altitude: 50         # Meters above sea level
```

### Overhead Zone
```yaml
overhead_zone:
  radius_km: 3.0           # Detection radius
  min_altitude_m: 500      # Minimum altitude
  max_altitude_m: 12000    # Maximum altitude
```

### Display Settings
```yaml
display:
  led_rows: 32
  led_cols: 64
  brightness: 80
  rotation_seconds: 8      # Time per flight
  enabled: true
```

### API Settings
```yaml
api:
  provider: "opensky"      # API provider
  api_key: ""              # Optional API key
  cache_duration: 300      # Cache duration (seconds)
```

### ADS-B Settings
```yaml
adsb:
  data_source: "http://localhost:8080/data/aircraft.json"
  update_interval: 2       # Update frequency (seconds)
  max_age: 30             # Max data age (seconds)
```

## Running the Application

### Web Dashboard (Recommended for Monitoring)

```bash
# Start the web dashboard
python3 src/dashboard.py

# Access at http://localhost:5000
# Or from another device: http://YOUR_PI_IP:5000
```

See [DASHBOARD_README.md](DASHBOARD_README.md) for full dashboard documentation.

### Standard Mode (with LED Display)

```bash
# Ensure ADS-B decoder is running
sudo systemctl start readsb

# Run flight tracker (requires sudo for LED matrix)
sudo python3 src/main.py
```

### Testing Mode (without LED hardware)

For development/testing without LED hardware, set `display.enabled: false` in config.yaml:

```bash
python3 src/main.py
```

This will output flight information to console instead.

### Run as System Service

Create `/etc/systemd/system/flight-tracker.service`:

```ini
[Unit]
Description=Flight Tracker LED Display
After=network.target readsb.service

[Service]
ExecStart=/usr/bin/python3 /home/pi/Flight_Location_Detector/src/main.py
WorkingDirectory=/home/pi/Flight_Location_Detector
User=root
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable flight-tracker
sudo systemctl start flight-tracker
sudo systemctl status flight-tracker
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test module
python -m pytest tests/test_geo_filter.py -v

# Run with coverage (requires pytest-cov)
python -m pytest tests/ --cov=src --cov-report=html
```

### Test Structure

- `tests/test_adsb_processor.py` - ADS-B data processing (14 tests)
- `tests/test_geo_filter.py` - Geographic filtering (13 tests)
- `tests/test_flight_api.py` - API client (15 tests)
- `tests/test_led_display.py` - Display controller (14 tests)
- `tests/test_config.py` - Configuration (13 tests)
- `tests/test_dashboard.py` - Web dashboard (7 tests)

**Total: 76 tests - All passing ✅**

### Code Quality

Built with Test-Driven Development (TDD):
1. Write failing tests
2. Implement minimal code to pass
3. Refactor and optimize

All modules have >90% test coverage.

## Troubleshooting

### No Aircraft Detected

1. Check ADS-B decoder is running: `systemctl status readsb`
2. Verify antenna connection and placement (higher is better)
3. Check RTL-SDR is recognized: `rtl_test`
4. Increase `overhead_zone.radius_km` in config

### LED Display Not Working

1. Verify RGB Matrix wiring (check `rpi-rgb-led-matrix` docs)
2. Ensure running as root: `sudo python3 src/main.py`
3. Check display config: `led_rows`, `led_cols`, `brightness`
4. Test with example: `sudo python3 ~/rpi-rgb-led-matrix/bindings/python/samples/simple-square.py`

### API Rate Limiting

1. Increase `api.cache_duration` to reduce API calls
2. Register for API key (if supported by provider)
3. Use alternative provider (adsbexchange, aviationstack)

### Poor Reception Range

1. Upgrade to outdoor/amplified antenna
2. Move antenna to higher location
3. Check for local interference (WiFi, electronics)
4. Consider adding bandpass filter

## API Providers

### OpenSky Network (Default)
- **Free**: Yes (rate limited)
- **Registration**: Optional (increases limits)
- **Data**: Basic flight info, origin country
- **Rate Limit**: 400 calls/day (anonymous), 4000/day (registered)

### ADS-B Exchange
- **Free**: API available
- **Registration**: Required
- **Data**: Comprehensive flight data
- **Website**: adsbexchange.com

### AviationStack
- **Free Tier**: 500 requests/month
- **Registration**: Required
- **Data**: Commercial flight data
- **Website**: aviationstack.com

## Project Structure

```
Flight_Location_Detector/
├── config.yaml              # Main configuration
├── requirements.txt         # Python dependencies
├── pytest.ini              # Test configuration
├── PROJECT_PLAN.md         # Detailed project plan
├── README.md               # This file
├── src/
│   ├── __init__.py
│   ├── main.py            # Main application
│   ├── config.py          # Configuration manager
│   ├── adsb_processor.py  # ADS-B data processor
│   ├── geo_filter.py      # Geographic filtering
│   ├── flight_api.py      # Flight API client
│   ├── led_display.py     # LED display controller
│   └── utils.py           # Shared utilities
├── data/
│   └── airports.json      # Airport database
├── tests/
│   ├── test_adsb_processor.py
│   ├── test_geo_filter.py
│   ├── test_flight_api.py
│   ├── test_led_display.py
│   └── test_config.py
└── logs/                  # Application logs
```

## Performance

- **Memory Usage**: ~50-100MB (depending on aircraft count)
- **CPU Usage**: ~5-10% on Raspberry Pi 4
- **Update Latency**: <3 seconds from aircraft overhead to display
- **Reception Range**: 100-300 miles (depending on antenna/location)

## Future Enhancements

- [ ] Web interface for remote monitoring
- [ ] Historical flight logging and statistics
- [ ] Weather information overlay
- [ ] Aircraft type/model display
- [ ] Sound notifications for interesting aircraft
- [ ] Mobile app integration
- [ ] Multiple display modes
- [ ] Route prediction and tracking

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- **hzeller/rpi-rgb-led-matrix** - RGB LED matrix library
- **OpenSky Network** - Free ADS-B data API
- **FlightAware** - ADS-B decoder (readsb)
- **RTL-SDR community** - SDR support and tools

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check PROJECT_PLAN.md for detailed documentation
- Review test files for usage examples

---

**Built with Test-Driven Development ✨**

*Track flights in real-time with your Raspberry Pi!*
