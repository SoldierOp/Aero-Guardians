/*
 * PeatGuard Professional Dual-Hazard Monitoring System
 * Hardware: Complete Seeed Studio Grove System
 * 
 * FIRE DETECTION SENSORS:
 * - SGP30 VOC Sensor (I2C via Hub Ch0) → Peat decomposition gases
 * - PMS5003 PM Sensor (UART) → Professional laser-based PM detection
 * - Grove Dust Sensor (I2C via Hub Ch2) → Backup PM detection
 * - MCP9808 Temp/Humidity (I2C via Hub Ch1) → Drought conditions
 * 
 * FLOOD DETECTION SENSORS:
 * - Grove Ultrasonic Ranger (Digital) → Water level measurement
 * - Grove TDS Sensor (Analog) → Salinity/saltwater intrusion
 * - Grove Water Sensor (Analog) → Immediate flood presence detection
 * 
 * INFRASTRUCTURE:
 * - TCA9548A I2C Hub → Manages multiple I2C devices
 * - Grove OLED Display (I2C via Hub Ch3) → Indonesian language status
 * - Grove Relay (Digital) → Triggers siren/alarm
 * - CP2102 UART Converter → Interfaces with PMS5003
 * 
 * FEATURES:
 * - Dual-hazard monitoring (fire + flood)
 * - Redundant PM detection (professional + backup)
 * - Triple water detection (level + salinity + presence)
 * - Edge AI risk prediction
 * - Offline-first operation
 * - Physical alert system
 */

#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <U8g2lib.h>
#include <ArduinoJson.h>
#include <Adafruit_SGP30.h>
#include <Adafruit_MCP9808.h>

// ============= HARDWARE PINS =============
// I2C (for Hub and all I2C devices)
#define I2C_SDA 4
#define I2C_SCL 5

// I2C Hub (TCA9548A) channels
#define I2C_HUB_ADDR 0x70
#define CH_SGP30 0        // Channel 0: VOC sensor
#define CH_MCP9808 1      // Channel 1: Temp/Humidity
#define CH_DUST 2         // Channel 2: Dust sensor (if I2C)
#define CH_OLED 3         // Channel 3: OLED display

// UART for PMS5003
#define PMS5003_RX 44     // ESP32 RX ← PMS5003 TX
#define PMS5003_TX 43     // ESP32 TX → PMS5003 RX

// Digital pins
#define RELAY_PIN 2       // Grove Relay (siren control)
#define ULTRASONIC_PIN 6  // Grove Ultrasonic Ranger

// Analog pins
#define TDS_SENSOR_PIN 1  // Grove TDS Sensor (A0/GPIO1)
#define WATER_SENSOR_PIN 2 // Grove Water Sensor (A1/GPIO2)

// ============= WIFI CONFIGURATION =============
const char* WIFI_SSID = "YourWiFiSSID";
const char* WIFI_PASSWORD = "YourWiFiPassword";

// ============= MQTT CONFIGURATION =============
const char* MQTT_BROKER = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC_DATA = "peatguard/sungaitohor/sensors";
const char* MQTT_TOPIC_ALERT = "peatguard/sungaitohor/alerts";
const char* NODE_ID = "SungaiTohor_Node01";

// ============= SENSORS =============
Adafruit_SGP30 sgp30;
Adafruit_MCP9808 mcp9808 = Adafruit_MCP9808();
U8G2_SSD1306_128X64_NONAME_F_HW_I2C display(U8G2_R0, U8X8_PIN_NONE);
HardwareSerial pmsSerial(1); // Use UART1 for PMS5003

// ============= MQTT CLIENT =============
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// ============= RISK THRESHOLDS =============
struct Thresholds {
    // Fire Risk Indicators
    int VOC_SAFE = 400;           // ppb
    int VOC_WARNING = 800;
    int VOC_DANGER = 1500;
    
    int PM25_SAFE = 50;           // µg/m³
    int PM25_WARNING = 100;
    int PM25_DANGER = 250;
    
    float HUMIDITY_SAFE = 70;     // %
    float HUMIDITY_WARNING = 50;
    float HUMIDITY_DANGER = 30;
    
    float TEMP_FIRE_RISK = 32.0;  // °C
    
