/*
 * PeatGuard Pro - WiFi IoT Integration
 * Sensors: SGP30 (VOC/eCO2) + MCP9808 (Temp) + PMS5003 (PM2.5) + TDS
 * Connectivity: WiFi + HTTP POST to Backend API
 * Output: OLED Display + Buzzer + Cloud Dashboard
 */

#include <Wire.h>
#include <Adafruit_SGP30.h>
#include <Adafruit_MCP9808.h>
#include <U8g2lib.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ============= WiFi Configuration =============
const char* ssid = "YOUR_WIFI_SSID";           // CHANGE THIS
const char* password = "YOUR_WIFI_PASSWORD";   // CHANGE THIS

// ============= Backend API Configuration =============
const char* apiEndpoint = "http://YOUR_BACKEND_IP:8000/api/readings";  // CHANGE THIS
// Example: "http://192.168.1.100:8000/api/readings"

// ============= Node Configuration =============
const char* nodeId = "PeatGuard_Node01";
const float nodeLat = 0.125;  // Your GPS coordinates
const float nodeLon = 103.123;

// OLED Display (built-in on XIAO base board)
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

// I2C Hub
#define TCAADDR 0x70

// Sensors
Adafruit_SGP30 sgp;
Adafruit_MCP9808 tempsensor;

// PMS5003 UART
#define PMS_RX 44
#define PMS_TX 43
HardwareSerial pmsSerial(1);

// Analog Sensors
#define TDS_PIN 1

// Buzzer (built-in on XIAO base board)
#define BUZZER_PIN A3

// Sensor data storage
uint16_t pm25 = 0, pm10 = 0, pm1_0 = 0;
int voc = 0, eco2 = 0;
float temp = 0;
int tdsRaw = 0;
float tdsValue = 0;
bool waterPresent = false;

// WiFi status
bool wifiConnected = false;

