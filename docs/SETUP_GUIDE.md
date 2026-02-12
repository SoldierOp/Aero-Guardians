# 🚀 PeatSense Setup Guide

Complete setup instructions for the PeatSense peatland monitoring system.

---

## 📋 Prerequisites

### Hardware Requirements
- ✅ Complete PeatSense hardware kit (see [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md))
- ✅ USB-C cable for programming
- ✅ Computer with Arduino IDE or PlatformIO
- ✅ WiFi network (2.4 GHz)

### Software Requirements
- Python 3.10 or higher
- PostgreSQL 14 or higher
- Mosquitto MQTT broker (or AWS IoT Core)
- Arduino IDE 2.0+ or PlatformIO
- Node.js (optional, for advanced frontend)

### Accounts Needed
- Twilio account (for WhatsApp alerts)
- AWS account (optional, for cloud deployment)

---

## 🔧 Part 1: Hardware Setup

### Step 1: Install Arduino IDE and Libraries

1. **Download Arduino IDE 2.0+**
   ```
   https://www.arduino.cc/en/software
   ```

2. **Install ESP32 Board Support**
   - Open Arduino IDE
   - Go to `File > Preferences`
   - Add to "Additional Board Manager URLs":
     ```
     https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
     ```
   - Go to `Tools > Board > Boards Manager`
   - Search "ESP32" and install "esp32 by Espressif Systems"

3. **Install Required Libraries**
   
   Open `Tools > Manage Libraries` and install:
   - `Adafruit SGP30 Sensor` by Adafruit
   - `Adafruit MCP9808 Library` by Adafruit
   - `Adafruit NeoPixel` by Adafruit
   - `U8g2` by oliver (for OLED display)
   - `PubSubClient` by Nick O'Leary (for MQTT)
   - `Seeed_HM330X` by Seeed Studio (for dust sensor)

### Step 2: Assemble Hardware

Follow the complete assembly guide in [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md).

**Quick checklist:**
- [ ] XIAO ESP32S3 mounted on Grove Base Board
- [ ] I2C Hub connected to I2C Port 1
- [ ] All sensors connected via Grove cables
- [ ] Ultrasonic sensor on D0/D1 port
- [ ] TDS sensor on A0/A1 port (via USB-UART adapter)
- [ ] RGB LED strip connected
- [ ] Power source ready (USB-C or solar)

### Step 3: Upload Firmware

1. **Open `peatsense_firmware.ino` in Arduino IDE**

2. **Configure WiFi and MQTT**
   
   Edit lines 35-41:
   ```cpp
   const char* WIFI_SSID = "YOUR_WIFI_SSID";
   const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
   const char* MQTT_BROKER = "mqtt.peatsense.local";  // Or AWS IoT endpoint
   const char* NODE_ID = "SungaiTohor_Node01";
   ```

3. **Calibrate Sensors**
   
   Edit lines 57-73 based on your installation:
   ```cpp
   const float CANAL_DEPTH_CM = 200.0;  // Measure your canal depth
   const float FLOOD_WARNING_CM = 150.0;
   const float FLOOD_DANGER_CM = 180.0;
   ```

4. **Select Board and Port**
   - `Tools > Board > ESP32 Arduino > XIAO_ESP32S3`
   - `Tools > Port` → Select your COM port

5. **Upload**
   - Click Upload button
   - Wait for "Done uploading" message
   - Open Serial Monitor (115200 baud) to verify

6. **Verify Operation**
   
   You should see in Serial Monitor:
   ```
   🌊 PeatSense v1.0 Starting...
   ✓ Ultrasonic sensor initialized
   ✓ TDS sensor initialized
   ✓ SGP30 VOC sensor found
   ✓ MCP9808 temp sensor found
   ✓ HM330X dust sensor found
   📡 Connecting to WiFi...
   ✓ WiFi connected!
   🚀 PeatSense Ready!
   ```

---

## 🖥️ Part 2: Backend Setup

### Step 1: Install PostgreSQL

**Windows:**
```powershell
# Download from https://www.postgresql.org/download/windows/
# Or use chocolatey:
choco install postgresql
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib

# Mac
brew install postgresql
```

### Step 2: Create Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE peatsense;

-- Create user (optional)
CREATE USER peatsense_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE peatsense TO peatsense_user;
```

### Step 3: Install MQTT Broker

**Option A: Mosquitto (Local)**

```bash
# Windows
choco install mosquitto

# Linux
sudo apt install mosquitto mosquitto-clients

# Mac
brew install mosquitto
```

Start Mosquitto:
```bash
mosquitto -v
```

**Option B: AWS IoT Core (Cloud)**
- See AWS IoT Core documentation
- Update MQTT_BROKER in firmware and backend

### Step 4: Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 5: Configure Backend

Create `.env` file in project root:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=peatsense
DB_USER=postgres
DB_PASSWORD=your_password

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Add village leader WhatsApp numbers in backend_api.py
```

