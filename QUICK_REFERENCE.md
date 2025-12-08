# ⚡ Quick Reference Card

## 🚀 Start Commands

```bash
# Terminal 1 - Backend
python app.py
# OR double-click: start_backend.bat

# Terminal 2 - Dashboard  
streamlit run sensor_dashboard.py
# OR double-click: start_dashboard.bat

# Optional - Test API
python test_api.py
```

## 🔗 URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Flask Backend | http://127.0.0.1:5000 | API server |
| Sensor Dashboard | http://localhost:8501 | ESP32 data visualization |
| Original Dashboard | http://localhost:8501 | API air quality data |

## 📡 API Endpoints

```bash
# Receive ESP32 data
POST http://127.0.0.1:5000/api/data
Content-Type: application/json
Body: {"dust": 120.5, "temp": 25.3, "tvoc": 45, "eco2": 420}

# Get all sensor data
GET http://127.0.0.1:5000/api/sensor-data

# Get latest reading
GET http://127.0.0.1:5000/api/latest-sensor

# Get API air quality
GET http://127.0.0.1:5000/data
```

## 🔧 ESP32 Configuration

```cpp
// 1. WiFi Settings
#define STASSID "YourWiFiName"
#define STAPSK  "YourPassword"

// 2. Server Address (use YOUR computer's IP)
const char* serverName = "http://192.168.1.100:5000/api/data";

// 3. Transmission Interval (milliseconds)
unsigned long sampletime_ms = 5000;  // 5 seconds
```

## 🖥️ Get Your Computer's IP

```bash
# Windows
ipconfig
# Look for: IPv4 Address . . . : 192.168.1.100

# Mac/Linux
ifconfig
# or
ip addr show
```

## 📊 Dashboard Shortcuts

| Action | How To |
|--------|--------|
| Refresh manually | Click "🔄 Refresh Data" |
| Auto-refresh | Enable in sidebar (10s) |
| Adjust data points | Sidebar slider (10-100) |
| View raw data | Enable "Show Raw Data" |
| Switch graphs | Click tabs (All/Dust/Multi/Corr) |

## 🎯 Risk Levels

| Level | Dust | Temp | TVOC | eCO2 |
|-------|------|------|------|------|
| **Good** | <200 | <30 | <100 | <600 |
| **Moderate** | 200-500 | 30-35 | 100-250 | 600-800 |
| **High** | 500-1000 | 35-40 | 250-500 | 800-1000 |
| **Critical** | >1000 | >40 | >500 | >1000 |

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| WiFi connection fails | Check SSID/password, use 2.4GHz |
| POST fails | Verify IP address, check firewall |
| No data on dashboard | Ensure Flask is running |
| Import errors | Run: `pip install -r requirements.txt` |
| Port already in use | Close other Flask apps or change port |

## 📁 Important Files

```
esp32_sensor_code.ino      ← Upload to ESP32
app.py                     ← Flask backend
sensor_dashboard.py        ← Main dashboard
test_api.py                ← Test without hardware
data/sensor_log.csv        ← Your sensor data
```

## 🎨 Color Codes (OLED)

```
ESP32 Display:
D: 120     ← Dust (µg/m³)
T: 25      ← Temperature (°C)
V: 45      ← TVOC (ppb)
C: 420     ← eCO2 (ppm)

SENDING DATA...  ← Transmission status
SENT OK!         ← Success
SEND FAIL        ← Error
```

## 🔊 Buzzer Sounds

| Pattern | Meaning |
|---------|---------|
| High-Low chime | Setup complete / Alert triggered |
| Two quick beeps | Error (WiFi/POST failed) |
| Quick beep-beep | Success (data sent) |

## 📈 Serial Monitor Output

```
Expected output (115200 baud):
========================================
Current Readings:
  Dust: 120.5 µg/m³
  Temp: 25.3 °C
  TVOC: 45 ppb
  eCO2: 420 ppm
--- Sending to Server ---
URL: http://192.168.1.100:5000/api/data
Payload: {"dust":120.5,"temp":25.3,"tvoc":45,"eco2":420}
✓ SUCCESS! Response Code: 200
Response: {"status":"success",...}
========================================
```

## 🧪 Test API Without Hardware

```bash
python test_api.py

Choose:
1 = Single test POST
2 = Multiple readings (populate dashboard)  ← Recommended
3 = Test GET endpoints
4 = Run all tests
```

## 💾 Data Storage

```
data/sensor_log.csv format:
timestamp, dust, temp, tvoc, eco2, risk, alert
2025-12-08 14:30:45, 120.5, 25.3, 45, 420, Low, ✅ Air quality is good
```

## 🔑 Key Metrics Explained

| Metric | Full Name | Unit | What It Measures |
|--------|-----------|------|------------------|
| **Dust** | Particulate Matter | µg/m³ | Airborne particles |
| **Temp** | Temperature | °C | Ambient temperature |
| **TVOC** | Total Volatile Organic Compounds | ppb | Chemical vapors |
| **eCO2** | Equivalent CO2 | ppm | Air freshness |

## ⚙️ Advanced Settings

```python
# In sensor_dashboard.py
data_points = 50              # Readings to display (10-100)
auto_refresh = True           # Auto-update every 10s

# In esp32_sensor_code.ino
sampletime_ms = 5000         # 5s between readings
THRESH_DUST = 1000           # Alert threshold
```

## 🌐 Network Requirements

- ESP32 and computer on **same WiFi network**
- WiFi must be **2.4GHz** (ESP32 limitation)
- Computer firewall allows **port 5000**
- Static IP recommended for stability

## 📞 Emergency Commands

```bash
# Kill process on port 5000 (if stuck)
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Check if Flask is running
curl http://127.0.0.1:5000

# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## 🎓 Dashboard Tabs Explained

| Tab | What It Shows | Best For |
|-----|---------------|----------|
| **All Sensors** | Normalized 0-100 scale | Overall comparison |
| **Dust Analysis** | Anomalies + thresholds | Safety monitoring |
| **Multi-Parameter** | 3 sensors, 3 axes | Relationships |
| **Correlations** | Heatmap matrix | Understanding dependencies |

## 🤖 AI Features

```
✓ Anomaly Detection    → Flags unusual readings
✓ Trend Analysis       → Shows if rising/falling
✓ Correlation Matrix   → Finds sensor relationships
✓ Smart Alerts         → Context-aware recommendations
```

## 📌 Remember

1. ✅ Flask MUST be running before dashboard
2. ✅ ESP32 and PC must be on same network
3. ✅ Update IP address in ESP32 code
4. ✅ Check Serial Monitor (115200 baud)
5. ✅ Wait 10-20 readings for AI insights

---

**Need detailed help?** See `SETUP_INSTRUCTIONS.md`
**Architecture details?** See `ARCHITECTURE.md`
**Complete overview?** See `PROJECT_SUMMARY.md`