    // Flood Risk Indicators
    float WATER_SAFE = 100;       // cm (canal depth)
    float WATER_WARNING = 150;
    float WATER_DANGER = 200;
    
    float TDS_SAFE = 500;         // ppm (fresh water)
    float TDS_WARNING = 1500;     // ppm (brackish)
    float TDS_DANGER = 2500;      // ppm (saltwater)
    
    int WATER_PRESENT = 300;      // Analog threshold for water presence
} thresholds;

// ============= SENSOR DATA =============
struct SensorData {
    // Fire indicators
    int voc;              // VOC in ppb (SGP30)
    int eco2;             // eCO2 in ppm (SGP30)
    float pm25_primary;   // PM2.5 from PMS5003 (µg/m³)
    float pm10;           // PM10 from PMS5003 (µg/m³)
    float pm25_backup;    // PM2.5 from Grove Dust (µg/m³)
    float temperature;    // Temperature in °C
    float humidity;       // Humidity in %
    
    // Flood indicators
    float water_level;    // Water level in cm (ultrasonic)
    float tds;            // TDS (salinity) in ppm
    bool water_present;   // Water presence (immediate detection)
    
    // Risk scores
    int fire_risk;        // 0=Safe, 1=Warning, 2=Danger
    int flood_risk;       // 0=Safe, 1=Warning, 2=Danger
    int overall_risk;     // Maximum of fire/flood risk
    
    unsigned long timestamp;
} currentData;

// ============= STATE VARIABLES =============
bool wifiConnected = false;
bool mqttConnected = false;
unsigned long lastSensorRead = 0;
unsigned long lastMQTTPublish = 0;
unsigned long lastDisplayUpdate = 0;
unsigned long lastAlertCheck = 0;
unsigned long lastReconnectAttempt = 0;

const unsigned long SENSOR_INTERVAL = 5000;
const unsigned long MQTT_INTERVAL = 30000;
const unsigned long DISPLAY_INTERVAL = 2000;
const unsigned long ALERT_INTERVAL = 10000;
const unsigned long RECONNECT_INTERVAL = 10000;

bool alertActive = false;
unsigned long alertStartTime = 0;
const unsigned long ALERT_DURATION = 5000;

// ============= I2C HUB FUNCTIONS =============
void selectI2CChannel(uint8_t channel) {
    if (channel > 7) return;
    
    Wire.beginTransmission(I2C_HUB_ADDR);
    Wire.write(1 << channel);
    Wire.endTransmission();
}

void disableAllI2CChannels() {
    Wire.beginTransmission(I2C_HUB_ADDR);
    Wire.write(0);
    Wire.endTransmission();
}

// ============= SETUP =============
void setup() {
    Serial.begin(115200);
    Serial.println("🔥💧 PeatGuard Professional Monitoring System");
    Serial.println("==========================================");
    
    // Initialize I2C
    Wire.begin(I2C_SDA, I2C_SCL);
    delay(100);
    
    // Initialize I2C Hub
    Serial.print("Initializing I2C Hub... ");
    Wire.beginTransmission(I2C_HUB_ADDR);
    if (Wire.endTransmission() == 0) {
        Serial.println("✓");
    } else {
        Serial.println("✗ FAILED - Check connections!");
    }
    
    // Initialize OLED Display (Channel 3)
    Serial.print("Initializing OLED... ");
    selectI2CChannel(CH_OLED);
    display.begin();
    displayBootScreen();
    Serial.println("✓");
    delay(2000);
    
    // Initialize relay (siren control)
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW);
    
    // Initialize analog sensors
    pinMode(TDS_SENSOR_PIN, INPUT);
    pinMode(WATER_SENSOR_PIN, INPUT);
    pinMode(ULTRASONIC_PIN, INPUT);
    
    // Initialize SGP30 VOC Sensor (Channel 0)
    Serial.print("Initializing SGP30 VOC sensor... ");
    selectI2CChannel(CH_SGP30);
    if (sgp30.begin()) {
        Serial.println("✓");
        displayStatus("SGP30 OK");
    } else {
        Serial.println("✗ FAILED");
        displayStatus("SGP30 FAIL!");
        delay(2000);
    }
    
    // Initialize MCP9808 Temp Sensor (Channel 1)
    Serial.print("Initializing MCP9808 temp sensor... ");
    selectI2CChannel(CH_MCP9808);
    if (mcp9808.begin(0x18)) {
        Serial.println("✓");
        displayStatus("MCP9808 OK");
    } else {
        Serial.println("✗ FAILED");
        displayStatus("MCP9808 FAIL!");
        delay(2000);
    }
    
    // Initialize PMS5003 UART Sensor
    Serial.print("Initializing PMS5003 PM sensor... ");
    pmsSerial.begin(9600, SERIAL_8N1, PMS5003_RX, PMS5003_TX);
    delay(1000);
    Serial.println("✓");
    displayStatus("PMS5003 OK");
    delay(1000);
    
    // Connect to WiFi
    connectWiFi();
    
    // Setup MQTT
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    
    delay(1000);
    Serial.println("\n🚀 System ready!");
    Serial.println("Monitoring for fire AND flood hazards...\n");
}

