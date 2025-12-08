# AeroGuardians - ESP32 Sensor Integration Setup Guide

## 🎯 Overview
This project integrates ESP32 hardware sensors with a Flask backend and Streamlit dashboard for real-time environmental monitoring with AI-powered analysis.

## 📋 What's New
- ✅ ESP32 sensor data reception via REST API
- ✅ Real-time data logging to CSV
- ✅ Interactive dashboard with graphs
- ✅ AI-powered anomaly detection
- ✅ Correlation analysis
- ✅ Smart risk classification
- ✅ Historical trend analysis

## 🚀 Quick Start Guide

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Find Your Computer's IP Address
**Windows:**
```bash
ipconfig
```
Look for "IPv4 Address" (e.g., `192.168.1.100`)

**Mac/Linux:**
```bash
ifconfig
```

### Step 3: Configure ESP32 Code
1. Open `esp32_sensor_code.ino` in Arduino IDE
2. Update these lines:
   ```cpp
   #define STASSID "YOUR_WIFI_NAME"        // Your WiFi name
   #define STAPSK  "YOUR_WIFI_PASSWORD"    // Your WiFi password
   const char* serverName = "http://192.168.1.100:5000/api/data";  // Your computer's IP
   ```
3. Upload to ESP32

### Step 4: Start the Flask Backend
```bash
python app.py
```
The server will run on `http://127.0.0.1:5000`

### Step 5: Launch the Sensor Dashboard
Open a new terminal:
```bash
streamlit run sensor_dashboard.py
```
The dashboard will open in your browser at `http://localhost:8501`

### Step 6: Power On ESP32
- ESP32 will connect to WiFi
- Start sending sensor data every 5 seconds
- Data appears on dashboard in real-time

## 📊 Dashboard Features

### 1. **Current Readings**
- Live metrics for Dust, Temperature, TVOC, and eCO2
- Delta indicators showing changes from baseline

### 2. **Risk Assessment**
- Real-time risk classification (Low/Moderate/High/Critical)
- Multi-parameter alert system
- Color-coded warnings

### 3. **Time Series Analysis**
Four interactive tabs:
- **All Sensors**: Normalized view of all parameters
- **Dust Analysis**: Anomaly detection with threshold markers
- **Temperature & Air Quality**: Multi-axis comparison
- **Correlations**: Heatmap showing sensor relationships

### 4. **AI-Powered Insights**
- Trend detection (upward/downward patterns)
- Anomaly detection using Isolation Forest algorithm
- Correlation analysis between parameters
- Automated health recommendations

### 5. **Historical Statistics**
- Average, max, min values
- Trend indicators
- Standard deviation analysis

## 📡 API Endpoints

### Receive ESP32 Data
```
POST /api/data
Content-Type: application/json

{
  "dust": 120.5,
  "temp": 25.3,
  "tvoc": 45,
  "eco2": 420
}
```

### Get All Sensor Data
```
GET /api/sensor-data
Returns: Last 100 readings
```

### Get Latest Reading
```
GET /api/latest-sensor
Returns: Most recent sensor reading
```

## 🔧 Troubleshooting

