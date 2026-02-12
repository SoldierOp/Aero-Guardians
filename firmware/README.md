# PeatGuard Firmware

This directory contains the Arduino firmware for PeatGuard Pro monitoring nodes.

## Files

### PeatGuard_Standalone.ino
**Standalone monitoring node** with local display and alerts.

**Features:**
- 4-sensor monitoring (VOC, Temperature, PM2.5, TDS)
- Real-time OLED display showing all readings
- Built-in buzzer alerts (WARNING/DANGER levels)
- Risk assessment algorithm
- No WiFi required - works offline

**Use Case:** Testing, offline deployments, power-constrained scenarios

### PeatGuard_IoT.ino
**IoT-enabled node** with cloud connectivity and remote monitoring.

**Features:**
- All features from Standalone version
- WiFi connectivity
- HTTP POST to backend API every 15 seconds
- JSON payload with sensor data and GPS coordinates
- Cloud dashboard integration
- WhatsApp alert support (via backend)

**Use Case:** Production deployments, remote monitoring, multi-node networks

## Hardware Requirements

- **Microcontroller:** Seeed XIAO ESP32S3
- **Sensors:**
  - SGP30 (VOC/eCO2) on I2C Hub Channel 0
  - MCP9808 (Temperature) on I2C Hub Channel 1
  - PMS5003 (PM2.5) via UART (GPIO43/44)
  - TDS Sensor on GPIO1 (A0)
- **I2C Hub:** TCA9548A at address 0x70
- **Display:** SSD1306 OLED 128x64 (built-in on Grove base board)
- **Alert:** Buzzer on GPIO3 (A3)

## Installation

### 1. Install Arduino Libraries

```bash
# Via Arduino Library Manager:
- Adafruit SGP30 Sensor
- Adafruit MCP9808 Library
- U8g2 (OLED display)
- ArduinoJson (for IoT version)
```

### 2. Configure WiFi (IoT version only)

Edit `PeatGuard_IoT.ino` lines 17-21:

```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* apiEndpoint = "http://YOUR_BACKEND_IP:8000/api/readings";
const char* nodeId = "PeatGuard_Node01";
const float nodeLat = 0.125;  // Your GPS latitude
const float nodeLon = 103.123;  // Your GPS longitude
```

### 3. Upload to Board

1. Select **Board:** Seeed XIAO ESP32S3
2. Select **Port:** (your ESP32S3 COM port)
3. Click **Upload**

### 4. Monitor Serial Output

Open Serial Monitor at **115200 baud** to view:
- Sensor initialization status
- Real-time readings
- WiFi connection status (IoT version)
- API response codes (IoT version)

## Sensor Readings Explanation

### VOC (ppb)
Volatile Organic Compounds - increases with smoke/combustion
- Normal: 0-50 ppb
- Warning: 50-100 ppb
- Danger: >100 ppb

### eCO2 (ppm)
Estimated CO2 - correlates with fire activity
- Normal: 400-450 ppm
- Warning: 450-600 ppm
- Danger: >600 ppm

### Temperature (°C)
Ambient air temperature
- Normal: <35°C
- Warning: 35-40°C
- Danger: >40°C

### PM2.5 (µg/m³)
Particulate matter from smoke
- Normal: 0-75 µg/m³
- Warning: 75-150 µg/m³
- Danger: >150 µg/m³

### TDS (ppm)
Water quality/conductivity (drought indicator)
- Normal: detected in water
- Warning: low readings (drying conditions)
- Danger: no water detected

## Troubleshooting

### WiFi Won't Connect (IoT version)
- Verify SSID and password are correct
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Check router is within range

### Sensors Not Detected
- Verify I2C hub connections
- Check sensor addresses with I2C scanner
- Ensure power supply is adequate (5V 1A minimum)

### HTTP POST Fails
- Verify backend API is running
- Check IP address and port are correct
- Ensure firewall allows connections on port 8000

### No OLED Display
- Verify I2C connection to XIAO base board
- Check U8g2 library is installed
- Try I2C address scan to verify 0x3C

## Wiring Guide

See [docs/hardware/WIRING_GUIDE.md](../docs/hardware/WIRING_GUIDE.md) for detailed connection diagrams.

## License

MIT License - See main repository LICENSE file

## Support

For issues or questions, please open an issue on GitHub or contact the development team.