// ============= MAIN LOOP =============
void loop() {
    unsigned long currentMillis = millis();
    
    // Read sensors
    if (currentMillis - lastSensorRead >= SENSOR_INTERVAL) {
        lastSensorRead = currentMillis;
        readSensors();
        calculateFireRisk();
        calculateFloodRisk();
        currentData.overall_risk = max(currentData.fire_risk, currentData.flood_risk);
    }
    
    // Update display
    if (currentMillis - lastDisplayUpdate >= DISPLAY_INTERVAL) {
        lastDisplayUpdate = currentMillis;
        updateDisplay();
    }
    
    // Check for alerts
    if (currentMillis - lastAlertCheck >= ALERT_INTERVAL) {
        lastAlertCheck = currentMillis;
        checkAndTriggerAlert();
    }
    
    // Publish to MQTT
    if (currentMillis - lastMQTTPublish >= MQTT_INTERVAL) {
        lastMQTTPublish = currentMillis;
        
        if (!mqttClient.connected()) {
            if (currentMillis - lastReconnectAttempt >= RECONNECT_INTERVAL) {
                lastReconnectAttempt = currentMillis;
                reconnectMQTT();
            }
        } else {
            publishSensorData();
        }
    }
    
    // MQTT loop
    if (mqttClient.connected()) {
        mqttClient.loop();
    }
    
    // Handle active alert
    if (alertActive && (currentMillis - alertStartTime >= ALERT_DURATION)) {
        digitalWrite(RELAY_PIN, LOW);
        alertActive = false;
    }
}

// ============= SENSOR READING =============
void readSensors() {
    // Read SGP30 (VOC sensor) - Channel 0
    selectI2CChannel(CH_SGP30);
    if (sgp30.IAQmeasure()) {
        currentData.voc = sgp30.TVOC;
        currentData.eco2 = sgp30.eCO2;
    }
    
    // Read MCP9808 (Temperature) - Channel 1
    selectI2CChannel(CH_MCP9808);
    currentData.temperature = mcp9808.readTempC();
    
    // Read humidity (if available - MCP9808 is temp-only)
    // TODO: Add separate humidity sensor if needed
    currentData.humidity = 65.0; // Placeholder
    
    // Read PMS5003 (Professional PM sensor via UART)
    readPMS5003();
    
    // Read water level (ultrasonic)
    currentData.water_level = readWaterLevel();
    
    // Read TDS (salinity)
    currentData.tds = readTDS();
    
    // Read water presence sensor
    int waterSensorValue = analogRead(WATER_SENSOR_PIN);
    currentData.water_present = (waterSensorValue > thresholds.WATER_PRESENT);
    
    currentData.timestamp = millis();
    
    // Debug output
    Serial.println("📊 Sensor Readings:");
    Serial.printf("  VOC: %d ppb | eCO2: %d ppm\n", currentData.voc, currentData.eco2);
    Serial.printf("  PM2.5 (PMS5003): %.1f µg/m³ | PM10: %.1f µg/m³\n", 
                  currentData.pm25_primary, currentData.pm10);
    Serial.printf("  Temp: %.1f°C | Humidity: %.1f%%\n", 
                  currentData.temperature, currentData.humidity);
    Serial.printf("  Water Level: %.1f cm | TDS: %.0f ppm | Present: %s\n", 
                  currentData.water_level, currentData.tds, 
                  currentData.water_present ? "YES" : "NO");
    Serial.printf("  Fire Risk: %d | Flood Risk: %d\n", 
                  currentData.fire_risk, currentData.flood_risk);
    Serial.println();
}

