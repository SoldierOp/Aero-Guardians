/*
 * PeatGuard Dual-Hazard Early Warning System
 * Hardware: Seeed XIAO ESP32S3 + Grove Sensors
 * 
 * FIRE DETECTION SENSORS:
 * - SGP30 VOC Sensor (I2C) → Detects peat decomposition/burning
 * - Dust Sensor (I2C) → Detects smoke PM2.5
 * - MCP9808 Temp/Humidity (I2C) → Drought conditions
 * 
 * FLOOD DETECTION SENSORS:
 * - Grove Ultrasonic Ranger → Water level measurement
 * - Grove TDS Sensor → Salinity/saltwater intrusion detection
 * 
 * OUTPUTS:
 * - Grove OLED Display → Shows risk status
 * - Grove Relay → Triggers siren/alarm for fire OR flood
 * - WiFi/MQTT → Sends data to cloud (when available)
 * 
 * UNIQUE FEATURES:
 * - Dual-hazard monitoring (fire + flood)
 * - Edge AI risk prediction (TinyML)
 * - Offline-first operation
 * - Indonesian language display
 * - Physical alert system
 */

#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <U8g2lib.h>
#include <ArduinoJson.h>
#include <SparkFunCCS811.h> // For SGP30 VOC sensor
#include <Adafruit_MCP9808.h>

// ============= HARDWARE PINS =============
#define I2C_SDA 4
#define I2C_SCL 5
#define RELAY_PIN 2           // Grove Relay control (siren/alarm)
#define DUST_SENSOR_PIN 3     // Grove Dust Sensor (PM2.5)
#define ULTRASONIC_PIN 6      // Grove Ultrasonic Ranger (water level)
#define TDS_SENSOR_PIN A0     // Grove TDS Sensor (salinity)

// ============= WIFI CONFIGURATION =============
const char* WIFI_SSID = "YourWiFiSSID";          // Change this
const char* WIFI_PASSWORD = "YourWiFiPassword";  // Change this

// ============= MQTT CONFIGURATION =============
const char* MQTT_BROKER = "broker.hivemq.com";  // Free broker for testing
const int MQTT_PORT = 1883;
const char* MQTT_TOPIC_DATA = "peatguard/sungaitohor/sensors";
const char* MQTT_TOPIC_ALERT = "peatguard/sungaitohor/alerts";
const char* NODE_ID = "SungaiTohor_Node01";

// ============= SENSORS =============
CCS811 vocSensor(0x5A);  // SGP30 VOC sensor
Adafruit_MCP9808 tempSensor = Adafruit_MCP9808();
U8G2_SSD1306_128X64_NONAME_F_HW_I2C display(U8G2_R0, U8X8_PIN_NONE);

// ============= MQTT CLIENT =============
WiFiClient espClient;
PubSubClient mqttClient(espClient);

// ============= RISK THRESHOLDS =============
struct Thresholds {
    // Fire Risk Indicators
    int VOC_SAFE = 400;      // ppb
    int VOC_WARNING = 800;
    int VOC_DANGER = 1500;
    
    int PM25_SAFE = 50;      // µg/m³
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
    
    // Salinity Risk Indicators (TDS)
    float TDS_SAFE = 500;         // ppm (fresh water)
    float TDS_WARNING = 1500;     // ppm (brackish)
    float TDS_DANGER = 2500;      // ppm (saltwater intrusion)
} thresholds;

// ============= SENSOR DATA =============
struct SensorData {
    // Fire indicators
    int voc;           // VOC in ppb
    int eco2;          // eCO2 in ppm
    float pm25;        // PM2.5 in µg/m³
    float temperature; // Temperature in °C
    float humidity;    // Humidity in %
    
    // Flood indicators
    float water_level; // Water level in cm
    float tds;         // TDS (salinity) in ppm
    
