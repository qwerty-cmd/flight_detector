# Flight Tracker LED Display - Project Plan

## Project Overview
Real-time flight information display system that shows flight number, origin country, and destination for aircraft flying overhead, displayed on an LED matrix board connected to a Raspberry Pi.

---

## Hardware Requirements

### Essential Components
1. **Raspberry Pi**
   - Recommended: Raspberry Pi 4 (4GB+ RAM) or Raspberry Pi 5
   - Alternative: Raspberry Pi 3B+ or Zero 2 W (budget option)

2. **RTL-SDR USB Dongle**
   - Chipset: RTL2832U with R820T2 tuner
   - Frequency range: Must cover 1090 MHz (ADS-B frequency)
   - Examples: NooElec NESDR, FlightAware Pro Stick Plus
   - Cost: $25-40

3. **ADS-B Antenna**
   - 1090 MHz optimized antenna
   - Options:
     - Basic dipole antenna (often included with RTL-SDR)
     - Upgraded external antenna for better range
     - DIY antenna (can be built from coax cable)

4. **LED Matrix Display**
   - RGB LED Matrix Panel (HUB75 interface)
   - Recommended sizes: 64x32 or 64x64 pixels
   - Pixel pitch: P3, P4, or P5
   - Cost: $20-60 depending on size

5. **LED Matrix HAT/Adapter**
   - Adafruit RGB Matrix HAT or Bonnet
   - Alternative: Electrodragon RGB Matrix Panel Driver Board
   - Cost: $15-25

6. **Power Supply**
   - 5V power supply (4A-10A depending on LED panel size)
   - Separate power for LED panel recommended
   - Cost: $10-20