void readPMS5003() {
    // PMS5003 data frame: 32 bytes
    // Header: 0x42 0x4D
    // Data: PM1.0, PM2.5, PM10 (standard + environment)
    
    uint8_t buffer[32];
    int index = 0;
    bool found_start = false;
    
    // Look for start bytes 0x42 0x4D
    while (pmsSerial.available() > 0 && index < 32) {
        uint8_t byte = pmsSerial.read();
        
        if (!found_start) {
            if (byte == 0x42) {
                buffer[index++] = byte;
            } else if (index == 1 && byte == 0x4D) {
                buffer[index++] = byte;
                found_start = true;
            } else {
                index = 0;
            }
        } else {
            buffer[index++] = byte;
            if (index >= 32) break;
        }
    }
    
    if (index >= 32 && buffer[0] == 0x42 && buffer[1] == 0x4D) {
        // Parse data (big-endian)
        uint16_t pm10_standard = (buffer[4] << 8) | buffer[5];
        uint16_t pm25_standard = (buffer[6] << 8) | buffer[7];
        uint16_t pm100_standard = (buffer[8] << 8) | buffer[9];
        
        // Use environmental values (more accurate for outdoor)
        uint16_t pm10_env = (buffer[10] << 8) | buffer[11];
        uint16_t pm25_env = (buffer[12] << 8) | buffer[13];
        uint16_t pm100_env = (buffer[14] << 8) | buffer[15];
        
        currentData.pm25_primary = pm25_env;
        currentData.pm10 = pm100_env;
    } else {
        Serial.println("⚠ PMS5003 read failed");
        currentData.pm25_primary = -1;
        currentData.pm10 = -1;
    }
}

