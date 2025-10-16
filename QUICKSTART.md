# Quick Start Guide - Flight Tracker Dashboard

## For Footscray, Melbourne, Victoria

Your flight tracker is configured and ready to monitor aircraft overhead in Footscray, Melbourne!

## 🚀 Getting Started (5 Minutes)

### 1. Test the Dashboard (Without Hardware)

You can test the dashboard right now on your Windows PC without any ADS-B hardware:

```bash
# Navigate to project directory
cd "C:\Users\diamo\OneDrive\Documents\02_Work_Projects\05_Personal_Projects\Flight_Location_Detector"

# Install Flask if not already installed
pip install flask flask-cors

# Start the dashboard
python src/dashboard.py
```

Open your browser and go to:
```
http://localhost:5000
```

**Note**: Without ADS-B data, you won't see aircraft yet, but you can verify the dashboard works!

### 2. Test Configuration

Your location is already configured for:
- **Location**: Footscray, Melbourne, Victoria
- **Coordinates**: -37.7964°S, 144.9008°E
- **Detection Radius**: 3.0 km
- **Altitude Range**: 500m - 12,000m

### 3. Run All Tests

Verify everything works:

```bash
python -m pytest tests/ -v
```

You should see **76 tests passing** ✅

## 📊 Dashboard Features

Once you access the dashboard, you'll see:

1. **System Status**
   - Uptime and last update time
   - Detection radius (3 km)
   - Altitude range

2. **Statistics**
   - Current aircraft detected
   - Aircraft overhead count
   - Total aircraft seen
   - API call counter

3. **Aircraft Overhead** (Real-time)
   - Flight callsign/number
   - Origin → Destination countries
   - Distance from your location
   - Altitude, speed, heading

4. **All Detected Aircraft**
   - Complete list with details
   - Refresh button for manual updates

5. **Recent Overhead Flights**
   - History of flights that passed over
   - Time and route information

6. **Configuration**
   - Current system settings

## 🛠️ For Production (Raspberry Pi)

When you're ready to deploy on Raspberry Pi with real ADS-B hardware:

### Hardware Needed:
1. Raspberry Pi (any model 3/4/5)
2. RTL-SDR dongle (for ADS-B reception)
3. 1090 MHz antenna
4. Optional: RGB LED Matrix panel

### Installation:

```bash
# 1. Copy project to Raspberry Pi
scp -r Flight_Location_Detector pi@YOUR_PI_IP:/home/pi/

# 2. SSH into Raspberry Pi
ssh pi@YOUR_PI_IP

# 3. Run installation script
cd Flight_Location_Detector
bash install.sh
```

The installer will:
- Install all dependencies
- Configure ADS-B decoder (readsb)
- Set up the dashboard
- Configure systemd services
- Use your Footscray location

### After Installation:

```bash
# Start the dashboard
python3 src/dashboard.py

# Access from any device on your network
http://RASPBERRY_PI_IP:5000
```

## 📱 Access from Other Devices

Once running, access the dashboard from:

- **Same computer**: `http://localhost:5000`
- **Phone/Tablet (same WiFi)**: `http://YOUR_PI_IP:5000`
- **Find Pi IP**: `hostname -I` on Raspberry Pi

## 🎯 What to Expect

### Melbourne/Footscray Area

Melbourne Airport (MEL/YMML) is about 15km north of Footscray, so you should see:

- **Commercial flights**: Landing/departing Melbourne Airport
- **International flights**: Long-haul aircraft passing overhead
- **Domestic flights**: Sydney, Brisbane, Adelaide routes
- **General aviation**: Light aircraft from nearby airfields

### Typical Detection:
- **Radius**: 3 km from Footscray center
- **Altitude**: 500m - 12,000m (1,640 ft - 39,370 ft)
- **Aircraft per day**: Varies, but Melbourne is busy! Expect dozens daily

### Peak Times:
- **Morning**: 6 AM - 9 AM (arrivals)
- **Evening**: 5 PM - 8 PM (departures)
- **International**: Red-eye arrivals early morning

## 🔧 Troubleshooting

### Dashboard shows "No aircraft"

**Without Hardware (Testing on Windows)**:
- Expected! You need ADS-B receiver for real data
- Dashboard shows "Waiting for aircraft..."

**With Hardware (On Raspberry Pi)**:
1. Check ADS-B decoder:
   ```bash
   systemctl status readsb
   curl http://localhost:8080/data/aircraft.json
   ```

2. Check antenna connection and placement
   - Higher is better (window, roof)
   - Clear line of sight to sky

3. Verify location in config.yaml is correct

### Can't access dashboard from phone

1. Ensure phone and Pi are on same WiFi network
2. Find Pi's IP address: `hostname -I`
3. Check firewall isn't blocking port 5000

### Dashboard is slow/laggy

1. Reduce update frequency in config.yaml:
   ```yaml
   adsb:
     update_interval: 5  # Increase from 2 to 5 seconds
   ```

2. Increase browser refresh interval in `dashboard/static/js/dashboard.js`

## 📚 Next Steps

1. **Customize Settings**
   - Edit `config.yaml` to adjust detection radius
   - Change altitude limits
   - Configure API provider

2. **Add LED Display**
   - Follow main README.md for LED setup
   - Shows flight info on physical display

3. **Run as Service**
   - See DASHBOARD_README.md for systemd setup
   - Auto-start on boot

4. **Explore APIs**
   - OpenSky Network (default, free)
   - ADS-B Exchange (more data)
   - FlightAware (commercial)

## 📖 Documentation

- **README.md** - Full project documentation
- **DASHBOARD_README.md** - Complete dashboard guide
- **PROJECT_PLAN.md** - Detailed implementation plan
- **IMPLEMENTATION_SUMMARY.md** - Technical details

## 🎉 You're Ready!

Your flight tracker is configured for Footscray, Melbourne and ready to use!

**Current Status:**
- ✅ Location: Footscray, Melbourne, VIC
- ✅ Dashboard: Installed and tested
- ✅ Tests: 76 tests passing
- ✅ Configuration: Ready for deployment

### Quick Commands:

```bash
# Test everything
python -m pytest tests/ -v

# Start dashboard
python src/dashboard.py

# Start main app (when hardware ready)
python src/main.py
```

---

**Happy Flight Tracking! ✈️**

*Watch the skies over Footscray, Melbourne!*