// Select I2C hub channel
void tcaselect(uint8_t i) {
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

// Buzzer alert function
void buzzerAlert(int beeps) {
  for(int i = 0; i < beeps; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(100);
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  }
}

// Connect to WiFi
void connectWiFi() {
  Serial.println("\n--- Connecting to WiFi ---");
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if(WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println("\n✅ WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    buzzerAlert(2); // 2 beeps for WiFi success
  } else {
    wifiConnected = false;
    Serial.println("\n❌ WiFi Connection Failed");
    Serial.println("⚠️ Running in offline mode");
  }
}

// Calculate risk levels
int calculateFireRisk() {
  // Fire risk based on VOC, PM2.5, and temperature
  int risk = 0;
  
  if(voc > 100 || pm25 > 150 || temp > 40) {
    risk = 2; // DANGER
  } else if(voc > 50 || pm25 > 75 || temp > 35) {
    risk = 1; // WARNING
  }
  
  return risk;
}

int calculateFloodRisk() {
  // Flood risk based on water presence and TDS
  // In real deployment, you'd use water level sensor
  if(tdsRaw > 1000) return 2; // High water
  if(tdsRaw > 500) return 1;  // Medium water
  return 0; // Low/no water
}

// Send data to backend
void sendDataToBackend() {
  if(!wifiConnected) {
    Serial.println("⚠️ WiFi not connected - skipping upload");
    return;
  }
  
  HTTPClient http;
  http.begin(apiEndpoint);
  http.addHeader("Content-Type", "application/json");
  
  // Create JSON payload
  StaticJsonDocument<512> doc;
  
  doc["node_id"] = nodeId;
  doc["timestamp"] = (long)(millis() / 1000);
  doc["water_level"] = tdsRaw / 10.0;  // Proxy from TDS
  doc["water_present"] = waterPresent ? 1 : 0;
  doc["tds"] = tdsValue;
  doc["voc"] = voc;
  doc["eco2"] = eco2;
  doc["pm1_0"] = pm1_0;
  doc["pm25"] = pm25;
  doc["pm10"] = pm10;
  doc["dust_concentration"] = pm25;  // Using PMS data
  doc["temperature"] = temp;
  doc["humidity"] = 70.0;  // Placeholder - add DHT22 if needed
  doc["flood_risk"] = calculateFloodRisk();
  doc["fire_risk"] = calculateFireRisk();
  doc["overall_risk"] = max(calculateFloodRisk(), calculateFireRisk());
  doc["lat"] = nodeLat;
  doc["lon"] = nodeLon;
  
  String jsonPayload;
  serializeJson(doc, jsonPayload);
  
  Serial.println("\n📤 Sending data to backend...");
  Serial.println(jsonPayload);
  
  int httpCode = http.POST(jsonPayload);
  
  if(httpCode > 0) {
    Serial.printf("✅ HTTP Response: %d\n", httpCode);
    if(httpCode == 200) {
      buzzerAlert(1); // Success beep
    }
  } else {
    Serial.printf("❌ HTTP Error: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Wire.begin();
  
  // Initialize buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Initialize OLED
  u8g2.begin();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  
  // Boot screen
  u8g2.clearBuffer();
  u8g2.drawStr(0, 15, "PeatGuard Pro");
  u8g2.drawStr(0, 35, "IoT Edition");
  u8g2.sendBuffer();
  
  buzzerAlert(1);
  
  Serial.println("\n=================================");
  Serial.println("   PeatGuard Pro - IoT System");
  Serial.println("=================================\n");

  // Connect to WiFi
  connectWiFi();

  // Init SGP30 (Channel 0)
  Serial.print("SGP30 VOC Sensor... ");
  tcaselect(0);
  delay(100);
  if (sgp.begin()) {
    Serial.println("✅ OK");
  } else {
    Serial.println("❌ FAILED");
  }

  // Init MCP9808 (Channel 1)
  Serial.print("MCP9808 Temperature... ");
  tcaselect(1);
  delay(100);
  if (tempsensor.begin(0x18)) {
    tempsensor.setResolution(3);
    Serial.println("✅ OK");
  } else {
    Serial.println("❌ FAILED");
  }

  // Init PMS5003
  Serial.print("PMS5003 PM2.5 Sensor... ");
  pmsSerial.begin(9600, SERIAL_8N1, PMS_RX, PMS_TX);
  Serial.println("✅ UART Started");

  // Init TDS
  pinMode(TDS_PIN, INPUT);
  Serial.println("TDS Sensor... ✅ GPIO 1 Ready");

  Serial.println("\n=================================");
  Serial.println("   System Ready - Monitoring");
  Serial.println("=================================\n");
  
  // Ready screen
  u8g2.clearBuffer();
  u8g2.drawStr(0, 20, "System Ready!");
  u8g2.drawStr(0, 40, wifiConnected ? "WiFi: OK" : "WiFi: OFF");
  u8g2.sendBuffer();
  delay(2000);
}

void loop() {
  static unsigned long lastRead = 0;
  static unsigned long lastUpload = 0;
  
  // Read sensors every 3 seconds
  if(millis() - lastRead < 3000) return;
  lastRead = millis();

  Serial.println("\n--- SENSOR READINGS ---");

  // Read SGP30 (VOC/eCO2)
  tcaselect(0);
  delay(50);
  if (sgp.IAQmeasure()) {
    voc = sgp.TVOC;
    eco2 = sgp.eCO2;
    Serial.print("🔥 VOC: ");
    Serial.print(voc);
    Serial.print(" ppb   eCO2: ");
    Serial.print(eco2);
    Serial.println(" ppm");
  }

  // Read Temperature
  tcaselect(1);
  delay(50);
  temp = tempsensor.readTempC();
  Serial.print("🌡️  Temperature: ");
  Serial.print(temp, 1);
  Serial.println(" °C");

  // Read PMS5003 (PM2.5, PM10, PM1.0)
  if (pmsSerial.available() >= 32) {
    if (pmsSerial.read() == 0x42) {
      if (pmsSerial.read() == 0x4d) {
        uint8_t buffer[30];
        pmsSerial.readBytes(buffer, 30);
        pm1_0 = (buffer[2] << 8) | buffer[3];
        pm25 = (buffer[4] << 8) | buffer[5];
        pm10 = (buffer[6] << 8) | buffer[7];
      }
    }
  }
  Serial.print("🔬 PM1.0: ");
  Serial.print(pm1_0);
  Serial.print(" | PM2.5: ");
  Serial.print(pm25);
  Serial.print(" | PM10: ");
  Serial.print(pm10);
  Serial.println(" µg/m³");

  // Read TDS (Water Detection)
  tdsRaw = 0;
  for(int i = 0; i < 10; i++) {
    tdsRaw += analogRead(TDS_PIN);
    delay(5);
  }
  tdsRaw /= 10;
  
  waterPresent = (tdsRaw > 50);
  
  if(waterPresent) {
    float tdsVoltage = tdsRaw * (3.3 / 4095.0);
    tdsValue = (133.42 * tdsVoltage * tdsVoltage * tdsVoltage 
                 - 255.86 * tdsVoltage * tdsVoltage 
                 + 857.39 * tdsVoltage) * 0.5;
  } else {
    tdsValue = 0;
  }
  
  Serial.print("💧 TDS: ");
  Serial.print(tdsValue, 1);
  Serial.print(" ppm (Raw: ");
  Serial.print(tdsRaw);
  Serial.println(waterPresent ? " - Water present)" : " - No water)");

  // Fire Risk Assessment
  int fireRisk = calculateFireRisk();
  String status = "NORMAL";
  
  if(fireRisk == 2) {
    status = "DANGER!";
    buzzerAlert(3);
    Serial.println("🚨 FIRE RISK ALERT!");
  } else if(fireRisk == 1) {
    status = "WARNING";
    buzzerAlert(1);
    Serial.println("⚠️  WARNING - Elevated readings");
  }

  Serial.println("-----------------------");

  // Update OLED Display
  Wire.begin(); // Reset to main I2C bus
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  
  char buf[22];
  
  u8g2.drawStr(0, 10, status.c_str());
  
  sprintf(buf, "T:%.1fC V:%d", temp, voc);
  u8g2.drawStr(0, 25, buf);
  
  sprintf(buf, "PM2.5:%d", pm25);
  u8g2.drawStr(0, 40, buf);
  
  sprintf(buf, waterPresent ? "TDS:%.0f ppm" : "Water: DRY", tdsValue);
  u8g2.drawStr(0, 55, buf);
  
  u8g2.sendBuffer();
  
  // Upload to backend every 15 seconds
  if(millis() - lastUpload > 15000) {
    lastUpload = millis();
    sendDataToBackend();
  }
}