    // Risk scores
    int fire_risk;     // 0=Safe, 1=Warning, 2=Danger
    int flood_risk;    // 0=Safe, 1=Warning, 2=Danger
    int overall_risk;  // Maximum of fire/flood risk
    
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

const unsigned long SENSOR_INTERVAL = 5000;    // Read sensors every 5 seconds
const unsigned long MQTT_INTERVAL = 30000;     // Publish every 30 seconds
const unsigned long DISPLAY_INTERVAL = 2000;   // Update display every 2 seconds
const unsigned long ALERT_INTERVAL = 10000;    // Check alerts every 10 seconds
const unsigned long RECONNECT_INTERVAL = 10000; // Try reconnect every 10 seconds

bool alertActive = false;
unsigned long alertStartTime = 0;
const unsigned long ALERT_DURATION = 5000;  // Siren duration 5 seconds

// ============= SETUP =============
void setup() {
    Serial.begin(115200);
    Serial.println("🔥 PeatGuard Fire Early Warning System");
    Serial.println("=====================================");
    
    // Initialize I2C
    Wire.begin(I2C_SDA, I2C_SCL);
    
    // Initialize display
    display.begin();
    displayBootScreen();
    delay(2000);
    
    // Initialize relay (siren control)
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW);
    
    // Initialize dust sensor
    pinMode(DUST_SENSOR_PIN, INPUT);
    
    // Initialize water level sensor (ultrasonic)
    pinMode(ULTRASONIC_PIN, INPUT);
    
    // Initialize TDS sensor (analog)
    pinMode(TDS_SENSOR_PIN, INPUT);
    
    // Initialize VOC sensor
    Serial.print("Initializing VOC sensor... ");
    if (vocSensor.begin()) {
        Serial.println("✓");
        displayStatus("VOC sensor OK");
    } else {
        Serial.println("✗ FAILED");
        displayStatus("VOC FAIL!");
        delay(2000);
    }
    
    // Initialize temperature sensor
    Serial.print("Initializing temp sensor... ");
    if (tempSensor.begin(0x18)) {
        Serial.println("✓");
        displayStatus("Temp sensor OK");
    } else {
        Serial.println("✗ FAILED");
        displayStatus("Temp FAIL!");
        delay(2000);
    }
    
    // Connect to WiFi
    connectWiFi();
    
    // Setup MQTT
    mqttClient.setServer(MQTT_BROKER, MQTT_PORT);
    
    delay(1000);
    Serial.println("\n🚀 System ready!");
    Serial.println("Monitoring peatland for fire AND flood risk...\n");
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
        
        // Reconnect if needed
        if (!mqttClient.connected()) {
            if (currentMillis - lastReconnectAttempt >= RECONNECT_INTERVAL) {
                lastReconnectAttempt = currentMillis;
                reconnectMQTT();
            }
        } else {
            publishSensorData();
        }
    }
    
    // MQTT loop (for receiving messages)
    if (mqttClient.connected()) {
        mqttClient.loop();
    }
    
    // Handle active alert (turn off siren after duration)
    if (alertActive && (currentMillis - alertStartTime >= ALERT_DURATION)) {
        digitalWrite(RELAY_PIN, LOW);
        alertActive = false;
    }
}

// ============= SENSOR READING =============
void readSensors() {
    // Read VOC sensor (SGP30)
    if (vocSensor.dataAvailable()) {
        vocSensor.readAlgorithmResults();
        currentData.voc = vocSensor.getTVOC();
        currentData.eco2 = vocSensor.getCO2();
    }
    
    // Read temperature & humidity (MCP9808)
    currentData.temperature = tempSensor.readTempC();
    
    // Read humidity (if available on your MCP9808 variant)
    // Note: MCP9808 is temp-only. You may have DHT22 or similar
    // Adjust this section based on your actual humidity sensor
    currentData.humidity = 65.0;  // TODO: Read from actual humidity sensor
    
    // Read PM2.5 from dust sensor
    currentData.pm25 = readDustSensor();
    
    // Read water level (ultrasonic ranger)
    currentData.water_level = readWaterLevel();
    
    // Read TDS (salinity)
    currentData.tds = readTDS();
    
    currentData.timestamp = millis();
    
    // Debug output
    Serial.println("📊 Sensor Readings:");
    Serial.printf("  VOC: %d ppb\n", currentData.voc);
    Serial.printf("  eCO2: %d ppm\n", currentData.eco2);
    Serial.printf("  PM2.5: %.1f µg/m³\n", currentData.pm25);
    Serial.printf("  Temp: %.1f°C\n", currentData.temperature);
    Serial.printf("  Humidity: %.1f%%\n", currentData.humidity);
    Serial.printf("  Water Level: %.1f cm\n", currentData.water_level);
    Serial.printf("  TDS (Salinity): %.0f ppm\n", currentData.tds);
    Serial.printf("  Fire Risk: %d | Flood Risk: %d\n", currentData.fire_risk, currentData.flood_risk);
    Serial.println();
}