### Optional Components
- GPS module (for precise location if Pi doesn't have GPS)
- External case/enclosure
- Heatsinks and cooling for Raspberry Pi

---

## Software Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Flight Tracker System                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌───────────────┐      ┌──────────┐ │
│  │  ADS-B       │─────▶│  Flight Data  │─────▶│   LED    │ │
│  │  Receiver    │      │  Processor    │      │ Display  │ │
│  └──────────────┘      └───────────────┘      └──────────┘ │
│         │                      │                            │
│         │                      │                            │
│   RTL-SDR Dongle        ┌──────▼─────┐                     │
│   dump1090/readsb       │  Flight    │                     │
│                         │  API       │                     │
│                         │  Client    │                     │
│                         └────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

### Software Stack

1. **Operating System**
   - Raspberry Pi OS (64-bit recommended)
   - Lite version acceptable (headless operation)

2. **ADS-B Decoder**
   - Primary: `readsb` (modern, actively maintained)
   - Alternative: `dump1090-fa` (FlightAware version)
   - Output: JSON data via HTTP or file

3. **Python Application** (Main Application)
   - Language: Python 3.9+
   - Core modules:
     - `adsb_processor.py` - Parse ADS-B data
     - `flight_api.py` - Query flight information APIs
     - `geo_filter.py` - Filter overhead flights
     - `led_display.py` - LED matrix control
     - `main.py` - Main application loop
     - `config.py` - Configuration management

4. **LED Matrix Library**
   - `rpi-rgb-led-matrix` (C++ library with Python bindings)
   - High performance, widely used
   - GitHub: hzeller/rpi-rgb-led-matrix

5. **Python Dependencies**
   - `requests` - HTTP API calls
   - `pyModeS` - ADS-B message decoding (optional)
   - `geopy` - Geographic calculations
   - `python-dateutil` - Time parsing
   - `rgbmatrix` - LED matrix bindings

---

## Implementation Phases

### Phase 1: Hardware Setup & Testing
**Duration: 1-2 days**

#### Tasks:
1. Assemble hardware components
   - Connect LED matrix to Raspberry Pi via HAT/adapter
   - Connect RTL-SDR dongle to USB port
   - Attach ADS-B antenna to RTL-SDR
   - Set up power supplies

2. Install Raspberry Pi OS
   - Flash OS to SD card
   - Configure WiFi/Ethernet
   - Enable SSH for remote access
   - Update system packages

3. Test LED matrix display
   - Install `rpi-rgb-led-matrix` library
   - Run example demos
   - Verify display works correctly

4. Test RTL-SDR reception
   - Install RTL-SDR drivers
   - Test reception with basic tools
   - Verify 1090 MHz reception

**Deliverables:**
- Fully assembled hardware
- Working LED display with test patterns
- Confirmed ADS-B signal reception

---

### Phase 2: ADS-B Data Reception
**Duration: 2-3 days**

#### Tasks:
1. Install ADS-B decoder software
   ```bash
   # Install readsb
   sudo apt-get update
   sudo apt-get install readsb
   ```

2. Configure ADS-B decoder
   - Set location coordinates (lat/lon)
   - Configure RTL-SDR device
   - Enable JSON output
   - Set up data persistence

3. Optimize antenna placement
   - Test different locations
   - Maximize aircraft detection range
   - Document reception statistics

4. Create Python ADS-B data parser
   - Read JSON data from readsb
   - Parse aircraft positions
   - Extract ICAO codes, callsigns, positions
   - Implement data refresh loop

**Deliverables:**
- Running ADS-B decoder (24/7 operation)
- Python module to read aircraft data
- Reception range baseline (document max distance)

---

### Phase 3: Geographic Filtering
**Duration: 1-2 days**

#### Tasks:
1. Define "overhead" criteria
   - Maximum distance from location (e.g., 2-5 km radius)
   - Minimum altitude (e.g., filter out ground aircraft)
   - Maximum altitude (optional, to exclude very high flights)
   - Bearing/angle considerations

2. Implement geo-calculation functions
   - Calculate distance between points (Haversine formula)
   - Calculate bearing/heading
   - Determine if aircraft is in overhead zone

3. Create filtering logic
   - Real-time position monitoring
   - Track aircraft entry/exit from overhead zone
   - Debounce logic (avoid flickering)

4. Add aircraft tracking
   - Maintain dictionary of tracked aircraft
   - Update positions continuously
   - Remove stale aircraft data

**Deliverables:**
- Geographic filtering module
- Configurable overhead zone parameters
- Aircraft tracking system

---

### Phase 4: Flight Information API Integration
**Duration: 2-3 days**

#### Tasks:
1. Research and select flight data API
   - **Option A: OpenSky Network** (Free, open)
     - Rate limits: reasonable for hobby projects
     - Data: flight routes, origins, destinations
   - **Option B: ADS-B Exchange** (Free API available)
     - Real-time data
     - Good coverage
   - **Option C: AviationStack** (Free tier available)
     - Commercial data
     - Limited requests on free tier

2. Implement API client
   - Register for API key (if required)
   - Create API request functions
   - Handle rate limiting
   - Implement caching (avoid redundant requests)
   - Error handling and retries

3. Map ICAO codes to flight details
   - Query by ICAO hex code or callsign
   - Extract:
     - Flight number
     - Origin airport/country
     - Destination airport/country
     - Airline information

4. Create country lookup database
   - Airport code to country mapping
   - Handle IATA/ICAO airport codes
   - Use local JSON database for offline lookup

**Deliverables:**
- Working API client module
- Flight information caching system
- Airport/country lookup database

---

### Phase 5: LED Display Controller
**Duration: 2-3 days**

#### Tasks:
1. Design display layout
   ```
   ┌─────────────────────────────────┐
   │ BA142                           │
   │ UK → USA                        │
   └─────────────────────────────────┘
   ```
   - Line 1: Flight number
   - Line 2: Origin country → Destination country
   - Consider scrolling for long text

2. Implement display rendering
   - Text rendering with fonts
   - Color coding:
     - Different colors for different flight types
     - Altitude-based colors
     - Direction indicators
   - Animations/transitions between flights

3. Handle multiple aircraft
   - Queue system for multiple overhead flights
   - Rotation timing (e.g., 5-10 seconds per flight)
   - Priority logic (closest first, lowest altitude, etc.)

4. Add status indicators
   - "Waiting for aircraft..." message
   - Signal strength indicator
   - Error states
   - Boot/startup animation

**Deliverables:**
- LED display controller module
- Flight information display layouts
- Multi-aircraft queue system

---

### Phase 6: Main Application Integration
**Duration: 2-3 days**

#### Tasks:
1. Create main application loop
   - Initialize all components
   - Continuous monitoring cycle
   - Graceful error handling
   - Logging system

2. Implement configuration system
   - Config file (YAML or JSON)
   - Configurable parameters:
     - Location coordinates
     - Overhead zone radius
     - Display timing
     - API credentials
     - Logging levels

3. Add logging and monitoring
   - Application logs
   - Aircraft detection logs
   - API request logs
   - Error tracking

4. Create systemd service
   - Auto-start on boot
   - Restart on failure
   - Service management commands

**Deliverables:**
- Integrated application
- Configuration file
- Systemd service setup
- Logging system

---

### Phase 7: Testing & Optimization
**Duration: 3-5 days**

#### Tasks:
1. Functional testing
   - Test with various aircraft types
   - Test edge cases (multiple simultaneous aircraft)
   - Test API failures/fallbacks
   - Test display with long text

2. Performance optimization
   - Reduce CPU usage
   - Optimize API calls (caching)
   - Memory leak detection
   - Reduce unnecessary updates

3. Improve accuracy
   - Fine-tune overhead zone parameters
   - Improve country/airport lookup
   - Handle missing data gracefully

4. User experience improvements
   - Better visual design
   - Smooth transitions
   - Informative error messages
   - Configuration validation

**Deliverables:**
- Tested and stable application
- Performance benchmarks
- Optimized configuration
- Bug fixes

---

### Phase 8: Documentation & Deployment
**Duration: 1-2 days**

#### Tasks:
1. Write documentation
   - README.md with setup instructions
   - Hardware assembly guide
   - Software installation guide
   - Configuration guide
   - Troubleshooting section

2. Create installation script
   - Automated dependency installation
   - Service setup
   - Configuration wizard

3. Final deployment
   - Clean installation on fresh Pi
   - Verify all components work
   - Document any issues

4. Future enhancements planning
   - Additional features to consider
   - Known limitations
   - Improvement ideas

**Deliverables:**
- Complete documentation
- Installation script
- Production-ready system

---

## Configuration Parameters

### Location Settings
```yaml
location:
  latitude: 51.5074   # Your location latitude
  longitude: -0.1278  # Your location longitude
  altitude: 50        # Meters above sea level
```

### Overhead Zone Settings
```yaml
overhead_zone:
  radius_km: 3.0           # Radius in kilometers
  min_altitude_m: 500      # Minimum altitude in meters
  max_altitude_m: 12000    # Maximum altitude in meters (optional)
```

### Display Settings
```yaml
display:
  led_rows: 32
  led_cols: 64
  led_chain: 1
  led_parallel: 1
  brightness: 80
  rotation_seconds: 8      # Time to show each flight
  font_path: "/path/to/font.bdf"
```

### API Settings
```yaml
api:
  provider: "opensky"      # opensky, adsbexchange, aviationstack
  api_key: "your_key"      # If required
  cache_duration: 300      # Cache flight data for 5 minutes
  request_timeout: 10      # Seconds
```

### ADS-B Settings
```yaml
adsb:
  data_source: "http://localhost:8080/data/aircraft.json"
  update_interval: 2       # Seconds between updates
```

---

## API Options Comparison

| API Provider | Cost | Rate Limit | Data Quality | Registration |
|--------------|------|------------|--------------|--------------|
| OpenSky Network | Free | 400/day (anonymous), 4000/day (registered) | Good | Optional |
| ADS-B Exchange | Free/Paid | Varies | Excellent | Required |
| AviationStack | Free tier available | 500/month (free) | Good | Required |
| FlightAware | Paid | Varies by plan | Excellent | Required |

**Recommendation:** Start with OpenSky Network (free, no key required for basic use)

---

## Directory Structure

```
flight-tracker-led/
├── README.md
├── PROJECT_PLAN.md
├── requirements.txt
├── config.yaml
├── install.sh
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── adsb_processor.py
│   ├── flight_api.py
│   ├── geo_filter.py
│   ├── led_display.py
│   └── utils.py
├── data/
│   ├── airports.json
│   └── countries.json
├── fonts/
│   └── (BDF font files)
├── logs/
│   └── (application logs)
├── tests/
│   ├── test_adsb_processor.py
│   ├── test_flight_api.py
│   ├── test_geo_filter.py
│   └── test_led_display.py
└── systemd/
    └── flight-tracker.service
```

---

## Estimated Costs

| Item | Estimated Cost (USD) |
|------|---------------------|
| Raspberry Pi 4 (4GB) | $55-75 |
| RTL-SDR Dongle | $25-40 |
| LED Matrix Panel (64x32) | $20-35 |
| RGB Matrix HAT | $15-25 |
| Power Supply (5V 4A) | $10-15 |
| ADS-B Antenna (optional upgrade) | $20-50 |
| SD Card (32GB+) | $8-15 |
| Miscellaneous (cables, case) | $10-20 |
| **Total** | **$163-275** |

---

## Timeline Summary

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Hardware Setup | 1-2 days | - |
| Phase 2: ADS-B Reception | 2-3 days | Phase 1 |
| Phase 3: Geographic Filtering | 1-2 days | Phase 2 |
| Phase 4: API Integration | 2-3 days | Phase 2 |
| Phase 5: LED Display | 2-3 days | Phase 1 |
| Phase 6: Integration | 2-3 days | Phases 3, 4, 5 |
| Phase 7: Testing | 3-5 days | Phase 6 |
| Phase 8: Documentation | 1-2 days | Phase 7 |
| **Total** | **14-23 days** | |

*Note: Timeline assumes working a few hours per day. Full-time work could reduce this significantly.*

---

## Risk Assessment & Mitigation

### Technical Risks

1. **Poor ADS-B Reception**
   - **Risk:** Location has limited aircraft visibility
   - **Mitigation:** Upgrade antenna, relocate antenna to higher position, use external antenna with longer cable

2. **API Rate Limiting**
   - **Risk:** Exceeding free tier limits
   - **Mitigation:** Implement aggressive caching, use multiple API providers as fallback, cache flight routes for common flights

3. **Power Supply Issues**
   - **Risk:** Insufficient power for LED display
   - **Mitigation:** Use adequate power supply (5V 4A minimum), separate power for Pi and LED panel

4. **Performance Bottlenecks**
   - **Risk:** Raspberry Pi can't handle processing load
   - **Mitigation:** Optimize code, reduce update frequency, use lighter display rendering

### Operational Risks

1. **Internet Dependency**
   - **Risk:** Flight info requires internet connectivity
   - **Mitigation:** Implement offline mode (show only ICAO/callsign), cache historical data

2. **False Positives**
   - **Risk:** Displaying incorrect flight information
   - **Mitigation:** Data validation, display confidence levels, allow manual verification

---

## Future Enhancements

### Potential Features
- Web interface for remote monitoring and configuration
- Historical flight logging and statistics
- Weather information overlay
- Aircraft type/model display
- Airline logos
- Sound notifications for interesting aircraft
- Integration with FlightRadar24 for photos
- Multiple display modes (detailed, compact, artistic)
- Mobile app for remote viewing
- Community features (share interesting flights)

### Hardware Upgrades
- Larger LED display (128x64 or multiple panels)
- Better antenna with amplifier (increases range to 200+ miles)
- GPS module for portable installation
- Outdoor enclosure for weather protection
- Solar power for off-grid operation

---

## Resources & References

### Documentation
- [ADS-B on Raspberry Pi - FlightAware](https://flightaware.com/adsb/piaware/build)
- [rpi-rgb-led-matrix GitHub](https://github.com/hzeller/rpi-rgb-led-matrix)
- [OpenSky Network API](https://opensky-network.org/apidoc/)
- [RTL-SDR Quick Start Guide](https://www.rtl-sdr.com/rtl-sdr-quick-start-guide/)

### Communities
- r/RTLSDR (Reddit)
- r/adsb (Reddit)
- FlightAware Forums
- Raspberry Pi Forums

### Tools
- [VirtualRadar](http://www.virtualradarserver.co.uk/) - Web-based aircraft tracking
- [tar1090](https://github.com/wiedehopf/tar1090) - Improved web interface for ADS-B data
- [Plane Finder](https://planefinder.net/) - Additional tracking service

---

## Success Criteria

The project will be considered successful when:

1. ✅ LED display shows real-time flight information
2. ✅ System accurately detects overhead aircraft
3. ✅ Flight number and route information displayed correctly
4. ✅ System runs reliably 24/7
5. ✅ At least 80% of overhead flights correctly identified
6. ✅ Display updates within 5 seconds of aircraft entering overhead zone
7. ✅ Graceful handling of edge cases and errors
8. ✅ Clear documentation for reproduction

---

## Getting Started

### Next Steps (In Order)
1. ✅ Review and approve this project plan
2. 📦 Order hardware components
3. 🔧 Set up Raspberry Pi with OS
4. 📡 Install and test RTL-SDR
5. 💡 Test LED matrix display
6. 💻 Begin software development (Phase 2)

---

*Document Version: 1.0*
*Last Updated: 2025-10-16*
*Project Start Date: TBD*
