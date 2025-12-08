# 🎉 AeroGuardians ESP32 Integration - Complete!

## ✅ What Has Been Added

### 1. **Flask Backend Updates** (`app.py`)
- ✅ New API endpoint: `POST /api/data` - Receives ESP32 sensor data
- ✅ New API endpoint: `GET /api/sensor-data` - Returns all sensor history
- ✅ New API endpoint: `GET /api/latest-sensor` - Returns latest reading
- ✅ Smart risk classification for sensor data
- ✅ Automatic CSV logging to `data/sensor_log.csv`
- ✅ Multi-parameter risk analysis (dust, temp, TVOC, eCO2)

### 2. **Sensor Dashboard** (`sensor_dashboard.py`)
- ✅ Real-time ESP32 data visualization
- ✅ 4 interactive graph types:
  - All Sensors (normalized view)
  - Dust Analysis with anomaly detection
  - Multi-parameter comparison
  - Correlation heatmap
- ✅ AI-powered insights:
  - Trend detection
  - Anomaly detection (Isolation Forest)
  - Correlation analysis
  - Automated recommendations
- ✅ Live metrics with delta indicators
- ✅ Risk classification (Low/Moderate/High/Critical)
- ✅ Historical statistics
- ✅ Auto-refresh option
- ✅ Responsive design

### 3. **ESP32 Arduino Code** (`esp32_sensor_code.ino`)
- ✅ WiFi connection with retry logic
- ✅ HTTP POST with JSON payload
- ✅ Error handling and retry mechanism
- ✅ OLED display feedback
- ✅ Audio alerts (buzzer)
- ✅ Detailed serial debugging
- ✅ Success/error indicators
- ✅ 5-second data transmission interval

### 4. **Helper Scripts**
- ✅ `start_backend.bat` - Easy Flask startup
- ✅ `start_dashboard.bat` - Easy dashboard launch
- ✅ `test_api.py` - API testing tool
- ✅ `SETUP_INSTRUCTIONS.md` - Complete setup guide

### 5. **Dependencies** (`requirements.txt`)
- ✅ Added: pandas, requests, streamlit, plotly, numpy, scikit-learn

---

## 🚀 How to Use

### Quick Start (3 Steps)

**Step 1: Start Backend**
```bash
# Option A: Use batch file (double-click)
start_backend.bat

# Option B: Manual
python app.py
```

**Step 2: Start Dashboard**
```bash
# Option A: Use batch file (double-click)
start_dashboard.bat

# Option B: Manual
streamlit run sensor_dashboard.py
```

**Step 3: Configure & Upload ESP32 Code**
1. Open `esp32_sensor_code.ino` in Arduino IDE
2. Change WiFi credentials:
   ```cpp
   #define STASSID "YourWiFiName"
   #define STAPSK  "YourWiFiPassword"
   ```
3. Get your computer's IP:
   - Windows: Run `ipconfig` in terminal
   - Look for "IPv4 Address" (e.g., 192.168.1.100)
4. Update server address:
   ```cpp
   const char* serverName = "http://192.168.1.100:5000/api/data";
   ```
5. Upload to ESP32
6. Open Serial Monitor (115200 baud) to see status

---

## 📊 Dashboard Features Explained

### Real-Time Metrics
- **Dust**: Particulate matter concentration (µg/m³)
- **Temperature**: Ambient temperature (°C)
- **TVOC**: Total Volatile Organic Compounds (ppb)
- **eCO2**: Equivalent CO2 levels (ppm)

### Graph Types

**1. All Sensors (Normalized)**
- Shows all 4 sensors on same scale (0-100)
- Easy comparison of relative changes
- Identifies which sensor is most volatile

**2. Dust Analysis**
- Anomaly detection with red X markers
- Warning threshold at 500 µg/m³ (orange line)
- Critical threshold at 1000 µg/m³ (red line)
- Statistics: average, max, std deviation

**3. Multi-Parameter**
- Three Y-axes for different units
- Shows relationships between temp, TVOC, eCO2
- Identify if temperature affects air quality

**4. Correlation Matrix**
- Heatmap showing how sensors relate
- Red = positive correlation (rise together)
- Blue = negative correlation (inverse)
- Helps understand sensor dependencies

### AI Insights

**Trend Detection**
- Compares last 10 readings vs overall average
- Identifies gradual changes
- Shows 📈 or 📉 for each sensor

**Anomaly Detection**
- Uses Isolation Forest ML algorithm
- Flags unusual readings that deviate from pattern
- Helps identify sensor issues or sudden events

**Recommendations**
- Context-aware suggestions based on current readings
- Examples:
  - "Activate air filtration" when dust > 500
  - "Increase ventilation" when TVOC > 250
  - "Check cooling systems" when temp > 35

---

## 🧪 Testing Without ESP32

Use the test script to simulate ESP32 data:

```bash
python test_api.py
```

Choose option 2 and send 20-30 readings to see:
- Graphs populate with data
- AI insights appear
- Trends become visible
- Correlations emerge