float readDustSensor() {
    // Grove Dust Sensor (PPD42NS) reading
    // Returns PM2.5 concentration in µg/m³
    
    unsigned long duration = pulseIn(DUST_SENSOR_PIN, LOW, 30000);
    float ratio = duration / (float)(30000 * 10.0);
    float concentration = 1.1 * pow(ratio, 3) - 3.8 * pow(ratio, 2) + 520 * ratio + 0.62;
    
    return max(0.0f, concentration);
}

float readWaterLevel() {
    // Grove Ultrasonic Ranger reading
    // Returns water level in cm (distance from sensor to water surface)
    
    pinMode(ULTRASONIC_PIN, OUTPUT);
    digitalWrite(ULTRASONIC_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(ULTRASONIC_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(ULTRASONIC_PIN, LOW);
    
    pinMode(ULTRASONIC_PIN, INPUT);
    unsigned long duration = pulseIn(ULTRASONIC_PIN, HIGH, 30000);
    
    // Calculate distance in cm (speed of sound = 340 m/s)
    float distance = duration * 0.034 / 2;
    
    // Convert to water level (assuming sensor is mounted 300cm above canal bottom)
    // Adjust SENSOR_HEIGHT based on your installation
    const float SENSOR_HEIGHT = 300.0;  // cm from canal bottom
    float water_level = SENSOR_HEIGHT - distance;
    
    // Validate reading
    if (distance < 2 || distance > 400) {
        return -1;  // Invalid reading
    }
    
    return max(0.0f, water_level);
}

float readTDS() {
    // Grove TDS Sensor reading
    // Returns Total Dissolved Solids in ppm (salinity indicator)
    
    int analogValue = analogRead(TDS_SENSOR_PIN);
    
    // Convert to voltage (ESP32 ADC: 0-4095 = 0-3.3V)
    float voltage = analogValue * (3.3 / 4095.0);
    
    // TDS formula (from Grove TDS sensor datasheet)
    // TDS (ppm) = (133.42 * voltage^3 - 255.86 * voltage^2 + 857.39 * voltage) * 0.5
    float tds_value = (133.42 * pow(voltage, 3) - 255.86 * pow(voltage, 2) + 857.39 * voltage) * 0.5;
    
    // Temperature compensation (25°C reference)
    float compensation_coefficient = 1.0 + 0.02 * (currentData.temperature - 25.0);
    tds_value = tds_value / compensation_coefficient;
    
    return max(0.0f, tds_value);
}

// ============= FIRE RISK CALCULATION =============
void calculateFireRisk() {
    // Multi-factor fire risk assessment
    
    int voc_risk = 0;
    if (currentData.voc >= thresholds.VOC_DANGER) voc_risk = 2;
    else if (currentData.voc >= thresholds.VOC_WARNING) voc_risk = 1;
    
    int pm_risk = 0;
    if (currentData.pm25 >= thresholds.PM25_DANGER) pm_risk = 2;
    else if (currentData.pm25 >= thresholds.PM25_WARNING) pm_risk = 1;
    
    int humidity_risk = 0;
    if (currentData.humidity <= thresholds.HUMIDITY_DANGER) humidity_risk = 2;
    else if (currentData.humidity <= thresholds.HUMIDITY_WARNING) humidity_risk = 1;
    
    int temp_risk = (currentData.temperature >= thresholds.TEMP_FIRE_RISK) ? 1 : 0;
    
    // Overall risk: Highest individual risk + bonus for multiple factors
    int max_risk = max({voc_risk, pm_risk, humidity_risk});
    int factor_count = (voc_risk > 0) + (pm_risk > 0) + (humidity_risk > 0) + (temp_risk > 0);
    
    if (factor_count >= 3) {
        currentData.fire_risk = 2;  // DANGER: Multiple risk factors
    } else if (factor_count >= 2) {
        currentData.fire_risk = max(1, max_risk);  // At least WARNING
    } else {
        currentData.fire_risk = max_risk;
    }
    
    // TODO: Add Edge ML prediction here
    // float ml_prediction = fireRiskModel.predict(currentData);
    // currentData.fire_risk = (int)ml_prediction;
}

// ============= FLOOD RISK CALCULATION =============
void calculateFloodRisk() {
    // Multi-factor flood risk assessment
    
    int water_risk = 0;
    if (currentData.water_level >= thresholds.WATER_DANGER) water_risk = 2;
    else if (currentData.water_level >= thresholds.WATER_WARNING) water_risk = 1;
    
    int salinity_risk = 0;
    if (currentData.tds >= thresholds.TDS_DANGER) salinity_risk = 2;
    else if (currentData.tds >= thresholds.TDS_WARNING) salinity_risk = 1;
    
    // Overall flood risk: Consider both water level and salinity
    // High water + high salinity = Severe flood with saltwater intrusion (worst case)
    if (water_risk >= 2 || salinity_risk >= 2) {
        currentData.flood_risk = 2;  // DANGER
    } else if (water_risk >= 1 || salinity_risk >= 1) {
        currentData.flood_risk = 1;  // WARNING
    } else {
        currentData.flood_risk = 0;  // SAFE
    }
    
    // Bonus risk: Both factors elevated simultaneously = critical
    if (water_risk >= 1 && salinity_risk >= 1) {
        currentData.flood_risk = 2;  // DANGER: Saltwater flood imminent
    }
}

// ============= ALERT SYSTEM =============
void checkAndTriggerAlert() {
    bool alert_triggered = false;
    
    // Check fire risk
    if (currentData.fire_risk == 2) {  // DANGER level
        Serial.println("🔥 FIRE DANGER DETECTED!");
        alert_triggered = true;
        
        // Send MQTT alert (if connected)
        if (mqttClient.connected()) {
            publishAlert("FIRE", "DANGER");
        }
    }
    
    // Check flood risk
    if (currentData.flood_risk == 2) {  // DANGER level
        Serial.println("🌊 FLOOD DANGER DETECTED!");
        alert_triggered = true;
        
        // Send MQTT alert (if connected)
        if (mqttClient.connected()) {
            publishAlert("FLOOD", "DANGER");
        }
    }
    
    // Activate siren if any danger detected
    if (alert_triggered && !alertActive) {
        digitalWrite(RELAY_PIN, HIGH);
        alertActive = true;
        alertStartTime = millis();
        Serial.println("🔔 Siren activated!");
    }
}

void publishAlert(const char* type, const char* level) {
    StaticJsonDocument<512> doc;
    
    doc["node_id"] = NODE_ID;
    doc["type"] = type;
    doc["level"] = level;
    
    if (strcmp(type, "FIRE") == 0) {
        doc["voc"] = currentData.voc;
        doc["pm25"] = currentData.pm25;
        doc["temperature"] = currentData.temperature;
        doc["humidity"] = currentData.humidity;
        
        if (currentData.fire_risk == 2) {
            doc["message"] = "Risiko kebakaran tinggi! Kondisi gambut sangat kering.";
        } else {
            doc["message"] = "Peringatan: Kondisi gambut kering. Waspadai api.";
        }
    } else {  // FLOOD
        doc["water_level"] = currentData.water_level;
        doc["tds"] = currentData.tds;
        
        if (currentData.flood_risk == 2) {
            if (currentData.tds >= thresholds.TDS_DANGER) {
                doc["message"] = "BAHAYA! Air pasang tinggi + air asin! Segera evakuasi!";
            } else {
                doc["message"] = "BAHAYA! Ketinggian air sangat tinggi! Risiko banjir!";
            }
        } else {
            doc["message"] = "Peringatan: Air mulai naik. Siapkan evakuasi.";
        }
    }
    
    char buffer[512];
    serializeJson(doc, buffer);
    
    mqttClient.publish(MQTT_TOPIC_ALERT, buffer);
    Serial.println("📡 Alert published to MQTT");
}

// ============= MQTT FUNCTIONS =============
void connectWiFi() {
    Serial.print("Connecting to WiFi");
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
        Serial.println(" ✗ FAILED");
        Serial.println("⚠ Running in OFFLINE mode");
        displayStatus("Offline Mode");
        wifiConnected = false;
    }
    
    delay(1000);
}

void reconnectMQTT() {
    if (!wifiConnected) {
        Serial.println("WiFi not connected, skipping MQTT");
        return;
    }
    
    Serial.print("Connecting to MQTT... ");
    
    if (mqttClient.connect(NODE_ID)) {
        Serial.println("✓");
        mqttConnected = true;
    } else {
        Serial.print("✗ FAILED (rc=");
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
    doc["pm25"] = currentData.pm25;
    doc["temperature"] = currentData.temperature;
    doc["humidity"] = currentData.humidity;
    doc["water_level"] = currentData.water_level;
    doc["tds"] = currentData.tds;
    doc["fire_risk"] = currentData.fire_risk;
    doc["flood_risk"] = currentData.flood_risk;
    doc["overall_risk"] = currentData.overall_risk;
    doc["lat"] = 0.8512;  // Sungai Tohor coordinates
    doc["lon"] = 103.3556;
    
    char buffer[512];
    serializeJson(doc, buffer);
    
    mqttClient.publish(MQTT_TOPIC_DATA, buffer);
    Serial.println("📡 Data published to MQTT");
}

// ============= DISPLAY FUNCTIONS =============
void displayBootScreen() {
    display.clearBuffer();
    display.setFont(u8g2_font_ncenB10_tr);
    display.drawStr(20, 20, "PeatGuard");
    display.setFont(u8g2_font_6x10_tr);
    display.drawStr(10, 40, "Fire Warning System");
    display.drawStr(15, 55, "Sungai Tohor");
    display.sendBuffer();
}

void displayStatus(const char* message) {
    display.clearBuffer();
    display.setFont(u8g2_font_6x10_tr);
    display.drawStr(0, 30, message);
    display.sendBuffer();
}

void updateDisplay() {
    display.clearBuffer();
    
    // Title
    display.setFont(u8g2_font_6x10_tr);
    display.drawStr(0, 8, "PeatGuard - Dual Hazard");
    display.drawLine(0, 10, 128, 10);
    
    // Determine highest risk
    int max_risk = max(currentData.fire_risk, currentData.flood_risk);
    
    // Risk level display
    display.setFont(u8g2_font_ncenB08_tr);
    
    const char* riskText;
    if (max_risk == 2) {
        riskText = "BAHAYA!";
        // Flash display for danger
        if ((millis() / 500) % 2 == 0) {
            display.drawBox(0, 14, 128, 14);
            display.setDrawColor(0);
            display.drawStr(35, 24, riskText);
            display.setDrawColor(1);
        } else {
            display.drawStr(35, 24, riskText);
        }
    } else if (max_risk == 1) {
        riskText = "HATI-HATI";
        display.drawStr(25, 24, riskText);
    } else {
        riskText = "AMAN";
        display.drawStr(45, 24, riskText);
    }
    
    // Show which hazard is active
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
    
    // Key sensor values
    char buffer[32];
    
    sprintf(buffer, "Air:%.0fcm TDS:%.0f", currentData.water_level, currentData.tds);
    display.drawStr(0, 45, buffer);
    
    sprintf(buffer, "VOC:%d PM:%.0f", currentData.voc, currentData.pm25);
    display.drawStr(0, 54, buffer);
    
    sprintf(buffer, "%.1fC %.0f%%", currentData.temperature, currentData.humidity);
    display.drawStr(0, 63, buffer);
    
    // Connection status
    display.drawStr(80, 63, wifiConnected ? "WiFi" : "Off");
    display.drawStr(110, 63, mqttConnected ? "M" : "");
    
    display.sendBuffer();
}
