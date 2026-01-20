# 🛰️ AeroGuardians - Industrial Emission Control System

> **Transform industrial pollution monitoring from reactive to proactive**  
> A complete end-to-end IoT system combining ESP32 hardware sensors, real-time automated control, Flask REST API backend, and a professional mission-control style dashboard for industrial air quality management.

![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.13+-blue)
![Platform](https://img.shields.io/badge/Platform-ESP32-orange)
![AI](https://img.shields.io/badge/AI-Powered-purple)
![Dashboard](https://img.shields.io/badge/Dashboard-Streamlit-red)
![Flask](https://img.shields.io/badge/Backend-Flask-black)

---

## 📋 Table of Contents
- [What is AeroGuardians?](#-what-is-aeroguardians)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Hardware Components](#-hardware-components)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Dashboard Usage](#-dashboard-usage)
- [API Documentation](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## 🎯 What is AeroGuardians?

**AeroGuardians** is an industrial emission control system designed to solve a critical real-world problem: **industries lack effective real-time emission control systems**. 

### The Problem
- Manual and intermittent air quality monitoring
- Delayed response to pollution events
- Non-automated control mechanisms
- Inability to prevent pollution before it escalates
- Regulatory violations and health risks

### Our Solution
AeroGuardians doesn't just **monitor** air quality—it actively **controls** emissions in real-time by automatically activating control mechanisms when thresholds are exceeded.

### Why This Matters
- 🏭 **Prevents pollution** before it becomes hazardous
- 👷 **Protects worker health** with immediate alerts and automated responses
- 📊 **Regulatory compliance** with comprehensive logging and reporting
- 💰 **Cost-effective** at ~₹2,700 hardware cost vs ₹50,000-5,00,000 commercial systems
- 🌍 **Environmental impact** reduction through proactive control

---

## ✨ Key Features

### 🎮 Automated Emission Control
**This is what sets us apart from simple monitoring systems:**
- **Automatic Mode**: System automatically activates control devices when thresholds are exceeded
  - 🌪️ **Exhaust Fan**: Auto-activates when eCO₂ > 1200ppm
  - 🔧 **Filtration Unit**: Auto-activates when Dust > 1000µg/m³
  - 💨 **Ventilation System**: Auto-activates when TVOC > 500ppb
- **Manual Mode**: Operators can override and control devices manually
- **Emergency Shutdown**: Immediate stop-all functionality
- **Comprehensive Logging**: Every control action documented for compliance

### 🔬 Hardware Sensor Network
| Component | Purpose | Specifications |
|-----------|---------|----------------|
| **ESP32** | Microcontroller & WiFi | Dual-core 240MHz, built-in WiFi |
| **GP2Y1014** | Dust/PM2.5 sensor | 0-500 µg/m³, infrared optical detection |
| **SGP30** | TVOC & eCO₂ sensor | Metal oxide, I2C, self-calibrating |
| **MCP9808** | Temperature sensor | ±0.25°C accuracy, -40°C to +125°C |
| **SSD1306** | OLED display | 128x64 pixels, local status display |
| **Buzzer** | Audio alerts | Immediate hazard warnings |

**Data Collection**: Sensor readings every 5 seconds, transmitted to backend via HTTP POST over WiFi

### 📊 Mission Control Dashboard
Built with Streamlit, inspired by SpaceX mission control aesthetic:

**Real-time Monitoring**
- 🎯 **4 KPI Cards**: PM2.5, Temperature, TVOC, eCO₂ with live values
- 📈 **Interactive Charts**: Dual-axis emission trends, thermal monitoring
- 🚦 **Color-Coded Status**: Green (Safe) / Yellow (Warning) / Red (Hazard)
- 🔄 **Auto-refresh**: Updates every 2 seconds
- 📱 **Responsive Design**: Works on desktop, tablet, mobile

**Control System Panel** (Sidebar)
- 🤖 **Mode Toggle**: Switch between Automatic and Manual control
- 🎛️ **Device Controls**: Individual ON/OFF switches for all control devices
- 🚨 **Emergency Shutdown**: One-click stop-all functionality
- 📊 **Status Indicators**: Real-time display of all device states

**Advanced Features**
- 💡 **AQI Gauge**: Real-time Air Quality Index (0-500 scale)
- 🤖 **AI Diagnostics**: Context-aware recommendations and risk assessment
- 📄 **PDF Reports**: Professional compliance reports with charts and analytics

### 🔧 Backend System
**Flask REST API** - Production-ready with:
- 🌐 RESTful endpoints for sensor data and control commands
- 📝 CSV data persistence with timestamps
- 🔄 Real-time control logic evaluation
- 🛡️ CORS support for cross-origin requests
- ⚡ Error handling and retry logic
- 📊 Control action logging for audit trails

### 📄 Professional PDF Report Generation
- ⏱️ **Time Range Selection**: 30 min to 24 hours
- 📊 **Embedded Charts**: High-quality emission and thermal trend visualizations
- 📈 **Statistical Analysis**: Min, max, average for all parameters
- 🤖 **AI-Generated Insights**: Detailed diagnostics and recommendations
- ✅ **Compliance Ready**: Formatted for regulatory submission
- 💼 **Executive Summary**: System health assessment and action items

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ESP32 HARDWARE                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ GP2Y1014 │  │  SGP30   │  │ MCP9808  │  │SSD1306   │       │
│  │  Dust    │  │TVOC/eCO₂ │  │   Temp   │  │  OLED    │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │              │             │              │
│       └─────────────┴──────────────┴─────────────┘              │
│                          │                                       │
│                    ┌─────▼─────┐                                │
│                    │   ESP32   │◄─── Buzzer Alert               │
│                    │WiFi Module│                                │
│                    └─────┬─────┘                                │
└──────────────────────────┼──────────────────────────────────────┘
                           │ HTTP POST (JSON)
                           │ Every 5 seconds
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FLASK BACKEND (PORT 5000)                     │
│  ┌───────────────────────────────────────────────────────┐      │
│  │  REST API Endpoints                                   │      │
│  │  • POST /api/data          - Receive sensor data      │      │
│  │  • GET  /api/sensor-data   - Return readings          │      │
│  │  • GET  /api/latest-sensor - Latest reading           │      │
│  │  • GET  /api/control/state - Control device states    │      │
│  │  • POST /api/control/set   - Update control devices   │      │
│  │  • GET  /api/control/history - Control action log     │      │
│  └───────────────────────────────────────────────────────┘      │
│                           │                                      │
│  ┌───────────────────────▼────────────────────────────┐         │
│  │  Automated Control Logic                           │         │
│  │  • Evaluate thresholds                             │         │
│  │  • Auto-activate control devices                   │         │
│  │  • Log all actions                                 │         │
│  └───────────────────────┬────────────────────────────┘         │
│                           │                                      │
│  ┌───────────────────────▼────────────────────────────┐         │
│  │  Data Persistence (CSV)                            │         │
│  │  • sensor_log.csv     - All readings               │         │
│  │  • control_log.csv    - Control actions            │         │
│  │  • realtime_log.csv   - Live buffer                │         │
│  └────────────────────────────────────────────────────┘         │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP GET/POST
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              STREAMLIT DASHBOARD (PORT 8501)                     │
│  ┌──────────────────────────────────────────────────────┐       │
│  │  Mission Control Interface                           │       │
│  │  • Real-time KPI cards with live data               │       │
│  │  • Interactive Plotly charts                        │       │
│  │  • Control system panel (Auto/Manual)               │       │
│  │  • Device control switches                          │       │
│  │  • AI diagnostics and recommendations               │       │
│  │  • PDF report generation                            │       │
│  └──────────────────────────────────────────────────────┘       │
│                                                                  │
│  Auto-refresh every 2 seconds                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow
1. **ESP32** reads sensors every 5 seconds → sends JSON via WiFi
2. **Flask Backend** receives data → evaluates thresholds → stores in CSV → updates control states
3. **Dashboard** fetches latest data via API → displays real-time → allows manual control
4. **Control Commands** from dashboard → backend → (future: relay modules) → physical devices

---

## 🔌 Hardware Components

### Bill of Materials (BOM)

| Component | Quantity | Price (₹) | Purpose |
|-----------|----------|-----------|---------|
| ESP32 Development Board | 1 | 500 | Microcontroller with WiFi |
| GP2Y1014 Dust Sensor | 1 | 500 | PM2.5 particulate measurement |
| SGP30 Gas Sensor | 1 | 800 | TVOC and eCO₂ detection |
| MCP9808 Temperature Sensor | 1 | 300 | High-precision temperature |
| SSD1306 OLED Display (128x64) | 1 | 200 | Local status display |
| Active Buzzer | 1 | 20 | Audio alerts |
| Breadboard | 1 | 100 | Prototyping |
| Jumper Wires | 1 pack | 100 | Connections |
| USB Cable (Micro/Type-C) | 1 | 150 | Power and programming |
| **TOTAL** | | **₹2,670** | |

### Wiring Diagram

**I2C Bus (Shared SDA/SCL):**
- SGP30: SDA → GPIO21, SCL → GPIO22
- MCP9808: SDA → GPIO21, SCL → GPIO22
- SSD1306: SDA → GPIO21, SCL → GPIO22

**Analog/Digital:**
- GP2Y1014: Output → GPIO34 (ADC1_CH6)
- Buzzer: Control → GPIO25

**Power:**
- All sensors: 3.3V from ESP32
- GP2Y1014: 5V via USB

---

## 🚀 Quick Start

### Prerequisites

**Hardware:**
- ESP32 development board
- Air quality sensors (GP2Y1014, SGP30, MCP9808)
- OLED display and buzzer
- Breadboard and jumper wires

**Software:**
- Python 3.8 or higher ([Download](https://www.python.org/downloads/))
- Arduino IDE 1.8.x or 2.x ([Download](https://www.arduino.cc/en/software))
- Git (optional, for cloning)

**Network:**
- WiFi network (2.4GHz recommended for ESP32)
- Computer and ESP32 on same network

---

### 📥 Installation Steps

#### Step 1: Clone/Download the Repository

**Option A: Using Git**
```bash
git clone https://github.com/yourusername/aero-guardians.git
cd aero-guardians
```

**Option B: Download ZIP**
1. Click green "Code" button → Download ZIP
2. Extract to desired location
3. Open folder in terminal

---

#### Step 2: Install Python Dependencies

**Windows:**
```cmd
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
pip3 install -r requirements.txt
```

This installs: Flask, Streamlit, Pandas, Plotly, ReportLab, Kaleido

---

#### Step 3: Configure ESP32 Firmware

1. **Open Arduino IDE**
2. **Install ESP32 Board Support:**
   - Go to File → Preferences
   - Add to "Additional Board Manager URLs":  
     `https://dl.espressif.com/dl/package_esp32_index.json`
   - Go to Tools → Board → Boards Manager
   - Search "ESP32" and install

3. **Install Required Libraries:**
   - Tools → Manage Libraries
   - Install: `Adafruit SSD1306`, `Adafruit GFX`, `Adafruit SGP30`, `Adafruit MCP9808`

4. **Open the Firmware:**
   - File → Open → `esp32_sensor_code.ino`

5. **Configure WiFi Credentials:**
   ```cpp
   const char* ssid = "YOUR_WIFI_NAME";        // Replace with your WiFi SSID
   const char* password = "YOUR_WIFI_PASSWORD"; // Replace with your WiFi password
   ```

6. **Find Your Computer's IP Address:**
   
   **Windows:** Open Command Prompt
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address" under your active network adapter (e.g., 192.168.1.100)
   
   **Mac/Linux:** Open Terminal
   ```bash
   ifconfig  # or: ip addr show
   ```
   Look for "inet" address (e.g., 192.168.1.100)

7. **Update Server IP in Code:**
   ```cpp
   const char* serverIP = "192.168.1.100";  // Replace with YOUR computer's IP
   ```

8. **Upload to ESP32:**
   - Connect ESP32 via USB
   - Tools → Board → Select your ESP32 board
   - Tools → Port → Select correct COM port
   - Click Upload button (→)
   - Wait for "Done uploading" message

---

#### Step 4: Start the Backend Server

**Windows:**
```cmd
start_backend.bat
```
*Double-click the file or run in Command Prompt*

**Linux/Mac:**
```bash
python3 app.py
```

**Expected Output:**
```
 * Running on http://0.0.0.0:5000
 * Running on http://192.168.1.100:5000
Press CTRL+C to quit
```

✅ Backend is now running on port 5000

---

#### Step 5: Start the Dashboard

**Open a NEW terminal/command prompt window**

**Windows:**
```cmd
start_dashboard.bat
```
*Double-click the file or run in Command Prompt*

**Linux/Mac:**
```bash
streamlit run airsight_dashboard.py --server.port 8501
```

**Expected Output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.1.100:8501
```

✅ Dashboard is now running on port 8501

---

#### Step 6: Access the Dashboard

1. **Open your web browser**
2. **Navigate to:** `http://localhost:8501`
3. **You should see:** AeroGuardians Mission Control interface

**If ESP32 is connected and transmitting:**
- KPI cards will show live sensor values
- Charts will populate with data
- Status indicators will update every 2 seconds

---

### 🎉 You're All Set!

Your AeroGuardians system is now operational:
- ✅ ESP32 transmitting sensor data every 5 seconds
- ✅ Backend receiving and processing data
- ✅ Dashboard displaying real-time monitoring
- ✅ Automated control logic evaluating thresholds

---

### 🧪 Testing Without Hardware

If you don't have the physical sensors yet, you can test with simulated data:

1. Run backend: `python app.py`
2. Use the test script:
   ```bash
   python test_api.py
   ```
   This sends sample sensor data to the backend
3. Open dashboard and see the simulated data

---

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

### Main Dashboard Interface

![Dashboard Overview](https://img.shields.io/badge/View-Mission%20Control-blue)

#### 1️⃣ Live Telemetry Cards (Top Section)
Four real-time KPI cards displaying:
- **PM2.5 Particulates** - Dust concentration in µg/m³
- **Temperature** - Ambient temperature in °C
- **TVOC Levels** - Volatile Organic Compounds in ppb
- **eCO₂ Concentration** - Equivalent CO₂ in ppm

**Color Indicators:**
- 🟢 **Green** = Safe (within normal limits)
- 🟡 **Yellow** = Warning (approaching threshold)
- 🔴 **Red** = Hazard (exceeds safety threshold)

#### 2️⃣ Control System Panel (Sidebar)

**Automatic Mode:**
- Toggle switch at top of sidebar
- When **ON**: System automatically activates control devices based on thresholds
- When **OFF**: Manual control only

**Manual Control Buttons:**
- 🌪️ **Exhaust Fan** - ON/OFF toggle
- 🔧 **Filtration Unit** - ON/OFF toggle
- 💨 **Ventilation System** - ON/OFF toggle
- 🚨 **EMERGENCY SHUTDOWN** - Stops all devices immediately

**Control Status Indicators:**
- Shows which devices are currently active
- Real-time updates as conditions change
- Displays whether in AUTO or MANUAL mode

#### 3️⃣ Emission Trend Charts
- **Dual-axis line chart**: PM2.5 (left axis) and TVOC (right axis) over time
- **Thermal conditions chart**: Temperature trends with warning zones
- **Interactive features**: Zoom, pan, hover for exact values
- **Time range selector**: View last 30 min, 1 hour, 6 hours, 12 hours, or 24 hours

#### 4️⃣ Air Quality Index (AQI)
- **Gauge meter**: 0-500 scale with color zones
- **Real-time calculation**: Based on current PM2.5 levels
- **Safety recommendations**: Context-aware guidance
- **Compliance status**: Regulatory threshold indicators

#### 5️⃣ AI Diagnostics Panel (Bottom)
- **Real-time risk assessment**: Safe / Moderate / Warning / Hazard
- **Smart recommendations**: Action items based on current readings
- **Parameter-specific insights**: Individual analysis for each sensor
- **Compliance alerts**: Warnings when thresholds are exceeded

---

### 📄 Generating PDF Reports

1. **Select Time Range** (top-right dropdown):
   - 30 minutes
   - 1 hour
   - 6 hours
   - 12 hours
   - 24 hours

2. **Click "Download PDF Report"** button

3. **Wait for generation** (spinner appears):
   - Charts are rendered
   - Statistics calculated
   - AI analysis generated
   - PDF compiled

4. **Download the file**:
   - Blue download button appears
   - Click to save PDF to your Downloads folder
   - Filename format: `AirQuality_Report_YYYYMMDD_HHMMSS.pdf`

**PDF Report Contents:**
- Executive summary with overall assessment
- Statistical tables (min, max, average for all parameters)
- Embedded emission and thermal trend charts
- AI-generated diagnostics for each parameter
- Regulatory compliance analysis
- Recommended actions and best practices
- Timestamp and data range information

---

### 🎛️ Control System Operation

#### Automatic Control Logic

When **Automatic Mode** is enabled, the system monitors thresholds and activates devices:

| Condition | Threshold | Automated Action |
|-----------|-----------|------------------|
| High Dust | PM2.5 > 1000 µg/m³ | ✅ Activate Filtration Unit |
| High eCO₂ | eCO₂ > 1200 ppm | ✅ Activate Exhaust Fan |
| High TVOC | TVOC > 500 ppb | ✅ Activate Ventilation System |
| Multiple Hazards | Any 2+ thresholds exceeded | ✅ Activate all relevant devices |

**Example Automated Response:**
```
1. PM2.5 reading: 1,250 µg/m³ (exceeds 1000 threshold)
2. System detects hazard condition
3. Automatically sends command: "Activate Filtration Unit"
4. Action logged to control_log.csv with timestamp and reason
5. Dashboard shows: "🔧 Filtration Unit ACTIVATED (Auto)"
6. Device remains active until reading drops below safe level
```

#### Manual Control Mode

When **Automatic Mode** is disabled:
- All control decisions are manual
- Operators use sidebar switches to control devices
- System still monitors and displays warnings
- Manual actions are logged for audit trail

#### Emergency Shutdown

The red **EMERGENCY SHUTDOWN** button:
- Immediately deactivates ALL control devices
- Overrides automatic mode
- Logs emergency stop action
- Requires manual restart of devices
- Use in case of equipment malfunction or safety concerns

---

## 🔌 API Documentation

The Flask backend provides RESTful API endpoints for sensor data and control commands.

**Base URL:** `http://localhost:5000` or `http://YOUR_IP:5000`

---

### Endpoints

#### 1. Health Check
```http
GET /
```
**Description:** Verify backend is running  
**Response:** `"Server is running"`

**Example:**
```bash
curl http://localhost:5000/
```

---

#### 2. Receive Sensor Data (from ESP32)
```http
POST /api/data
```
**Description:** ESP32 sends sensor readings to backend  
**Content-Type:** `application/json`

**Request Body:**
```json
{
    "dust": 820.5,      // PM2.5 in µg/m³
    "temp": 24.5,       // Temperature in °C
    "tvoc": 150,        // TVOC in ppb
    "eco2": 650,        // eCO₂ in ppm
    "risk": "Moderate"  // Risk level: Safe/Moderate/Warning/Hazard
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Data received"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/data \
  -H "Content-Type: application/json" \
  -d '{"dust":820.5,"temp":24.5,"tvoc":150,"eco2":650,"risk":"Moderate"}'
```

---

#### 3. Get All Sensor Data
```http
GET /api/sensor-data
```
**Description:** Retrieve all stored sensor readings  
**Response:** JSON array of all readings from `sensor_log.csv`

**Response Example:**
```json
[
    {
        "timestamp": "2026-01-20T10:30:45",
        "dust": 820.5,
        "temp": 24.5,
        "tvoc": 150,
        "eco2": 650,
        "risk": "Moderate"
    },
    // ... more readings
]
```

**Example:**
```bash
curl http://localhost:5000/api/sensor-data
```

---

#### 4. Get Latest Reading
```http
GET /api/latest-sensor
```
**Description:** Get most recent sensor reading  
**Response:** JSON object with latest values

**Response Example:**
```json
{
    "timestamp": "2026-01-20T10:35:50",
    "dust": 890.2,
    "temp": 25.1,
    "tvoc": 175,
    "eco2": 720,
    "risk": "Moderate"
}
```

**Example:**
```bash
curl http://localhost:5000/api/latest-sensor
```

---

#### 5. Get Control System State
```http
GET /api/control/state
```
**Description:** Get current state of all control devices  
**Response:** JSON object with device states and mode

**Response Example:**
```json
{
    "mode": "automatic",
    "devices": {
        "exhaust_fan": "active",
        "filtration_unit": "standby",
        "ventilation": "active"
    },
    "last_updated": "2026-01-20T10:35:50"
}
```

**Example:**
```bash
curl http://localhost:5000/api/control/state
```

---

#### 6. Set Control Device State
```http
POST /api/control/set
```
**Description:** Manually activate/deactivate control devices  
**Content-Type:** `application/json`

**Request Body:**
```json
{
    "device": "exhaust_fan",        // Device: exhaust_fan, filtration_unit, ventilation
    "state": "active",              // State: active, standby
    "mode": "manual",               // Mode: automatic, manual
    "reason": "Manual override"     // Optional reason for logging
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Device state updated",
    "device": "exhaust_fan",
    "new_state": "active"
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/control/set \
  -H "Content-Type: application/json" \
  -d '{"device":"exhaust_fan","state":"active","mode":"manual","reason":"Manual test"}'
```

---

#### 7. Get Control Action History
```http
GET /api/control/history
```
**Description:** Retrieve log of all control actions  
**Response:** JSON array from `control_log.csv`

**Response Example:**
```json
[
    {
        "timestamp": "2026-01-20T10:30:00",
        "device": "filtration_unit",
        "action": "activated",
        "mode": "automatic",
        "reason": "Dust level 1250 > 1000 µg/m³",
        "triggered_by": "system"
    },
    // ... more actions
]
```

**Example:**
```bash
curl http://localhost:5000/api/control/history
```

---

### Error Responses

All endpoints return appropriate HTTP status codes:

**Success:**
- `200 OK` - Request successful
- `201 Created` - Data successfully created

**Client Errors:**
- `400 Bad Request` - Invalid request format
- `404 Not Found` - Endpoint not found

**Server Errors:**
- `500 Internal Server Error` - Backend error

**Error Response Format:**
```json
{
    "status": "error",
    "message": "Description of the error"
}
```

---

## 🐛 Troubleshooting

### Common Issues and Solutions

#### ❌ ESP32 Not Connecting to WiFi

**Symptoms:**
- Serial monitor shows "Connecting to WiFi..."
- No "WiFi Connected" message
- ESP32 keeps restarting

**Solutions:**

1. **Verify WiFi Credentials**
   ```cpp
   // Check spelling and case-sensitivity
   const char* ssid = "YourWiFiName";     // Exact SSID
   const char* password = "YourPassword"; // Exact password
   ```

2. **Check WiFi Frequency**
   - ESP32 only supports 2.4GHz WiFi
   - Disable 5GHz or use 2.4GHz SSID

3. **Verify WiFi Security**
   - Supported: WPA/WPA2
   - Not supported: Enterprise networks, captive portals

4. **Check Network Settings**
   - Ensure router DHCP is enabled
   - Check MAC address filtering (whitelist ESP32)
   - Disable AP isolation if on guest network

5. **Monitor Serial Output**
   ```bash
   Tools → Serial Monitor → Set baud rate to 115200
   ```
   Look for specific error messages

**See:** `ESP32_WIFI_TROUBLESHOOTING.md` for detailed debugging steps

---

#### ❌ Backend Not Receiving Data

**Symptoms:**
- Dashboard shows "No data available"
- ESP32 connected to WiFi but no data appears
- Backend terminal shows no incoming requests

**Solutions:**

1. **Verify IP Address**
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig
   ```
   Confirm ESP32 code has correct IP (must match computer's IP)

2. **Check Firewall**
   
   **Windows Firewall:**
   ```
   1. Windows Security → Firewall & network protection
   2. Advanced settings → Inbound Rules
   3. New Rule → Port → TCP → Port 5000
   4. Allow the connection → Apply to Domain, Private, Public
   5. Name: "Flask Backend Port 5000"
   ```

   **Quick Test:**
   ```bash
   # Temporarily disable firewall to test
   # If works, then firewall is blocking
   ```

3. **Verify Backend is Running**
   ```bash
   curl http://localhost:5000/
   # Should return: "Server is running"
   ```

4. **Check Same Network**
   - ESP32 and computer must be on same subnet
   - Ping ESP32 IP from computer (if you know ESP32 IP)

5. **Test with Python Script**
   ```bash
   python test_api.py
   ```
   If this works, issue is with ESP32 communication

---

#### ❌ Dashboard Not Loading

**Symptoms:**
- Browser shows "Unable to connect"
- Port 8501 error
- Streamlit won't start

**Solutions:**

1. **Check if Port is in Use**
   
   **Windows:**
   ```cmd
   netstat -ano | findstr :8501
   ```
   
   **Mac/Linux:**
   ```bash
   lsof -i :8501
   ```
   
   If port is occupied, change port:
   ```bash
   streamlit run airsight_dashboard.py --server.port 8502
   ```

2. **Verify Dependencies**
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. **Clear Streamlit Cache**
   ```bash
   # Delete cache folder
   rm -rf ~/.streamlit/cache  # Mac/Linux
   rmdir /s %USERPROFILE%\.streamlit\cache  # Windows
   ```

4. **Check Browser**
   - Try incognito/private mode
   - Clear browser cache
   - Try different browser (Chrome recommended)
   - Disable browser extensions

5. **Check Python Version**
   ```bash
   python --version  # Should be 3.8+
   ```

---

#### ❌ PDF Generation Fails

**Symptoms:**
- "Error generating PDF" message
- Download button doesn't appear
- Charts not embedded in PDF

**Solutions:**

1. **Install Kaleido**
   ```bash
   pip install kaleido==0.2.1
   ```
   Kaleido is required for Plotly chart export

2. **Check Data Availability**
   - Ensure sensor data exists for selected time range
   - Try selecting a longer time range
   - Verify `sensor_log.csv` has data

3. **Check ReportLab**
   ```bash
   pip install reportlab --upgrade
   ```

4. **Memory Issues**
   - Close other applications
   - Reduce report time range (use 1 hour instead of 24 hours)
   - Restart Python processes

5. **Permissions**
   - Ensure write permissions in temp directory
   - Check disk space availability

---

#### ❌ Control Devices Not Responding

**Symptoms:**
- Control switches don't change device states
- Automatic mode not triggering actions
- Manual controls have no effect

**Solutions:**

1. **Check Backend API**
   ```bash
   curl http://localhost:5000/api/control/state
   ```
   Should return current device states

2. **Verify Dashboard Connection**
   - Look for connection error messages
   - Check browser console (F12) for errors
   - Refresh dashboard page

3. **Check Control Logic**
   - Verify thresholds are actually exceeded
   - Ensure Automatic Mode is enabled (toggle in sidebar)
   - Check `control_log.csv` for recorded actions

4. **Restart Services**
   ```bash
   # Stop backend (Ctrl+C)
   # Stop dashboard (Ctrl+C)
   # Restart both
   start_backend.bat
   start_dashboard.bat
   ```

---

#### ❌ Sensor Readings Look Wrong

**Symptoms:**
- Values are constant (never change)
- Readings are extremely high or low
- All sensors show 0 or error values

**Solutions:**

1. **Check Sensor Connections**
   - Verify wiring (SDA, SCL, power, ground)
   - Ensure I2C pull-up resistors (usually built-in)
   - Check for loose connections

2. **Test Individual Sensors**
   - Use Arduino IDE examples for each sensor
   - Test one sensor at a time
   - Verify I2C addresses (use I2C scanner sketch)

3. **Check Power Supply**
   - ESP32 should have stable 5V USB power
   - Some sensors need 3.3V, others need 5V
   - Check voltage with multimeter

4. **Sensor Warm-up Time**
   - SGP30 needs 15 seconds warm-up
   - GP2Y1014 needs stable environment
   - Wait 1 minute after power-on

5. **Calibration**
   - SGP30 self-calibrates over 12 hours
   - Test in clean air first
   - Compare with known good air quality meter

---

### 🔍 Debugging Tools

**View Backend Logs:**
- Terminal running `app.py` shows all incoming requests
- Look for POST requests from ESP32
- Check for error messages

**View ESP32 Serial Output:**
```bash
Arduino IDE → Tools → Serial Monitor (115200 baud)
```
Shows: WiFi connection status, sensor readings, HTTP responses

**Test API Manually:**
```bash
# Test data submission
python test_api.py

# Check latest data
curl http://localhost:5000/api/latest-sensor

# View all data
curl http://localhost:5000/api/sensor-data
```

**Check CSV Files:**
```bash
# View sensor data
type data\sensor_log.csv   # Windows
cat data/sensor_log.csv    # Mac/Linux

# View control actions
type data\control_log.csv  # Windows
cat data/control_log.csv   # Mac/Linux
```

---

### 📚 Additional Help

**Documentation Files:**
- `SETUP_INSTRUCTIONS.md` - Detailed setup guide
- `ESP32_WIFI_TROUBLESHOOTING.md` - WiFi-specific issues
- `DEPLOYMENT_CHECKLIST.md` - Production deployment
- `QUICK_REFERENCE.md` - Command reference
- `ARCHITECTURE.md` - System design

**Get Support:**
- Open an issue on GitHub
- Check existing issues for solutions
- Include error messages and system info
- Provide steps to reproduce

---

## 🌟 Real-World Applications

AeroGuardians can be deployed in various industrial settings:

### 🏭 Manufacturing Plants
- **Welding Operations** - Monitor metal fumes and particulates
- **Metal Grinding** - Track dust levels during cutting/grinding
- **Assembly Lines** - Maintain air quality in production areas
- **Worker Safety** - Automated alerts and ventilation control

### 🧪 Chemical Processing
- **Vapor Detection** - Real-time TVOC monitoring
- **Leak Detection** - Early warning for toxic gas releases
- **Compliance** - OSHA and EPA regulatory requirements
- **Emergency Response** - Automated ventilation activation

### 📦 Warehouses & Logistics
- **Loading Docks** - Monitor vehicle emissions
- **Material Handling** - Dust from packaging operations
- **Storage Areas** - Temperature and air quality control
- **Forklift Operations** - CO₂ and particulate monitoring

### 🎨 Paint Shops & Coating Facilities
- **VOC Emissions** - Track harmful organic compounds
- **Spray Booths** - Automated ventilation control
- **Curing Ovens** - Temperature monitoring
- **Environmental Permits** - Compliance documentation

### 🍕 Food Processing
- **Production Areas** - Hygiene and air quality
- **Storage Rooms** - Temperature and humidity monitoring
- **HACCP Compliance** - Food safety requirements
- **Quality Control** - Environmental condition tracking

---

## 🔮 Future Enhancements

### Hardware Roadmap
- 🔌 **Physical Relay Modules** - Control real equipment (fans, filters, dampers)
- 🌡️ **Additional Sensors** - NOx, SO₂, CO, humidity sensors
- 🔋 **Battery Backup** - UPS integration for continuous operation
- 📡 **Mesh Networking** - Multiple ESP32 nodes for large facilities
- 📱 **Touch Display** - Local HMI panel for on-site control
- ☁️ **Cloud Gateway** - LoRaWAN or cellular for remote sites

### Software Roadmap
- ☁️ **Cloud Deployment** - AWS/Azure hosting for remote access
- 📱 **Mobile App** - React Native app for iOS/Android
- 📧 **Notification System** - Email, SMS, push notifications
- 🤖 **Machine Learning** - Predictive maintenance and anomaly detection
- 🏢 **BMS Integration** - Connect to building management systems
- 👥 **Multi-facility Dashboard** - Corporate oversight for multiple locations
- 📊 **Advanced Analytics** - BigQuery/PowerBI integration
- 👤 **User Management** - Role-based access control
- 🔐 **Security** - HTTPS, authentication, API keys

### Analytics Roadmap
- 🧠 **AI Anomaly Detection** - Identify unusual patterns
- 🔍 **Pollution Source Identification** - Pinpoint emission sources
- ⚡ **Energy Optimization** - Reduce HVAC energy consumption
- 📈 **Predictive Forecasting** - Anticipate emission events
- 📋 **Compliance Reporting** - Automated regulatory reports
- 📊 **Trend Analysis** - Long-term environmental tracking

---

## 📦 Dependencies & Tech Stack

### Backend (Python)
```python
flask>=3.0.0           # REST API framework
flask-cors>=4.0.0      # Cross-origin resource sharing
pandas>=2.0.0          # Data manipulation and CSV handling
requests>=2.31.0       # HTTP library for API calls
```

### Frontend (Python)
```python
streamlit>=1.28.0      # Dashboard web framework
plotly>=5.17.0         # Interactive visualizations
reportlab>=4.0.0       # PDF generation
kaleido>=0.2.1         # Static image export for Plotly
```

### Embedded (C++/Arduino)
```cpp
WiFi.h                 // ESP32 WiFi connectivity (built-in)
HTTPClient.h           // HTTP POST requests (built-in)
Wire.h                 // I2C communication (built-in)
Adafruit_GFX.h         // Graphics library for OLED
Adafruit_SSD1306.h     // OLED display driver
Adafruit_SGP30.h       // TVOC/eCO₂ sensor library
Adafruit_MCP9808.h     // Temperature sensor library
```

### System Requirements
- **Python**: 3.8 or higher
- **Arduino IDE**: 1.8.x or 2.x
- **Operating System**: Windows 10/11, macOS, Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB for software and data
- **Network**: WiFi 2.4GHz (ESP32 compatible)

---

## 🛡️ Safety & Regulatory Compliance

### Threshold Standards

**PM2.5 (Particulate Matter):**
- Based on WHO Air Quality Guidelines
- Safe: < 500 µg/m³ (8-hour exposure)
- Warning: 500-1000 µg/m³
- Hazard: > 1500 µg/m³

**Temperature:**
- Based on OSHA workplace standards
- Safe: < 25°C (77°F)
- Warning: 25-30°C (77-86°F)
- Hazard: > 35°C (95°F)

**TVOC (Total Volatile Organic Compounds):**
- Based on EPA indoor air quality recommendations
- Safe: < 200 ppb
- Warning: 200-500 ppb
- Hazard: > 1000 ppb

**eCO₂ (Equivalent Carbon Dioxide):**
- Based on ASHRAE Standard 62.1
- Safe: < 800 ppm (outdoor baseline)
- Warning: 800-1200 ppm
- Hazard: > 2000 ppm

### Data Logging & Auditing
- ✅ All readings timestamped in ISO 8601 format
- ✅ CSV storage for regulatory compliance
- ✅ Immutable append-only logs
- ✅ Export capabilities for auditing
- ✅ Control action logs with reason codes
- ✅ PDF reports for compliance submission

### Regulatory Frameworks
- **OSHA** - Occupational Safety and Health Administration
- **EPA** - Environmental Protection Agency
- **ASHRAE** - American Society of Heating, Refrigerating and Air-Conditioning Engineers
- **WHO** - World Health Organization guidelines
- **ISO 45001** - Occupational health and safety management

---

## 🚀 Production Deployment

### Pre-Deployment Checklist

**Security:**
- [ ] Change default credentials
- [ ] Enable HTTPS/SSL for Flask
- [ ] Set up firewall rules (whitelist only required ports)
- [ ] Implement API authentication (JWT tokens)
- [ ] Disable debug mode (`debug=False` in app.py)
- [ ] Use environment variables for secrets

**Infrastructure:**
- [ ] Use production WSGI server (Gunicorn/uWSGI)
- [ ] Set up reverse proxy (Nginx/Apache)
- [ ] Configure process manager (PM2/systemd)
- [ ] Implement load balancing (if multiple servers)
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Configure automated backups

**Database:**
- [ ] Migrate from CSV to PostgreSQL/InfluxDB
- [ ] Implement data retention policies
- [ ] Set up automated backups
- [ ] Create database indexes for performance
- [ ] Implement connection pooling

**Maintenance:**
- [ ] Schedule regular dependency updates
- [ ] Set up log rotation
- [ ] Implement health check endpoints
- [ ] Configure alerting for system failures
- [ ] Create disaster recovery plan

### Recommended Production Setup

```bash
# Example with Gunicorn (production WSGI server)
pip install gunicorn

# Run backend with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Run Streamlit with production config
streamlit run airsight_dashboard.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  --server.enableCORS false \
  --server.enableXsrfProtection true
```

See `DEPLOYMENT_CHECKLIST.md` for complete production deployment guide.

---

## 📖 Documentation

Comprehensive documentation is available in the repository:

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Project overview and getting started guide (this file) |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System design, component diagrams, data flow |
| [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) | Detailed step-by-step installation guide |
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Production deployment checklist and best practices |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Command reference and API cheat sheet |
| [ESP32_WIFI_TROUBLESHOOTING.md](ESP32_WIFI_TROUBLESHOOTING.md) | WiFi connectivity debugging guide |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Executive summary and feature overview |
| [PRESENTATION_SCRIPT.md](PRESENTATION_SCRIPT.md) | Complete presentation guide with talking points |

---

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute
- 🐛 **Report Bugs** - Open an issue with detailed steps to reproduce
- ✨ **Suggest Features** - Share your ideas for improvements
- 📖 **Improve Documentation** - Fix typos, add examples, clarify instructions
- 🔧 **Submit Code** - Fix bugs or implement new features
- 🧪 **Test** - Help test on different platforms and configurations
- 🌍 **Translate** - Help make docs available in other languages

### Development Workflow

1. **Fork the Repository**
   ```bash
   # Click "Fork" button on GitHub
   # Clone your fork
   git clone https://github.com/YOUR_USERNAME/aero-guardians.git
   cd aero-guardians
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-new-feature
   # Or for bug fixes:
   git checkout -b fix/bug-description
   ```

3. **Make Your Changes**
   - Write clean, documented code
   - Follow existing code style
   - Add comments for complex logic
   - Test thoroughly

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add amazing new feature"
   
   # Use clear commit messages:
   # - "Add: new feature"
   # - "Fix: bug in sensor reading"
   # - "Update: documentation for API"
   # - "Refactor: improve code structure"
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/amazing-new-feature
   ```

6. **Open a Pull Request**
   - Go to original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Describe your changes clearly
   - Reference any related issues

### Code Style Guidelines
- **Python**: Follow PEP 8 style guide
- **C++/Arduino**: Follow Arduino style conventions
- **Comments**: Use clear, concise comments
- **Naming**: Use descriptive variable and function names
- **Documentation**: Update relevant docs with your changes

### Reporting Issues

When reporting bugs, please include:
- **Description**: Clear description of the issue
- **Steps to Reproduce**: Exact steps to recreate the problem
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Environment**: OS, Python version, hardware details
- **Screenshots/Logs**: If applicable

**Issue Template:**
```markdown
**Bug Description:**
Clear and concise description

**To Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: Windows 11
- Python: 3.11
- ESP32 Board: DevKit v1
- Browser: Chrome 120

**Additional Context:**
Any other relevant information
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 AeroGuardians Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

This project was made possible thanks to:

### Open Source Libraries
- **[Flask](https://flask.palletsprojects.com/)** - Lightweight web framework for backend API
- **[Streamlit](https://streamlit.io/)** - Rapid dashboard development framework
- **[Plotly](https://plotly.com/)** - Interactive data visualization library
- **[Pandas](https://pandas.pydata.org/)** - Data manipulation and analysis
- **[ReportLab](https://www.reportlab.com/)** - Professional PDF generation

### Hardware & Firmware
- **[Adafruit Industries](https://www.adafruit.com/)** - Sensor libraries and hardware support
- **[Espressif Systems](https://www.espressif.com/)** - ESP32 platform and tools
- **[Arduino](https://www.arduino.cc/)** - Development environment and ecosystem

### Inspiration & Design
- **[SpaceX](https://www.spacex.com/)** - Mission control aesthetic inspiration
- **IoT Community** - Best practices and design patterns
- **Environmental Monitoring Projects** - Real-world use cases and requirements

### Special Thanks
- All contributors who submit issues, PRs, and feedback
- Beta testers who helped validate the system
- The open-source community for amazing tools and libraries

---

## 📧 Support & Contact

### Getting Help

**Documentation:**
- Start with this README for overview
- Check [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for installation help
- Review [ESP32_WIFI_TROUBLESHOOTING.md](ESP32_WIFI_TROUBLESHOOTING.md) for connectivity issues

**GitHub Issues:**
- Search existing issues first: [Issues Page](https://github.com/yourusername/aero-guardians/issues)
- Open a new issue if your problem isn't covered
- Use issue templates for bugs and feature requests

**Community:**
- ⭐ **Star** the repository if you find it useful
- 👁️ **Watch** for updates and new releases
- 🍴 **Fork** to create your own customized version

### Stay Updated
- Follow releases for new versions
- Check changelog for new features
- Subscribe to notifications for important updates

---

## 🎓 Educational Use

AeroGuardians is perfect for:
- 🎓 **University Projects** - IoT, embedded systems, environmental engineering
- 📚 **Learning** - Hands-on experience with ESP32, Flask, Streamlit
- 🏆 **Competitions** - Hackathons, science fairs, innovation challenges
- 🔬 **Research** - Air quality monitoring, industrial safety studies
- 💼 **Portfolio** - Demonstrate full-stack IoT development skills

**Citation:**
If you use AeroGuardians in academic work, please cite:
```
AeroGuardians - Industrial Emission Control System
https://github.com/yourusername/aero-guardians
Accessed: [Date]
```

---

## 🌟 Project Statistics

![GitHub stars](https://img.shields.io/github/stars/yourusername/aero-guardians?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/aero-guardians?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/yourusername/aero-guardians?style=social)

![GitHub issues](https://img.shields.io/github/issues/yourusername/aero-guardians)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/aero-guardians)
![GitHub last commit](https://img.shields.io/github/last-commit/yourusername/aero-guardians)

---

## 💡 Quick Links

| Resource | Link |
|----------|------|
| 🏠 Homepage | [Project Website](#) |
| 📖 Documentation | [Full Docs](./ARCHITECTURE.md) |
| 🐛 Report Bug | [Issues](https://github.com/yourusername/aero-guardians/issues/new?template=bug_report.md) |
| ✨ Request Feature | [Issues](https://github.com/yourusername/aero-guardians/issues/new?template=feature_request.md) |
| 💬 Discussions | [GitHub Discussions](https://github.com/yourusername/aero-guardians/discussions) |
| 📺 Demo Video | [YouTube](#) |

---

<div align="center">

## ⭐ Star This Repository

If AeroGuardians helped you or you find it useful, please consider giving it a star! ⭐

**Built with ❤️ for industrial air quality monitoring and environmental compliance**

---

### 🌍 Making industries cleaner, safer, and more sustainable, one sensor at a time.

---

*AeroGuardians © 2026 | [MIT License](LICENSE) | Made with passion for a better environment*

</div>
