# 🌊 PeatSense - Peatland Groundwater Monitoring System

[![Status](https://img.shields.io/badge/Status-Prototype-yellow)](https://github.com/your-repo/peatsense)
[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-ESP32S3-orange)](https://www.seeedstudio.com/XIAO-ESP32S3-p-5627.html)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**Automated flood and fire risk monitoring for Indonesian peatland communities**

> From invisible underground changes to life-saving community alerts. Real-time monitoring that works even when the internet fails.

---

## 📁 Project Structure

```
peatsense/
│
├── 📄 README.md                    ← You are here
├── 📄 HARDWARE_GUIDE.md            ← Complete hardware setup & BOM
├── 📄 SETUP_GUIDE.md               ← Installation & deployment guide
│
├── 🔧 peatsense_firmware.ino       ← ESP32 firmware (Arduino)
├── 🐍 backend_api.py               ← FastAPI backend server
├── 📊 dashboard.py                 ← Streamlit web dashboard
├── 🧪 test_backend.py              ← API test script
│
├── 📦 requirements.txt             ← Python dependencies
├── ⚡ start_backend.bat            ← Quick start backend
├── ⚡ start_dashboard.bat          ← Quick start dashboard
│
└── 📂 data/                        ← Sensor data storage
```

---

## 🎯 What is PeatSense?

PeatSense monitors groundwater levels, salinity, and fire risk in Indonesian peatlands. It converts invisible underground changes into simple, actionable warnings that prevent:

- 🌊 **Floods** - Water level monitoring with advance warning
- 🔥 **Peat fires** - VOC, PM2.5, and humidity tracking
- 🌾 **Crop loss** - Salinity detection for farming decisions
- ☁️ **Haze disasters** - Early smoke/fire detection

**Target**: Sungai Tohor village, Riau, Indonesia (pilot site)

---

## ✨ Key Features

### 💧 Water Monitoring
- **Ultrasonic sensor** - Measures water level in canals
- **TDS sensor** - Detects saltwater intrusion
- **Flood prediction** - 24-48 hour advance warning

### 🔥 Fire Risk Detection
- **VOC sensor** - Detects peat drying/burning gases
- **PM2.5 sensor** - Catches smoke and haze
- **Humidity tracking** - Predicts dangerous dry conditions

### 🚨 Community Alerts
- **WhatsApp integration** - Alerts to village leaders
- **Physical display** - RGB LED + OLED visible from distance
- **Offline capable** - Works without internet

### 🏗️ Technical Highlights
- **Edge processing** - ESP32 calculates risk locally
- **Low cost** - ~$120 per node with Grove plug-and-play
- **Solar powered** - Runs indefinitely in remote areas
- **Field maintainable** - No soldering, community-serviceable

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Mosquitto MQTT broker
- Arduino IDE (for ESP32 firmware)

### 1️⃣ Clone Repository
```bash
git clone https://github.com/your-repo/peatsense.git
cd peatsense
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Setup Database
```bash
# Install PostgreSQL, then:
createdb peatsense
```

### 4️⃣ Start Backend
```bash
# Windows
start_backend.bat

# Linux/Mac
python backend_api.py
```

Backend runs on: http://localhost:8000  
API docs: http://localhost:8000/docs

### 5️⃣ Start Dashboard
```bash
# Windows
start_dashboard.bat

# Linux/Mac
streamlit run dashboard.py
```

Dashboard opens at: http://localhost:8501

### 6️⃣ Upload ESP32 Firmware
1. Open `peatsense_firmware.ino` in Arduino IDE
2. Configure WiFi credentials (lines 35-36)
3. Select board: `XIAO ESP32S3`
4. Upload to device

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[HARDWARE_GUIDE.md](HARDWARE_GUIDE.md)** | Complete BOM, assembly instructions, sensor calibration, field deployment |
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | Step-by-step software setup, troubleshooting, testing procedures |
| **[API Docs](http://localhost:8000/docs)** | Interactive API documentation (when backend running) |

---

## 🔧 Hardware Requirements

**Core Kit (~$120 USD):**
- Seeed XIAO ESP32S3 + Grove Base Board
- Grove Ultrasonic Distance Sensor (HC-SR04)
- Grove TDS Sensor (salinity)
- Grove SGP30 VOC Sensor
- Grove Dust Sensor (PM2.5)
- Grove MCP9808 Temp/Humidity
- Solar panel + battery
- Weatherproof enclosure

See [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md) for complete specifications.

---

## 🌍 Deployment

**Pilot Site**: Sungai Tohor, Riau, Indonesia  
**Partner**: PM.Haze NGO  
**Target Users**: Wetland farmers, community firefighters, village leaders

**Installation**:
1. Mount sensor node beside peat canal
2. Position ultrasonic sensor above water
3. Submerge TDS probe at fixed depth
4. Connect solar panel
5. Power on and verify in dashboard

---

## 🧪 Testing

```bash
# Test backend API
python test_backend.py

# Expected output:
# ✅ Health check passed
# ✅ Sensor reading stored
# ✅ Dashboard stats retrieved
```

---

## 📊 Technology Stack

| Layer | Technology |
|-------|------------|
| **Hardware** | Seeed XIAO ESP32S3, Grove sensors |
| **Firmware** | Arduino C++, MQTT, I2C |
| **Backend** | FastAPI, PostgreSQL, Paho MQTT |
| **Dashboard** | Streamlit, Plotly |
| **Alerts** | Twilio WhatsApp Business API |
| **Deployment** | Docker, AWS (optional) |

---

## 🤝 Contributing

We welcome contributions! This project serves real communities facing climate disasters.

**How to help**:
- 🐛 Report bugs in [Issues](https://github.com/your-repo/peatsense/issues)
- 💡 Suggest features for community needs
- 📝 Improve documentation
- 🔧 Submit pull requests
- 🌍 Help with deployment in other peatland regions

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file

---

## 👥 Team & Partners

**Developed by**: PeatSense Team  
**Partner NGO**: [PM.Haze](https://pmhaze.org)  
**Target Community**: Sungai Tohor village, Riau, Indonesia

**UN SDG Alignment**: Goals 1, 6, 13, 15, 17

---

## 📞 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/peatsense/issues)
- **Email**: support@peatsense.org
- **Documentation**: [Full docs](https://docs.peatsense.org)

---

## 🙏 Acknowledgments

- PM.Haze NGO for community partnerships and field expertise
- Sungai Tohor community for pilot testing
- Seeed Studio for Grove IoT platform
- Indonesian peatland restoration programs

---

**Built with ❤️ for climate resilience**

*Last updated: January 2026*