### Step 6: Initialize Database

```bash
# The backend will auto-create tables on first run
python backend_api.py
```

You should see:
```
🚀 PeatSense Backend Starting...
✓ Database initialized successfully
✓ MQTT client started
✅ Backend ready!
```

---

## 📊 Part 3: Dashboard Setup

### Step 1: Verify Backend is Running

```bash
# Test API health
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "mqtt": "connected"
}
```

### Step 2: Start Dashboard

```bash
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`

### Step 3: Verify Dashboard Connection

- Check "System Overview" page
- Verify nodes appear
- Confirm data is updating

---

## 🧪 Part 4: Testing

### Test 1: Sensor Data Flow

1. **Check ESP32 Serial Monitor**
   ```
   📊 Reading Sensors...
   Water level: 45.2 cm
   TDS/Salinity: 345 ppm
   VOC: 412 ppb
   ```

2. **Check MQTT Messages**
   ```bash
   # Subscribe to data topic
   mosquitto_sub -t peatsense/data -v
   ```

3. **Check Database**
   ```sql
   SELECT * FROM sensor_readings ORDER BY recorded_at DESC LIMIT 10;
   ```

4. **Check Dashboard**
   - Open dashboard
   - Navigate to "Water Monitoring"
   - Verify charts show data

### Test 2: Alert System

1. **Trigger Test Alert**
   
   Simulate flood condition:
   - Place ultrasonic sensor very close to table
   - Water level reading will spike
   - Should trigger alert

2. **Verify Alert Flow**
   - Check Serial Monitor for "🚨 SENDING ALERT!"
   - Check MQTT: `mosquitto_sub -t peatsense/alerts`
   - Check database alerts table
   - Check WhatsApp (if configured)

3. **Check Dashboard Alerts Page**
   - Should show recent alert
   - Verify WhatsApp status

### Test 3: Offline Mode

1. **Disconnect WiFi**
   - Turn off router or change WiFi password in firmware
   - ESP32 should enter offline mode

2. **Verify Local Operation**
   - OLED display still updates
   - RGB LED still shows risk level
   - Serial Monitor shows "⚠ Offline - alert stored locally"

3. **Reconnect WiFi**
   - Restore WiFi
   - ESP32 should reconnect automatically
   - Verify data resumes uploading

---

## 🚀 Part 5: Field Deployment

### Pre-Deployment Checklist

- [ ] All sensors calibrated
- [ ] Weatherproof enclosure assembled
- [ ] Solar panel and battery installed
- [ ] Site selected and measured
- [ ] Mounting pole installed
- [ ] WiFi tested at site location
- [ ] Backup power tested (24hr battery test)
- [ ] Emergency contact numbers added
- [ ] Village leaders trained on WhatsApp alerts

### Deployment Steps

1. **Install mounting structure**
   - 1.5m pole above ground
   - Secure in concrete or soil
   - Level and stable

2. **Mount enclosure**
   - Attach to pole
   - Solar panel facing south (15° tilt)
   - Ensure all cables secured

3. **Position water sensors**
   - Ultrasonic: 50cm above max water level
   - TDS probe: 10cm below min water level
   - Mark "zero point" on canal

4. **Power on and verify**
   - Connect power
   - Check OLED display shows "PeatSense Ready"
   - Verify RGB LED is green
   - Check dashboard shows node online

5. **Final testing**
   - Walk 50m away - verify LED visible
   - Check mobile dashboard access
   - Test WhatsApp alert reception
   - Document installation photos

### Post-Deployment Monitoring

**Week 1:**
- Daily site visits
- Verify readings make sense
- Adjust calibration if needed
- Check battery charging

**Week 2-4:**
- 3x per week visits
- Clean sensors
- Check for physical damage
- Review alert history

**Ongoing:**
- Monthly maintenance
- Quarterly calibration
- Annual weatherproofing inspection

---

## 🔍 Troubleshooting

### ESP32 Won't Upload

**Issue**: "Failed to connect to ESP32"

**Solutions**:
- Hold BOOT button while clicking Upload
- Try different USB cable
- Install CP210x drivers (Google "ESP32 drivers")
- Select correct COM port in Arduino IDE

### WiFi Won't Connect

**Issue**: "✗ WiFi failed - entering offline mode"

**Solutions**:
- Verify SSID and password spelling
- Check WiFi is 2.4 GHz (not 5 GHz)
- Move closer to router
- Check router allows new devices
- Try phone hotspot for testing

### No MQTT Data

**Issue**: Data not reaching backend

**Solutions**:
- Check Mosquitto running: `mosquitto -v`
- Verify firewall allows port 1883
- Check MQTT_BROKER IP in firmware
- Test with: `mosquitto_sub -t peatsense/#`
- Check ESP32 Serial Monitor for publish confirmations

### Database Connection Failed

**Issue**: "❌ Database connection failed"

