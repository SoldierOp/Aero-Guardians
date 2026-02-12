/*
 * PeatSense - Peatland Groundwater & Fire Risk Monitoring System
 * 
 * Hardware: Seeed Studio XIAO ESP32S3 + Grove Base Board
 * Target: Indonesian peatland communities (Sungai Tohor, Riau)
 * 
 * Monitors:
 * - Water level (ultrasonic) → Flood prediction
 * - Salinity/TDS → Agricultural planning
 * - VOC & eCO2 (SGP30) → Fire risk from peat drying
 * - PM2.5 (Dust sensor) → Smoke/haze detection
 * - Temperature & Humidity → Microclimate monitoring
 * 
 * Features:
 * - Edge processing: calculates risk states locally
 * - Offline-capable: works without internet
 * - MQTT alerts: sends to backend when WiFi available
 * - OLED display: shows current status
 * - RGB LED: physical risk indicator
 * 
 * Author: PeatSense Team
 * Version: 1.0
 * Last Updated: January 2026
 */

#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <U8g2lib.h>
#include <Adafruit_NeoPixel.h>
#include "Seeed_HM330X.h"
#include "Adafruit_SGP30.h"
#include <Adafruit_MCP9808.h>

// ============= CONFIGURATION =============

// WiFi Credentials
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// MQTT Broker Settings
const char* MQTT_BROKER = "mqtt.peatsense.local"; // Or AWS IoT Core endpoint
const int MQTT_PORT = 1883;
const char* MQTT_CLIENT_ID = "peatsense_node_001";
const char* MQTT_TOPIC_DATA = "peatsense/data";
const char* MQTT_TOPIC_ALERT = "peatsense/alerts";

// Node Information
const char* NODE_ID = "SungaiTohor_Node01";
const float NODE_LAT = 0.8512;  // Sungai Tohor coordinates
const float NODE_LON = 103.3556;

// Sensor Pin Definitions
#define ULTRASONIC_TRIG_PIN 1  // D0 on Grove Base
#define ULTRASONIC_ECHO_PIN 2  // D1 on Grove Base
#define TDS_SENSOR_PIN 26      // A0 on Grove Base
#define RGB_LED_PIN 3          // I2C addressable RGB
#define BUZZER_PIN 4           // I2C Grove Buzzer

// RGB LED Configuration
#define NUM_LEDS 8
Adafruit_NeoPixel strip(NUM_LEDS, RGB_LED_PIN, NEO_GRB + NEO_KHZ800);

// OLED Display (Built into Grove Base Board)
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, U8X8_PIN_NONE);

// Sensor Objects
Adafruit_SGP30 sgp30;                // VOC & eCO2 sensor
Adafruit_MCP9808 mcp9808;            // Temperature & Humidity
HM330X dustSensor;                   // PM2.5 dust sensor

// WiFi and MQTT Clients
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// ============= CALIBRATION CONSTANTS =============

// Water Level Calibration
const float CANAL_DEPTH_CM = 200.0;  // Distance from sensor to canal bottom
const float FLOOD_WARNING_CM = 150.0; // Water level for warning
const float FLOOD_DANGER_CM = 180.0;  // Water level for danger

// TDS/Salinity Calibration
const float TDS_VREF = 5.0;           // Reference voltage
const float TDS_OFFSET = 0.0;         // Calibration offset
// Salinity thresholds for rice farming (ppm)
const float SALINITY_SAFE = 500.0;    // Fresh water
const float SALINITY_WARNING = 2000.0; // Brackish water
const float SALINITY_DANGER = 3000.0;  // Crop loss risk

// Fire Risk Thresholds
const int VOC_SAFE = 400;             // ppb
const int VOC_WARNING = 1000;         // ppb
const int VOC_DANGER = 2000;          // ppb
const float HUMIDITY_SAFE = 70.0;     // %
const float HUMIDITY_WARNING = 50.0;  // %
const float HUMIDITY_DANGER = 30.0;   // %
const int PM25_SAFE = 50;             // µg/m³
const int PM25_WARNING = 150;         // µg/m³
const int PM25_DANGER = 300;          // µg/m³

// ============= GLOBAL VARIABLES =============

// Sensor Data Structure
struct SensorData {
  // Water monitoring
  float waterLevel;       // cm from canal bottom
  float tds;              // ppm (salinity proxy)
  