---

## 📈 Data Flow

```
ESP32 Sensors
    ↓
WiFi Network
    ↓
Flask API (port 5000)
    ↓
data/sensor_log.csv
    ↓
Streamlit Dashboard (port 8501)
    ↓
Your Browser (with graphs & AI)
```

---

## 🔍 Troubleshooting Guide

### ESP32 Shows "WiFi FAIL"
- ✅ Double-check WiFi name and password
- ✅ Ensure WiFi is 2.4GHz (not 5GHz)
- ✅ Move ESP32 closer to router

### ESP32 Shows "SEND FAIL"
- ✅ Verify computer IP hasn't changed
- ✅ Check Flask is running (`python app.py`)
- ✅ Temporarily disable Windows Firewall
- ✅ Ensure both on same network

### Dashboard Shows "Cannot connect to Flask backend"
- ✅ Start Flask: `python app.py`
- ✅ Check no other app using port 5000
- ✅ Try: `netstat -ano | findstr :5000`

### No Data Appearing
- ✅ Check ESP32 Serial Monitor for "SUCCESS"
- ✅ Look for `data/sensor_log.csv` file
- ✅ Verify Flask terminal shows POST requests
- ✅ Click "Refresh Data" on dashboard

### Graphs Not Updating
- ✅ Enable "Auto-refresh" in sidebar
- ✅ Manually click "Refresh Data"
- ✅ Check if new data in CSV file

---

## 📁 File Overview

| File | Purpose |
|------|---------|
| `app.py` | Flask backend with API endpoints |
| `sensor_dashboard.py` | Main dashboard with graphs & AI |
| `dashboard.py` | Original API-based dashboard |
| `esp32_sensor_code.ino` | Arduino code for ESP32 |
| `test_api.py` | API testing tool |
| `start_backend.bat` | Quick start Flask |
| `start_dashboard.bat` | Quick start dashboard |
| `SETUP_INSTRUCTIONS.md` | Detailed setup guide |
| `data/sensor_log.csv` | ESP32 sensor data storage |
| `data/realtime_log.csv` | Original API data storage |

---

## 🎯 Sensor Thresholds Reference

| Parameter | Good | Moderate | High | Critical |
|-----------|------|----------|------|----------|
| **Dust** (µg/m³) | 0-200 | 200-500 | 500-1000 | >1000 |
| **Temp** (°C) | <30 | 30-35 | 35-40 | >40 |
| **TVOC** (ppb) | 0-100 | 100-250 | 250-500 | >500 |
| **eCO2** (ppm) | <600 | 600-800 | 800-1000 | >1000 |

---

## 💡 Pro Tips

1. **Collect Baseline Data**
   - Run for 24-48 hours to establish normal patterns
   - AI insights become more accurate with more data

2. **Use Auto-Refresh**
   - Enable in sidebar for live monitoring
   - Refreshes every 10 seconds

3. **Monitor Correlations**
   - High dust + high TVOC = possible combustion
   - High temp + high TVOC = chemical vaporization
   - Use insights for root cause analysis

4. **Check Serial Monitor**
   - Best way to debug ESP32 issues
   - Shows WiFi status, POST results, sensor readings

5. **Adjust Transmission Interval**
   - Default: 5 seconds
   - Increase to 10-30s for long-term monitoring
   - Decrease to 2s for rapid response testing

---

## 🌟 What Makes This Special

✨ **Real Hardware Integration** - Not simulated, actual ESP32 sensors
✨ **AI-Powered Analysis** - Machine learning anomaly detection
✨ **Multi-Sensor Correlation** - Understand sensor relationships
✨ **Production Ready** - Error handling, retry logic, robust code
✨ **Beautiful UI** - Modern Streamlit dashboard with Plotly graphs
✨ **Easy Setup** - Batch files and detailed instructions
✨ **Comprehensive** - Testing tools, documentation, everything included

---

## 🎓 Understanding the AI

### Isolation Forest Algorithm
- Unsupervised ML technique
- Identifies outliers by isolating observations
- Works by randomly selecting features and split values
- Anomalies are easier to isolate (fewer splits needed)
- Perfect for sensor data where normal = clustered, abnormal = scattered

### Why It's Effective Here
- No training data needed
- Adapts to your environment
- Catches sensor failures
- Detects sudden environmental changes
- Low computational cost

---

## 📞 Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Test API: `python test_api.py`
3. ✅ Configure ESP32 with your WiFi
4. ✅ Upload code to ESP32
5. ✅ Start backend: `start_backend.bat`
6. ✅ Start dashboard: `start_dashboard.bat`
7. ✅ Watch real-time data flow!

---

## 🚀 Ready to Deploy!

Your AeroGuardians system is now complete with:
- ✅ ESP32 hardware integration
- ✅ Real-time data collection
- ✅ Advanced visualization
- ✅ AI-powered insights
- ✅ Risk classification
- ✅ Historical analysis

**Everything is set up and ready to use!** 🎉

---

Built with ❤️ for environmental monitoring