**Solutions**:
- Verify PostgreSQL running
- Check .env credentials
- Test connection: `psql -U postgres -d peatsense`
- Check firewall allows port 5432
- Verify database exists: `\l` in psql

### Dashboard Shows "No Data"

**Issue**: Dashboard empty despite backend running

**Solutions**:
- Check backend running: `curl http://localhost:8000/api/health`
- Verify API_BASE_URL in dashboard.py
- Check browser console for errors (F12)
- Verify data in database: `SELECT COUNT(*) FROM sensor_readings;`
- Check timestamp not in future

### WhatsApp Not Sending

**Issue**: Alerts not received on WhatsApp

**Solutions**:
- Verify Twilio credentials in .env
- Check Twilio balance/account status
- Test phone number format: `whatsapp:+628123456789`
- Check VILLAGE_LEADERS list in backend_api.py
- Review Twilio console for error logs
- Verify recipients accepted WhatsApp opt-in

### Sensor Readings Unstable

**Issue**: Erratic or impossible values

**Solutions**:

**Ultrasonic:**
- Clean sensor face
- Remove obstructions in beam path
- Check cable connections
- Verify sensor height calibration

**TDS:**
- Clean probe with distilled water
- Recalibrate with known solutions
- Check probe not dried out
- Verify voltage reading 0-5V

**SGP30:**
- Allow 15 min warm-up
- Ensure good airflow
- Check I2C connections
- Reset baseline if needed

**Dust Sensor:**
- Clean inlet filter
- Verify I2C address
- Check fan spinning
- Replace if readings stuck at 0

---

## 📱 Part 6: WhatsApp Configuration

### Twilio Setup

1. **Create Twilio Account**
   - Go to https://www.twilio.com
   - Sign up for free trial
   - Verify your phone number

2. **Enable WhatsApp Sandbox**
   - Console → Messaging → Try it out → Send a WhatsApp message
   - Follow instructions to join sandbox
   - Send "join [your-sandbox-keyword]" to Twilio number

3. **Get Credentials**
   - Account SID: Console → Dashboard
   - Auth Token: Console → Dashboard
   - WhatsApp From: `whatsapp:+14155238886` (sandbox)

4. **Add to .env**
   ```env
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   ```

5. **Add Village Leader Numbers**
   
   Edit `backend_api.py` line 50:
   ```python
   VILLAGE_LEADERS = [
       'whatsapp:+628123456789',  # Village Head
       'whatsapp:+628234567890',  # PM.Haze Coordinator
       'whatsapp:+628345678901',  # Fire Chief
   ]
   ```

6. **Test Alert**
   ```bash
   curl -X POST http://localhost:8000/api/alerts \
   -H "Content-Type: application/json" \
   -d '{
     "node_id": "test_node",
     "type": "FLOOD",
     "level": "WARNING",
     "message": "Test alert",
     "water_level": 155.0,
     "tds": 1200.0
   }'
   ```

### Production WhatsApp (Post-Trial)

For production deployment:
1. Upgrade Twilio account (remove trial limits)
2. Apply for WhatsApp Business API approval
3. Replace sandbox number with approved number
4. Update firmware and backend config

---

## 🌐 Part 7: Cloud Deployment (Optional)

### AWS Deployment

**Services needed:**
- EC2 (backend server)
- RDS PostgreSQL (database)
- AWS IoT Core (MQTT)
- CloudWatch (monitoring)

**Quick start:**
```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. Install dependencies
sudo apt update
sudo apt install python3-pip postgresql-client mosquitto-clients

# 3. Clone repository
git clone https://github.com/your-repo/peatsense.git
cd peatsense

# 4. Install Python packages
pip3 install -r requirements.txt

# 5. Configure environment
nano .env  # Add AWS RDS and IoT Core details

# 6. Run backend
python3 backend_api.py &

# 7. Run dashboard
streamlit run dashboard.py --server.port 80 &
```

**Security:**
- Set up VPC security groups
- Use HTTPS (Lets Encrypt certificate)
- Enable RDS encryption
- Use IAM roles for services

---

## 📚 Additional Resources

- **Hardware Guide**: [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md)
- **API Documentation**: http://localhost:8000/docs (when backend running)
- **Dashboard**: http://localhost:8501
- **Community Forum**: [Link to discussion forum]
- **PM.Haze Website**: https://pmhaze.org

---

## 🆘 Getting Help

**Technical Issues:**
- Check [GitHub Issues](https://github.com/your-repo/peatsense/issues)
- Email: support@peatsense.org

**Field Deployment:**
- Contact PM.Haze coordinator: [contact info]
- WhatsApp support group: [invite link]

**Emergency:**
- For urgent sensor failures during fire season, contact PM.Haze emergency line

---

**Last Updated**: January 2026  
**Version**: 1.0  
**Tested on**: Windows 11, Ubuntu 22.04, macOS Sonoma