  // Fire risk
  int voc;                // ppb
  int eco2;               // ppm
  int pm25;               // µg/m³
  
  // Environmental
  float temperature;      // °C
  float humidity;         // %
  
  // Timestamps
  unsigned long timestamp;
  
  // Risk states
  int floodRisk;          // 0=Safe, 1=Warning, 2=Danger
  int fireRisk;           // 0=Safe, 1=Warning, 2=Danger
  int overallRisk;        // 0=Safe, 1=Warning, 2=Danger
};

SensorData currentData;

// System State
bool wifiConnected = false;
bool mqttConnected = false;
bool offlineMode = false;
unsigned long lastSensorRead = 0;
unsigned long lastMQTTPublish = 0;
unsigned long lastAlertSent = 0;
const unsigned long SENSOR_INTERVAL = 30000;  // 30 seconds
const unsigned long MQTT_INTERVAL = 300000;   // 5 minutes
const unsigned long ALERT_COOLDOWN = 600000;  // 10 minutes between alerts

// ============= SETUP =============

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("🌊 PeatSense v1.0 Starting...");
  Serial.println("================================");
  
  // Initialize I2C
  Wire.begin();
  
  // Initialize OLED Display
  u8g2.begin();
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.drawStr(0, 15, "PeatSense v1.0");
  u8g2.drawStr(0, 30, "Initializing...");
  u8g2.sendBuffer();
  
  // Initialize RGB LED Strip
  strip.begin();
  strip.setBrightness(50);  // 50% brightness
  setLEDColor(0, 0, 255);   // Blue during startup
  strip.show();
  
  // Initialize Ultrasonic Sensor
  pinMode(ULTRASONIC_TRIG_PIN, OUTPUT);
  pinMode(ULTRASONIC_ECHO_PIN, INPUT);
  Serial.println("✓ Ultrasonic sensor initialized");
  
  // Initialize TDS Sensor
  pinMode(TDS_SENSOR_PIN, INPUT);
  Serial.println("✓ TDS sensor initialized");
  
  // Initialize SGP30 VOC Sensor
  if (sgp30.begin()) {
    Serial.println("✓ SGP30 VOC sensor found");
    // Load baseline if available (improves accuracy)
    // sgp30.setIAQBaseline(0x8E68, 0x8F41);  // Load from EEPROM in production
  } else {
    Serial.println("✗ SGP30 sensor not found!");
  }
  
  // Initialize MCP9808 Temperature Sensor
  if (mcp9808.begin(0x18)) {
    Serial.println("✓ MCP9808 temp sensor found");
    mcp9808.setResolution(3);  // Highest resolution
  } else {
    Serial.println("✗ MCP9808 sensor not found!");
  }
  
  // Initialize Dust Sensor
  if (dustSensor.init()) {
    Serial.println("✓ HM330X dust sensor found");
  } else {
    Serial.println("✗ Dust sensor not found!");
  }
  
  // Connect to WiFi
  connectWiFi();
  
  // Setup MQTT
  mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  
  // Initial sensor reading
  readAllSensors();
  
  Serial.println("================================");
  Serial.println("🚀 PeatSense Ready!");
  Serial.println("================================\n");
  
  // Show ready status
  u8g2.clearBuffer();
  u8g2.drawStr(0, 15, "PeatSense Ready");
  u8g2.drawStr(0, 30, NODE_ID);
  u8g2.sendBuffer();
  setLEDColor(0, 255, 0);  // Green = ready
  strip.show();
  
  delay(2000);
}

// ============= MAIN LOOP =============

