# 🛰️ AirSight Systems - Industrial Air Quality Monitoring Platform

> Professional-grade IoT platform for real-time industrial emissions monitoring with ESP32 sensors, AI-powered diagnostics, and enterprise-level PDF reporting

![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Platform](https://img.shields.io/badge/Platform-ESP32-orange)
![AI](https://img.shields.io/badge/AI-Powered-purple)
![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-red)

## ✨ Features

### 🔬 Hardware Integration
- **ESP32 WiFi** - Wireless sensor data transmission (5-second intervals)
- **GP2Y1014** - PM2.5 dust/particulate matter sensor (µg/m³)
- **SGP30** - TVOC & eCO2 air quality sensor (ppb/ppm)
- **MCP9808** - High-precision temperature sensor (±0.25°C)
- **SSD1306 OLED** - Real-time local readings display
- **Buzzer Alerts** - Audio warnings for threshold violations

### 📊 AirSight Mission Control Dashboard
- **SpaceX/Bloomberg Aesthetic** - Professional industrial dark theme with glassmorphism
- **Real-time KPI Cards** - 4 dynamic metrics with color-coded safety status
- **Live Emission Trends** - Dual-axis charts (PM2.5 + TVOC)
- **Thermal Monitoring** - Temperature area charts with warning thresholds
- **Regulatory Compliance Gauge** - AQI scoring (0-100 scale)
- **Auto-refresh** - 2-second update intervals
- **Responsive Design** - Works on desktop, tablet, mobile

### 🤖 AI-Powered Diagnostics
- **Real-time Analysis** - Context-aware diagnostic messages
- **Smart Recommendations** - Action items based on current readings
- **Risk Classification** - 4-level safety assessment (Safe/Moderate/Warning/Hazard)
- **Compliance Alerts** - Regulatory threshold violation warnings

### 📄 Professional PDF Report Generation
- **Time Range Selection** - 30 min, 1 hour, 6 hours, 12 hours, 24 hours
- **High-Quality Charts** - Embedded visualizations (emissions trends, thermal conditions)
- **Statistical Summaries** - Average, max, min for all parameters
- **Comprehensive AI Analysis** - Detailed recommendations per parameter
- **Executive Summary** - Overall system health assessment
- **Best Practices** - Air quality improvement strategies
- **Professional Formatting** - Enterprise-ready reports for compliance

### 🎯 Complete Production Solution
- ✅ Flask REST API backend with CORS support
- ✅ CSV data persistence with timestamps
- ✅ Error handling & connection retry logic
- ✅ Easy setup with batch files (Windows)
- ✅ Comprehensive documentation
- ✅ API testing tools included
- ✅ Network IP configuration helpers
- ✅ Firewall troubleshooting guides

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** 
- **ESP32 board** with sensors (GP2Y1014, SGP30, MCP9808)
- **Arduino IDE** 1.8.x or 2.x
- **WiFi network** (2.4GHz recommended)

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/yourusername/aero-guardians.git
cd aero-guardians
```

**2. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**3. Configure ESP32:**
- Open `esp32_sensor_code.ino` in Arduino IDE
- Update WiFi credentials:
  ```cpp
  const char* ssid = "YOUR_WIFI_SSID";
  const char* password = "YOUR_WIFI_PASSWORD";
  ```
- Find your computer's IP address and update:
  ```cpp
  const char* serverIP = "YOUR_COMPUTER_IP";  // e.g., "192.168.1.100"
  ```
- Upload to ESP32

**4. Start the backend:**
```bash
# Windows
start_backend.bat

# Linux/Mac
python app.py
```

**5. Start the dashboard:**
```bash
# Windows
start_dashboard.bat

# Linux/Mac
streamlit run airsight_dashboard.py --server.port 8505
```

**6. Access the dashboard:**
- Local: `http://localhost:8505`
- Network: `http://YOUR_IP:8505`

## 📁 Project Structure

```
aero-guardians/
├── app.py                          # Flask REST API backend
├── airsight_dashboard.py           # Streamlit dashboard with PDF generation
├── esp32_sensor_code.ino           # ESP32 firmware
├── requirements.txt                # Python dependencies
├── start_backend.bat               # Windows backend launcher
├── start_dashboard.bat             # Windows dashboard launcher
├── test_api.py                     # API testing script
├── data/
│   └── sensor_log.csv             # Sensor data storage (auto-generated)
├── ARCHITECTURE.md                 # System architecture documentation
├── SETUP_INSTRUCTIONS.md           # Detailed setup guide
├── DEPLOYMENT_CHECKLIST.md         # Production deployment checklist
├── QUICK_REFERENCE.md              # Command reference
└── ESP32_WIFI_TROUBLESHOOTING.md  # WiFi debugging guide
```

## 🔧 Configuration

### Safety Thresholds

Default regulatory compliance thresholds in `airsight_dashboard.py`:

```python
THRESHOLDS = {
    'dust': {'safe': 500, 'warning': 1000, 'hazard': 1500},      # µg/m³
    'temp': {'safe': 25, 'warning': 30, 'hazard': 35},           # °C
    'tvoc': {'safe': 200, 'warning': 500, 'hazard': 1000},       # ppb
    'eco2': {'safe': 800, 'warning': 1200, 'hazard': 2000}       # ppm
}
```

Modify these values based on your local regulations and requirements.

### Flask Backend

Configure in `app.py`:
- `host='0.0.0.0'` - Listens on all network interfaces
- `port=5000` - Default API port
- `debug=True` - Enable debug mode (disable in production)

## 📊 Dashboard Usage

### Main Dashboard
1. **View Real-time Data** - KPI cards update every 2 seconds
2. **Monitor Trends** - Interactive charts with zoom/pan
3. **Check Status** - Color-coded safety indicators (green/amber/red)
4. **AI Diagnostics** - Real-time recommendations in bottom panel

### PDF Report Generation
1. **Select Time Range** - Choose from dropdown (top-right)
2. **Click "Download PDF Report"** - Button in top-right corner
3. **Wait for Generation** - Spinner appears during processing
4. **Download** - Click blue download button when ready
5. **Save** - PDF saved to Downloads folder

### Sidebar Features
- **Industrial Zone** - Filter by monitoring area
- **Time Range** - Adjust data view period
- **Auto-refresh** - Toggle automatic updates
- **System Info** - View platform details

## 🔌 API Endpoints

### GET /
Health check endpoint
```bash
curl http://localhost:5000/
# Response: "Server is running"
```

### POST /api/data
Receive sensor data from ESP32
```json
{
    "dust": 820.5,
    "temp": 24.5,
    "tvoc": 150,
    "eco2": 650,
    "risk": "Moderate"
}
```

### GET /api/sensor-data
Retrieve all sensor data
```bash
curl http://localhost:5000/api/sensor-data
```

### GET /api/latest-sensor
Get most recent reading
```bash
curl http://localhost:5000/api/latest-sensor
```

## 🐛 Troubleshooting

### ESP32 Connection Issues
1. **Check WiFi credentials** - Verify SSID and password
2. **Verify server IP** - Use `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
3. **Firewall rules** - Allow port 5000 in Windows Firewall
4. **Network subnet** - Ensure ESP32 and computer are on same network
5. **Serial monitor** - Check ESP32 output for error messages

See `ESP32_WIFI_TROUBLESHOOTING.md` for detailed debugging steps.

### Dashboard Not Loading
1. **Check if backend is running** - Visit `http://localhost:5000`
2. **Verify port availability** - Port 8505 should be free
3. **Check dependencies** - Run `pip install -r requirements.txt`
4. **Browser cache** - Clear cache or try incognito mode

### PDF Generation Errors
1. **Install kaleido** - `pip install kaleido` (for chart export)
2. **Check data availability** - Ensure sensor data exists for selected time range
3. **Memory issues** - Close other applications if generating large reports

## 📦 Dependencies

### Python Packages
```
flask>=3.0.0
pandas>=2.0.0
requests>=2.31.0
streamlit>=1.28.0
plotly>=5.17.0
reportlab>=4.0.0
kaleido>=0.2.1
```

### Arduino Libraries
- Adafruit SSD1306
- Adafruit GFX
- Adafruit SGP30
- Adafruit MCP9808
- WiFi.h (ESP32 core)

## 🛡️ Safety & Compliance

### Regulatory Standards
- **PM2.5 Limits** - Based on WHO air quality guidelines
- **Temperature Ranges** - OSHA workplace comfort standards
- **TVOC Thresholds** - EPA indoor air quality recommendations
- **CO2 Levels** - ASHRAE ventilation standards

### Data Logging
- All readings timestamped in ISO 8601 format
- CSV storage for regulatory compliance
- Automatic data retention (configurable)
- Export capabilities for auditing

## 🚀 Production Deployment

### Recommended Setup
1. **Use HTTPS** - Configure SSL certificates for Flask
2. **Disable debug mode** - Set `debug=False` in `app.py`
3. **Use production server** - Deploy with Gunicorn or uWSGI
4. **Set up monitoring** - Use PM2 or systemd for process management
5. **Configure firewall** - Whitelist only required ports
6. **Regular backups** - Automated CSV data backups
7. **Update dependencies** - Keep packages up to date

See `DEPLOYMENT_CHECKLIST.md` for complete production checklist.

## 📖 Documentation

- **ARCHITECTURE.md** - System design and component overview
- **SETUP_INSTRUCTIONS.md** - Step-by-step installation guide
- **DEPLOYMENT_CHECKLIST.md** - Production deployment guide
- **QUICK_REFERENCE.md** - Command and API reference
- **ESP32_WIFI_TROUBLESHOOTING.md** - WiFi debugging help
- **PROJECT_SUMMARY.md** - Project overview and features

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Adafruit** - Sensor libraries and hardware support
- **Plotly** - Interactive visualization library
- **Streamlit** - Dashboard framework
- **Flask** - REST API framework
- **ReportLab** - PDF generation library

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting guides

---

**Built with ❤️ for industrial air quality monitoring and environmental compliance**
