# ✅ AeroGuardians - Deployment Checklist

## 📋 Pre-Deployment Checklist

### 🔧 Software Setup
- [ ] Python 3.8+ installed and working
- [ ] Arduino IDE installed
- [ ] Git installed (optional, for version control)

### 📦 Python Dependencies
- [ ] Run: `pip install -r requirements.txt`
- [ ] Verify no errors during installation
- [ ] Test imports: `python -c "import flask, streamlit, plotly, pandas, sklearn"`

### 🌐 Network Configuration
- [ ] Computer connected to WiFi
- [ ] WiFi is 2.4GHz (ESP32 requirement)
- [ ] Computer IP address noted (run `ipconfig`)
- [ ] Windows Firewall allows port 5000 (or temporarily disabled for testing)

### 🔌 Hardware Setup
- [ ] ESP32 board available
- [ ] GP2Y1014 dust sensor connected
- [ ] SGP30 air quality sensor connected
- [ ] MCP9808 temperature sensor connected
- [ ] OLED display connected (optional but recommended)
- [ ] Buzzer connected (optional)
- [ ] USB cable for programming

---

## 🚀 ESP32 Configuration Checklist

### Step 1: Open Arduino IDE
- [ ] Arduino IDE is open
- [ ] ESP32 board support installed
- [ ] Correct board selected: Tools → Board → ESP32 Dev Module
- [ ] Correct COM port selected: Tools → Port

### Step 2: Install Required Libraries
- [ ] Adafruit_SGP30
- [ ] Adafruit_MCP9808
- [ ] U8x8lib (for OLED)
- [ ] WiFi (built-in)
- [ ] HTTPClient (built-in)

### Step 3: Configure Code
Open `esp32_sensor_code.ino` and update:

- [ ] Line 12: WiFi name
  ```cpp
  #define STASSID "YourActualWiFiName"
  ```

- [ ] Line 13: WiFi password
  ```cpp
  #define STAPSK  "YourActualPassword"
  ```

- [ ] Line 19: Your computer's IP address
  ```cpp
  const char* serverName = "http://192.168.1.XXX:5000/api/data";
  ```
  Replace `192.168.1.XXX` with your actual IP from `ipconfig`

### Step 4: Upload to ESP32
- [ ] Click "Verify" button - should compile without errors
- [ ] Click "Upload" button
- [ ] Wait for "Done uploading" message
- [ ] Open Serial Monitor (Ctrl+Shift+M)
- [ ] Set baud rate to 115200
- [ ] Press ESP32 reset button

### Step 5: Verify ESP32 is Working
In Serial Monitor, you should see:
- [ ] "Connecting to: YourWiFiName"
- [ ] "✓ WiFi Connected!"
- [ ] "IP Address: ..."
- [ ] "✓ SGP30 sensor initialized"
- [ ] "✓ MCP9808 sensor initialized"
- [ ] "Ready to send data!"

---

## 🖥️ Backend Setup Checklist

### Step 1: Test Flask Installation
- [ ] Open terminal/PowerShell
- [ ] Navigate to project folder: `cd C:\Users\Mayan\Downloads\aero-guardians-master`
- [ ] Test: `python --version` (should be 3.8+)
- [ ] Test: `python -c "import flask; print('OK')"`

### Step 2: Start Flask Backend
Choose ONE method:

**Method A: Batch File (Easy)**
- [ ] Double-click `start_backend.bat`
- [ ] New window opens
- [ ] Shows "Running on http://127.0.0.1:5000"
- [ ] Keep this window open

**Method B: Manual**
- [ ] Open PowerShell
- [ ] Run: `python app.py`
- [ ] See "Running on http://127.0.0.1:5000"
- [ ] Keep this window open

### Step 3: Verify Backend is Running
- [ ] Open browser
- [ ] Go to: http://127.0.0.1:5000
- [ ] Should see: "Server is running"

---

## 📊 Dashboard Setup Checklist