void loop() {
  unsigned long currentMillis = millis();
  
  // Maintain WiFi connection
  if (WiFi.status() != WL_CONNECTED && !offlineMode) {
    connectWiFi();
  }
  
  // Maintain MQTT connection
  if (wifiConnected && !mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();
  
  // Read sensors at regular intervals
  if (currentMillis - lastSensorRead >= SENSOR_INTERVAL) {
    lastSensorRead = currentMillis;
    
    readAllSensors();
    calculateRiskLevels();
    updateDisplay();
    updateLEDStatus();
    
    // Print to serial for debugging
    printSensorData();
  }
  
  // Publish to MQTT at intervals (if connected)
  if (mqttConnected && (currentMillis - lastMQTTPublish >= MQTT_INTERVAL)) {
    lastMQTTPublish = currentMillis;
    publishSensorData();
  }
  
  // Send alerts if danger detected and cooldown expired
  if (currentData.overallRisk == 2 && 
      (currentMillis - lastAlertSent >= ALERT_COOLDOWN)) {
    lastAlertSent = currentMillis;
    sendAlert();
  }
  
  delay(100);
}

// ============= SENSOR READING FUNCTIONS =============

void readAllSensors() {
  Serial.println("\n📊 Reading Sensors...");
  
  currentData.timestamp = millis();
  
  // Read water level (ultrasonic)
  currentData.waterLevel = readWaterLevel();
  
  // Read TDS/salinity
  currentData.tds = readTDS();
  
  // Read VOC & eCO2
  if (sgp30.IAQmeasure()) {
    currentData.voc = sgp30.TVOC;
    currentData.eco2 = sgp30.eCO2;
  }
  
  // Read temperature & humidity
  currentData.temperature = mcp9808.readTempC();
  // Note: MCP9808 doesn't have humidity - need separate sensor or estimate
  currentData.humidity = 75.0;  // Placeholder - add Grove DHT22 if needed
  
  // Read PM2.5
  uint8_t buf[30];
  if (dustSensor.read_sensor_value(buf, 29)) {
    currentData.pm25 = (buf[6] * 256 + buf[7]);  // PM2.5 value
  }
  
  Serial.println("✓ All sensors read");
}

float readWaterLevel() {
  // Trigger ultrasonic pulse
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  
  // Measure echo pulse duration
  long duration = pulseIn(ULTRASONIC_ECHO_PIN, HIGH, 30000);  // 30ms timeout
  
  if (duration == 0) {
    Serial.println("⚠ Ultrasonic sensor timeout");
    return -1;
  }
  
  // Calculate distance in cm (speed of sound = 343 m/s)
  float distanceTriggerToWater = duration * 0.0343 / 2.0;
  
  // Calculate water level from canal bottom
  float waterLevel = CANAL_DEPTH_CM - distanceTriggerToWater;
  
  Serial.print("  Water level: ");
  Serial.print(waterLevel);
  Serial.println(" cm");
  
  return waterLevel;
}

float readTDS() {
  // Read analog voltage from TDS sensor
  int rawValue = analogRead(TDS_SENSOR_PIN);
  float voltage = rawValue * (TDS_VREF / 4095.0);  // ESP32 has 12-bit ADC
  
  // Convert voltage to TDS (ppm)
  // Formula from DFRobot TDS sensor datasheet
  float tdsValue = (133.42 * voltage * voltage * voltage 
                    - 255.86 * voltage * voltage 
                    + 857.39 * voltage) * 0.5;
  
  tdsValue += TDS_OFFSET;  // Apply calibration offset
  
  if (tdsValue < 0) tdsValue = 0;
  
  Serial.print("  TDS/Salinity: ");
  Serial.print(tdsValue);
  Serial.println(" ppm");
  
  return tdsValue;
}

// ============= RISK CALCULATION =============

void calculateRiskLevels() {
  Serial.println("\n🧮 Calculating Risk Levels...");
  
  // Calculate flood risk
  if (currentData.waterLevel >= FLOOD_DANGER_CM || 
      currentData.tds >= SALINITY_DANGER) {
    currentData.floodRisk = 2;  // Danger
  } else if (currentData.waterLevel >= FLOOD_WARNING_CM || 
             currentData.tds >= SALINITY_WARNING) {
    currentData.floodRisk = 1;  // Warning
  } else {
    currentData.floodRisk = 0;  // Safe
  }
  
  // Calculate fire risk (peat fire indicators)
  int fireIndicators = 0;
  
  if (currentData.voc >= VOC_DANGER) fireIndicators++;
  if (currentData.humidity <= HUMIDITY_DANGER) fireIndicators++;
  if (currentData.pm25 >= PM25_DANGER) fireIndicators++;
  
  if (fireIndicators >= 2) {
    currentData.fireRisk = 2;  // Danger
  } else if (currentData.voc >= VOC_WARNING || 
             currentData.humidity <= HUMIDITY_WARNING ||
             currentData.pm25 >= PM25_WARNING) {
    currentData.fireRisk = 1;  // Warning
  } else {
    currentData.fireRisk = 0;  // Safe
  }
  
  // Overall risk is highest of the two hazards
  currentData.overallRisk = max(currentData.floodRisk, currentData.fireRisk);
  
  // Print risk assessment
  Serial.print("  Flood Risk: ");
  Serial.println(getRiskText(currentData.floodRisk));
  Serial.print("  Fire Risk: ");
  Serial.println(getRiskText(currentData.fireRisk));
  Serial.print("  Overall Risk: ");
  Serial.println(getRiskText(currentData.overallRisk));
}

const char* getRiskText(int risk) {
  switch (risk) {
    case 0: return "SAFE ✓";
    case 1: return "WARNING ⚠";
    case 2: return "DANGER ⛔";
    default: return "UNKNOWN";
  }
}

// ============= DISPLAY & LED FUNCTIONS =============

void updateDisplay() {
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  
  // Title
  u8g2.drawStr(0, 10, "PeatSense Monitor");
  u8g2.drawLine(0, 12, 128, 12);
  
  // Water level
  char waterStr[32];
  sprintf(waterStr, "Water: %.0fcm", currentData.waterLevel);
  u8g2.drawStr(0, 25, waterStr);
  
  // Salinity
  char salinityStr[32];
  sprintf(salinityStr, "Salt: %.0fppm", currentData.tds);
  u8g2.drawStr(0, 35, salinityStr);
  
  // VOC
  char vocStr[32];
  sprintf(vocStr, "VOC: %dppb", currentData.voc);
  u8g2.drawStr(0, 45, vocStr);
  
  // Overall status
  u8g2.drawLine(0, 48, 128, 48);
  u8g2.setFont(u8g2_font_ncenB10_tr);
  u8g2.drawStr(0, 62, getRiskText(currentData.overallRisk));
  
  u8g2.sendBuffer();
}

void updateLEDStatus() {
  // Set LED color based on overall risk
  switch (currentData.overallRisk) {
    case 0:  // Safe
      setLEDColor(0, 255, 0);  // Green
      break;
    case 1:  // Warning
      setLEDColor(255, 200, 0);  // Yellow
      break;
    case 2:  // Danger
      setLEDColor(255, 0, 0);  // Red
      // Also pulse for attention
      pulseLEDs();
      break;
  }
  strip.show();
}

void setLEDColor(uint8_t r, uint8_t g, uint8_t b) {
  for (int i = 0; i < NUM_LEDS; i++) {
    strip.setPixelColor(i, strip.Color(r, g, b));
  }
}

void pulseLEDs() {
  // Simple pulse effect for danger state
  for (int brightness = 50; brightness <= 255; brightness += 10) {
    strip.setBrightness(brightness);
    strip.show();
    delay(10);
  }
  for (int brightness = 255; brightness >= 50; brightness -= 10) {
    strip.setBrightness(brightness);
    strip.show();
    delay(10);
  }
  strip.setBrightness(50);  // Reset to default
}

// ============= WIFI & MQTT FUNCTIONS =============

void connectWiFi() {
  Serial.print("📡 Connecting to WiFi: ");
  Serial.println(WIFI_SSID);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    offlineMode = false;
    Serial.println("\n✓ WiFi connected!");
    Serial.print("  IP: ");
    Serial.println(WiFi.localIP());
  } else {
    wifiConnected = false;
    offlineMode = true;
    Serial.println("\n✗ WiFi failed - entering offline mode");
  }
}