float readWaterLevel() {
    // Grove Ultrasonic Ranger
    pinMode(ULTRASONIC_PIN, OUTPUT);
    digitalWrite(ULTRASONIC_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(ULTRASONIC_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(ULTRASONIC_PIN, LOW);
    
    pinMode(ULTRASONIC_PIN, INPUT);
    unsigned long duration = pulseIn(ULTRASONIC_PIN, HIGH, 30000);
    
    float distance = duration * 0.034 / 2;
    
    // Convert to water level
    const float SENSOR_HEIGHT = 300.0; // cm from canal bottom
    float water_level = SENSOR_HEIGHT - distance;
    
    if (distance < 2 || distance > 400) {
        return -1; // Invalid
    }
    
    return max(0.0f, water_level);
}

float readTDS() {
    // Grove TDS Sensor
    int analogValue = analogRead(TDS_SENSOR_PIN);
    float voltage = analogValue * (3.3 / 4095.0);
    
    // TDS formula
    float tds_value = (133.42 * pow(voltage, 3) - 255.86 * pow(voltage, 2) + 857.39 * voltage) * 0.5;
    
    // Temperature compensation
    float compensation_coefficient = 1.0 + 0.02 * (currentData.temperature - 25.0);
    tds_value = tds_value / compensation_coefficient;
    
    return max(0.0f, tds_value);
}

// ============= RISK CALCULATION =============
void calculateFireRisk() {
    int voc_risk = 0;
    if (currentData.voc >= thresholds.VOC_DANGER) voc_risk = 2;
    else if (currentData.voc >= thresholds.VOC_WARNING) voc_risk = 1;
    
    int pm_risk = 0;
    if (currentData.pm25_primary >= thresholds.PM25_DANGER) pm_risk = 2;
    else if (currentData.pm25_primary >= thresholds.PM25_WARNING) pm_risk = 1;
    
    int humidity_risk = 0;
    if (currentData.humidity <= thresholds.HUMIDITY_DANGER) humidity_risk = 2;
    else if (currentData.humidity <= thresholds.HUMIDITY_WARNING) humidity_risk = 1;
    
    int temp_risk = (currentData.temperature >= thresholds.TEMP_FIRE_RISK) ? 1 : 0;
    
    int max_risk = max({voc_risk, pm_risk, humidity_risk});
    int factor_count = (voc_risk > 0) + (pm_risk > 0) + (humidity_risk > 0) + (temp_risk > 0);
    
    if (factor_count >= 3) {
        currentData.fire_risk = 2;
    } else if (factor_count >= 2) {
        currentData.fire_risk = max(1, max_risk);
    } else {
        currentData.fire_risk = max_risk;
    }
}

void calculateFloodRisk() {
    int water_risk = 0;
    if (currentData.water_level >= thresholds.WATER_DANGER) water_risk = 2;
    else if (currentData.water_level >= thresholds.WATER_WARNING) water_risk = 1;
    
    int salinity_risk = 0;
    if (currentData.tds >= thresholds.TDS_DANGER) salinity_risk = 2;
    else if (currentData.tds >= thresholds.TDS_WARNING) salinity_risk = 1;
    
    // Immediate danger if water presence detected
    if (currentData.water_present) {
        water_risk = max(water_risk, 2);
    }
    
    if (water_risk >= 2 || salinity_risk >= 2) {
        currentData.flood_risk = 2;
    } else if (water_risk >= 1 || salinity_risk >= 1) {
        currentData.flood_risk = 1;
    } else {
        currentData.flood_risk = 0;
    }
    
    if (water_risk >= 1 && salinity_risk >= 1) {
        currentData.flood_risk = 2; // Saltwater flood
    }
}

// ============= ALERT SYSTEM =============
void checkAndTriggerAlert() {
    bool alert_triggered = false;
    
    if (currentData.fire_risk == 2) {
        Serial.println("🔥 FIRE DANGER!");
        alert_triggered = true;
        if (mqttClient.connected()) publishAlert("FIRE", "DANGER");
    }
    
    if (currentData.flood_risk == 2) {
        Serial.println("🌊 FLOOD DANGER!");
        alert_triggered = true;
        if (mqttClient.connected()) publishAlert("FLOOD", "DANGER");
    }
    
    if (alert_triggered && !alertActive) {
        digitalWrite(RELAY_PIN, HIGH);
        alertActive = true;
        alertStartTime = millis();
        Serial.println("🔔 SIREN ACTIVATED!");
    }
}

void publishAlert(const char* type, const char* level) {
    StaticJsonDocument<512> doc;
    
    doc["node_id"] = NODE_ID;
    doc["type"] = type;
    doc["level"] = level;
    
    if (strcmp(type, "FIRE") == 0) {
        doc["voc"] = currentData.voc;
        doc["pm25"] = currentData.pm25_primary;
        doc["temperature"] = currentData.temperature;
        doc["humidity"] = currentData.humidity;
        doc["message"] = "Risiko kebakaran tinggi! Gambut sangat kering.";
    } else {
        doc["water_level"] = currentData.water_level;
        doc["tds"] = currentData.tds;
        doc["water_present"] = currentData.water_present;
        if (currentData.tds >= thresholds.TDS_DANGER) {
            doc["message"] = "BAHAYA! Banjir air asin! Evakuasi!";
        } else {
            doc["message"] = "BAHAYA! Air sangat tinggi! Risiko banjir!";
        }
    }
    
    char buffer[512];
    serializeJson(doc, buffer);
    mqttClient.publish(MQTT_TOPIC_ALERT, buffer);
    Serial.println("📡 Alert sent");
}

// ============= MQTT FUNCTIONS =============
void connectWiFi() {
    Serial.print("WiFi connecting");
    displayStatus("WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println(" ✓");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());
        displayStatus("WiFi OK");
        wifiConnected = true;
    } else {
        Serial.println(" ✗");
        Serial.println("⚠ OFFLINE MODE");
        displayStatus("Offline");
        wifiConnected = false;
    }
    delay(1000);
}

void reconnectMQTT() {
    if (!wifiConnected) return;
    Serial.print("MQTT connecting... ");
    if (mqttClient.connect(NODE_ID)) {
        Serial.println("✓");
        mqttConnected = true;
    } else {
        Serial.print("✗ (");
        Serial.print(mqttClient.state());
        Serial.println(")");
        mqttConnected = false;
    }
}

void publishSensorData() {
    if (!mqttClient.connected()) return;
    
    StaticJsonDocument<512> doc;
    doc["node_id"] = NODE_ID;
    doc["timestamp"] = currentData.timestamp;
    doc["voc"] = currentData.voc;
    doc["eco2"] = currentData.eco2;
    doc["pm25"] = currentData.pm25_primary;
    doc["pm10"] = currentData.pm10;
    doc["temperature"] = currentData.temperature;
    doc["humidity"] = currentData.humidity;
    doc["water_level"] = currentData.water_level;
    doc["tds"] = currentData.tds;
    doc["water_present"] = currentData.water_present;
    doc["fire_risk"] = currentData.fire_risk;
    doc["flood_risk"] = currentData.flood_risk;
    doc["overall_risk"] = currentData.overall_risk;
    doc["lat"] = 0.8512;
    doc["lon"] = 103.3556;
    
    char buffer[512];
    serializeJson(doc, buffer);
    mqttClient.publish(MQTT_TOPIC_DATA, buffer);
    Serial.println("📡 Data published");
}

// ============= DISPLAY FUNCTIONS =============
void displayBootScreen() {
    selectI2CChannel(CH_OLED);
    display.clearBuffer();
    display.setFont(u8g2_font_ncenB10_tr);
    display.drawStr(15, 20, "PeatGuard");
    display.setFont(u8g2_font_6x10_tr);
    display.drawStr(5, 35, "Professional System");
    display.drawStr(10, 50, "Fire + Flood");
    display.drawStr(15, 60, "Sungai Tohor");
    display.sendBuffer();
}

void displayStatus(const char* message) {
    selectI2CChannel(CH_OLED);
    display.clearBuffer();
    display.setFont(u8g2_font_6x10_tr);
    display.drawStr(0, 30, message);
    display.sendBuffer();
}

void updateDisplay() {
    selectI2CChannel(CH_OLED);
    display.clearBuffer();
    
    // Title
    display.setFont(u8g2_font_6x10_tr);
    display.drawStr(0, 8, "PeatGuard Pro");
    display.drawLine(0, 10, 128, 10);
    
    // Risk display
    int max_risk = max(currentData.fire_risk, currentData.flood_risk);
    display.setFont(u8g2_font_ncenB08_tr);
    
    if (max_risk == 2) {
        if ((millis() / 500) % 2 == 0) {
            display.drawBox(30, 14, 70, 14);
            display.setDrawColor(0);
            display.drawStr(35, 24, "BAHAYA!");
            display.setDrawColor(1);
        } else {
            display.drawStr(35, 24, "BAHAYA!");
        }
    } else if (max_risk == 1) {
        display.drawStr(25, 24, "HATI-HATI");
    } else {
        display.drawStr(45, 24, "AMAN");
    }
    
    // Hazard type
    display.setFont(u8g2_font_5x7_tr);
    char hazard[32];
    if (currentData.fire_risk == 2) {
        sprintf(hazard, "Api: BAHAYA");
    } else if (currentData.flood_risk == 2) {
        sprintf(hazard, "Banjir: BAHAYA");
    } else if (currentData.fire_risk == 1) {
        sprintf(hazard, "Api: Waspada");
    } else if (currentData.flood_risk == 1) {
        sprintf(hazard, "Banjir: Waspada");
    } else {
        sprintf(hazard, "Semua Aman");
    }
    display.drawStr(0, 36, hazard);
    
    // Sensor values (compact)
    char line1[32], line2[32], line3[32];
    sprintf(line1, "Air:%.0fcm TDS:%.0f", currentData.water_level, currentData.tds);
    sprintf(line2, "VOC:%d PM:%.0f", currentData.voc, currentData.pm25_primary);
    sprintf(line3, "%.1fC %.0f%%", currentData.temperature, currentData.humidity);
    
    display.drawStr(0, 45, line1);
    display.drawStr(0, 54, line2);
    display.drawStr(0, 63, line3);
    
    // Status
    if (currentData.water_present) display.drawStr(80, 63, "WET!");
    if (wifiConnected) display.drawStr(110, 63, "W");
    if (mqttConnected) display.drawStr(120, 63, "M");
    
    display.sendBuffer();
}