### Step 1: Open New Terminal
- [ ] Open NEW PowerShell window (don't close Flask window)
- [ ] Navigate to same folder

### Step 2: Start Dashboard
Choose ONE method:

**Method A: Batch File (Easy)**
- [ ] Double-click `start_dashboard.bat`
- [ ] Browser opens automatically
- [ ] Dashboard appears

**Method B: Manual**
- [ ] Run: `streamlit run sensor_dashboard.py`
- [ ] Browser opens at http://localhost:8501
- [ ] Dashboard appears

### Step 3: Verify Dashboard
- [ ] Dashboard loads without errors
- [ ] Shows "AeroGuardians Sensor Dashboard" header
- [ ] Sidebar controls visible
- [ ] May show "Waiting for sensor data" (normal if ESP32 not sending yet)

---

## 🧪 Testing Checklist

### Without Hardware (Simulated Data)
- [ ] Open third terminal
- [ ] Run: `python test_api.py`
- [ ] Choose option 2 (multiple readings)
- [ ] Enter 20 readings
- [ ] Watch dashboard populate with data
- [ ] Verify graphs appear
- [ ] Check AI insights appear

### With ESP32 Hardware
- [ ] ESP32 powered on
- [ ] Serial Monitor shows "✓ SUCCESS! Response Code: 200"
- [ ] Flask terminal shows "POST /api/data 200"
- [ ] Dashboard "Current Readings" update
- [ ] Graphs populate with real data
- [ ] AI insights appear after ~10 readings

---

## 🔍 Verification Checklist

### ESP32 Verification
- [ ] OLED shows current readings (if connected)
- [ ] Serial Monitor shows successful POST messages
- [ ] No "SEND FAIL" errors
- [ ] WiFi connection stable

### Backend Verification
- [ ] Flask shows POST requests: `127.0.0.1 - - [...] "POST /api/data HTTP/1.1" 200`
- [ ] File created: `data/sensor_log.csv`
- [ ] CSV file grows with new readings
- [ ] Can access: http://127.0.0.1:5000/api/latest-sensor

### Dashboard Verification
- [ ] Real-time metrics display current values
- [ ] Metrics update every 5-10 seconds
- [ ] All 4 graph tabs work
- [ ] AI Insights section shows analysis
- [ ] Risk Level displayed correctly
- [ ] Historical Statistics show trends

---

## 🎯 First-Time Run Checklist

### Run in This Order:

1. **Start Flask Backend**
   - [ ] Terminal 1: `python app.py`
   - [ ] Wait for "Running on..." message

2. **Start Dashboard**
   - [ ] Terminal 2: `streamlit run sensor_dashboard.py`
   - [ ] Wait for browser to open

3. **Test API (Optional)**
   - [ ] Terminal 3: `python test_api.py`
   - [ ] Send test data to populate dashboard

4. **Power ESP32**
   - [ ] Connect ESP32 to power/USB
   - [ ] Open Serial Monitor
   - [ ] Verify WiFi connection
   - [ ] Verify data sending

5. **Monitor Dashboard**
   - [ ] Click "Refresh Data" or enable Auto-refresh
   - [ ] Watch data appear
   - [ ] Explore different graph tabs
   - [ ] Read AI insights

---

## 🐛 Troubleshooting Checklist

### If ESP32 Won't Connect to WiFi
- [ ] WiFi name spelled exactly right (case-sensitive)
- [ ] WiFi password correct
- [ ] WiFi is 2.4GHz not 5GHz
- [ ] ESP32 within range of router
- [ ] Restart ESP32 and try again

### If ESP32 Can't Send Data
- [ ] Computer IP address is correct in code
- [ ] Both devices on same network
- [ ] Flask is running
- [ ] Firewall temporarily disabled (for testing)
- [ ] Port 5000 not used by another app

### If Dashboard Shows Error
- [ ] Flask backend is running
- [ ] No typos in URL (should be http://127.0.0.1:5000)
- [ ] Run `pip install -r requirements.txt` again
- [ ] Check Python version is 3.8+

### If No Data Appears
- [ ] ESP32 Serial Monitor shows "SUCCESS"
- [ ] Flask shows POST requests
- [ ] File exists: `data/sensor_log.csv`
- [ ] Click "Refresh Data" button
- [ ] Try test script: `python test_api.py`

---

## 📈 Success Criteria

You've successfully deployed when:

- [X] **ESP32 Status**
  - WiFi connected
  - Sensors reading
  - POST requests succeeding
  - Serial shows "✓ SUCCESS! Response Code: 200"

- [X] **Backend Status**
  - Flask running on port 5000
  - Receiving POST requests
  - CSV file growing
  - No error messages

- [X] **Dashboard Status**
  - Displaying real-time metrics
  - Graphs updating
  - AI insights appearing
  - Risk level shown

- [X] **Data Flow**
  - ESP32 → Flask → CSV → Dashboard → Browser
  - Complete loop working
  - Data updates every 5-10 seconds

---

## 🎉 Post-Deployment Checklist

### Optimization
- [ ] Adjust ESP32 transmission interval if needed (default: 5s)
- [ ] Configure dashboard auto-refresh
- [ ] Set up data backup/export
- [ ] Customize risk thresholds for your environment

### Documentation
- [ ] Bookmark dashboard URL: http://localhost:8501
- [ ] Note computer IP address for future uploads
- [ ] Document any custom threshold changes
- [ ] Save sensor calibration notes

### Monitoring
- [ ] Check CSV file size periodically
- [ ] Monitor ESP32 WiFi stability
- [ ] Review AI insights for patterns
- [ ] Validate sensor accuracy

### Maintenance
- [ ] Weekly: Review collected data
- [ ] Monthly: Restart ESP32 for sensor recalibration
- [ ] As needed: Clean dust sensor
- [ ] As needed: Update threshold values

---

## 📞 Quick Reference

| What | Command |
|------|---------|
| **Start Backend** | `python app.py` or `start_backend.bat` |
| **Start Dashboard** | `streamlit run sensor_dashboard.py` or `start_dashboard.bat` |
| **Test API** | `python test_api.py` |
| **Get IP** | `ipconfig` (Windows) |
| **View Logs** | Check Flask terminal window |
| **View Data** | Open `data/sensor_log.csv` |

---

## ✅ Final Pre-Launch Check

Right before you power on for the first time:

1. [ ] Flask terminal shows "Running on http://127.0.0.1:5000"
2. [ ] Dashboard open in browser at http://localhost:8501
3. [ ] ESP32 code uploaded with correct WiFi + IP
4. [ ] Serial Monitor open at 115200 baud
5. [ ] All sensor wires connected properly
6. [ ] USB cable secure
7. [ ] Ready to see magic happen! 🎉

---

**You're all set! Power on your ESP32 and watch the data flow! 🚀**

For help, see:
- QUICK_REFERENCE.md - Common commands
- SETUP_INSTRUCTIONS.md - Detailed guide
- ARCHITECTURE.md - How it works
- PROJECT_SUMMARY.md - Feature overview