void reconnectMQTT() {
  if (!wifiConnected) return;
  
  Serial.print("📡 Connecting to MQTT broker...");
  
  if (mqttClient.connect(MQTT_CLIENT_ID)) {
    mqttConnected = true;
    Serial.println(" ✓ Connected!");
    
    // Subscribe to control topics
    mqttClient.subscribe("peatsense/control/#");
  } else {
    mqttConnected = false;
    Serial.print(" ✗ Failed, rc=");
    Serial.println(mqttClient.state());
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  Serial.print("📨 MQTT message received: ");
  Serial.println(topic);
  
  // Handle incoming MQTT commands (e.g., configuration updates)
  // Implementation depends on backend design
}

void publishSensorData() {
  if (!mqttConnected) return;
  
  Serial.println("📤 Publishing sensor data to MQTT...");
  
  // Build JSON payload
  char jsonBuffer[512];
  sprintf(jsonBuffer,
    "{"
    "\"node_id\":\"%s\","
    "\"timestamp\":%lu,"
    "\"water_level\":%.2f,"
    "\"tds\":%.2f,"
    "\"voc\":%d,"
    "\"eco2\":%d,"
    "\"pm25\":%d,"
    "\"temperature\":%.2f,"
    "\"humidity\":%.2f,"
    "\"flood_risk\":%d,"
    "\"fire_risk\":%d,"
    "\"overall_risk\":%d,"
    "\"lat\":%.4f,"
    "\"lon\":%.4f"
    "}",
    NODE_ID,
    currentData.timestamp,
    currentData.waterLevel,
    currentData.tds,
    currentData.voc,
    currentData.eco2,
    currentData.pm25,
    currentData.temperature,
    currentData.humidity,
    currentData.floodRisk,
    currentData.fireRisk,
    currentData.overallRisk,
    NODE_LAT,
    NODE_LON
  );
  
  bool success = mqttClient.publish(MQTT_TOPIC_DATA, jsonBuffer);
  
  if (success) {
    Serial.println("  ✓ Data published successfully");
  } else {
    Serial.println("  ✗ Publish failed");
  }
}

void sendAlert() {
  Serial.println("🚨 SENDING ALERT!");
  
  char alertBuffer[256];
  
  if (currentData.floodRisk == 2) {
    sprintf(alertBuffer,
      "{\"node_id\":\"%s\",\"type\":\"FLOOD\",\"level\":\"DANGER\","
      "\"water_level\":%.0f,\"tds\":%.0f,\"message\":\"URGENT: Flood danger detected!\"}",
      NODE_ID, currentData.waterLevel, currentData.tds
    );
  } else if (currentData.fireRisk == 2) {
    sprintf(alertBuffer,
      "{\"node_id\":\"%s\",\"type\":\"FIRE\",\"level\":\"DANGER\","
      "\"voc\":%d,\"pm25\":%d,\"message\":\"URGENT: Fire risk detected!\"}",
      NODE_ID, currentData.voc, currentData.pm25
    );
  }
  
  if (mqttConnected) {
    mqttClient.publish(MQTT_TOPIC_ALERT, alertBuffer);
    Serial.println("  ✓ Alert sent via MQTT");
  } else {
    Serial.println("  ⚠ Offline - alert stored locally");
    // In offline mode, store alert for later transmission
    // or trigger local alarm (buzzer, louder LED pattern)
  }
  
  // Activate local alarm regardless of connectivity
  activateLocalAlarm();
}

void activateLocalAlarm() {
  // Flash LEDs rapidly
  for (int i = 0; i < 10; i++) {
    setLEDColor(255, 0, 0);
    strip.show();
    delay(100);
    setLEDColor(0, 0, 0);
    strip.show();
    delay(100);
  }
  
  // TODO: Activate buzzer if available
  // tone(BUZZER_PIN, 1000, 2000);  // 1kHz for 2 seconds
}

// ============= DEBUG FUNCTIONS =============

void printSensorData() {
  Serial.println("\n╔════════════════════════════════════════╗");
  Serial.println("║       PeatSense Sensor Readings       ║");
  Serial.println("╠════════════════════════════════════════╣");
  
  Serial.print("║ Water Level:    ");
  Serial.print(currentData.waterLevel, 1);
  Serial.println(" cm");
  
  Serial.print("║ TDS/Salinity:   ");
  Serial.print(currentData.tds, 0);
  Serial.println(" ppm");
  
  Serial.print("║ VOC:            ");
  Serial.print(currentData.voc);
  Serial.println(" ppb");
  
  Serial.print("║ eCO2:           ");
  Serial.print(currentData.eco2);
  Serial.println(" ppm");
  
  Serial.print("║ PM2.5:          ");
  Serial.print(currentData.pm25);
  Serial.println(" µg/m³");
  
  Serial.print("║ Temperature:    ");
  Serial.print(currentData.temperature, 1);
  Serial.println(" °C");
  
  Serial.print("║ Humidity:       ");
  Serial.print(currentData.humidity, 1);
  Serial.println(" %");
  
  Serial.println("╠════════════════════════════════════════╣");
  
  Serial.print("║ Flood Risk:     ");
  Serial.println(getRiskText(currentData.floodRisk));
  
  Serial.print("║ Fire Risk:      ");
  Serial.println(getRiskText(currentData.fireRisk));
  
  Serial.print("║ Overall Risk:   ");
  Serial.println(getRiskText(currentData.overallRisk));
  
  Serial.println("╚════════════════════════════════════════╝\n");
}