### ESP32 Cannot Connect to WiFi
1. Verify WiFi credentials are correct
2. Make sure ESP32 is within WiFi range
3. Check WiFi is 2.4GHz (ESP32 doesn't support 5GHz)

### "Cannot connect to Flask backend" Error
1. Make sure Flask app is running (`python app.py`)
2. Check firewall isn't blocking port 5000
3. Verify IP address in ESP32 code matches your computer

### No Data on Dashboard
1. Check ESP32 serial monitor for "SUCCESS" messages
2. Verify Flask shows incoming POST requests
3. Look for `data/sensor_log.csv` file creation

### Data Sending Errors
1. Check computer and ESP32 are on same WiFi network
2. Temporarily disable firewall to test
3. Verify IP address hasn't changed (use static IP if needed)

## 📁 File Structure
```
aero-guardians-master/
├── app.py                    # Flask backend with API endpoints
├── dashboard.py              # Original dashboard (API data)
├── sensor_dashboard.py       # NEW: ESP32 sensor dashboard
├── esp32_sensor_code.ino     # NEW: Arduino code for ESP32
├── requirements.txt          # Python dependencies
├── data/
│   ├── realtime_log.csv     # API air quality data
│   └── sensor_log.csv       # NEW: ESP32 sensor data
└── SETUP_INSTRUCTIONS.md    # This file
```

## 🎨 Dashboard Controls

### Sidebar Options
- **Auto-refresh**: Enable 10-second automatic refresh
- **Show Raw Data**: Display complete data table
- **Data points to display**: Adjust graph resolution (10-100 points)

### Manual Controls
- **Refresh Data**: Manual update button
- All graphs are interactive (zoom, pan, hover for details)

## 📈 Understanding the Graphs

### Normalized Sensor Readings
- All sensors scaled to 0-100 for comparison
- Helps identify overall trends and patterns

### Dust Analysis
- **Blue line**: Normal readings
- **Red X**: Detected anomalies
- **Orange dashed**: Warning threshold (500 µg/m³)
- **Red dashed**: Critical threshold (1000 µg/m³)

### Multi-Parameter Analysis
- Three Y-axes for different parameters
- Shows relationships between temp, TVOC, and eCO2

### Correlation Matrix
- **Red**: Positive correlation (sensors move together)
- **Blue**: Negative correlation (sensors move opposite)
- **White**: No correlation

## 🤖 AI Analysis Features

### Anomaly Detection
Uses Isolation Forest algorithm to detect unusual readings that may indicate:
- Sensor malfunction
- Sudden environmental changes
- Data transmission errors

### Trend Analysis
Compares recent readings (last 10) vs overall average to detect:
- Gradual deterioration
- Improvement trends
- Cyclic patterns

### Recommendations
AI generates specific actions based on current readings:
- "Activate air filtration" when dust is high
- "Increase ventilation" when TVOC is elevated
- "Check cooling systems" when temperature rises

## 🔐 Security Notes
- API endpoint is open (no authentication)
- For production use, add API keys or authentication
- Run Flask with proper WSGI server (not debug mode)

## 🎯 Sensor Thresholds

### Dust (µg/m³)
- **Good**: 0-200
- **Moderate**: 200-500
- **High**: 500-1000
- **Critical**: >1000

### Temperature (°C)
- **Good**: <30
- **Moderate**: 30-35
- **High**: 35-40
- **Critical**: >40

### TVOC (ppb)
- **Good**: 0-100
- **Moderate**: 100-250
- **High**: 250-500
- **Critical**: >500

### eCO2 (ppm)
- **Good**: <600
- **Moderate**: 600-800
- **High**: 800-1000
- **Critical**: >1000

## 💡 Tips for Best Results

1. **Stable WiFi**: Ensure ESP32 has strong WiFi signal
2. **Regular Calibration**: Restart ESP32 daily for sensor calibration
3. **Baseline Data**: Collect 24-48 hours of data for accurate trends
4. **Sensor Placement**: Position sensors away from direct air flow
5. **Monitor Temperature**: High temps can affect sensor accuracy

## 🆘 Need Help?

### Check Logs
**Flask Backend:**
```bash
python app.py
# Watch for POST requests from ESP32
```

**ESP32 Serial Monitor:**
```
Arduino IDE > Tools > Serial Monitor (115200 baud)
# Look for "SUCCESS!" messages
```

### Test API Manually
Use browser or Postman:
```
http://127.0.0.1:5000/api/latest-sensor
```

## 🎉 Success Indicators

✅ ESP32 Serial Monitor shows "✓ SUCCESS! Response Code: 200"
✅ Flask terminal shows "POST /api/data 200"
✅ Dashboard displays real-time data
✅ Graphs update with new readings
✅ AI insights appear after 10+ readings

---

**Built with ❤️ using ESP32, Flask, Streamlit, and AI**
