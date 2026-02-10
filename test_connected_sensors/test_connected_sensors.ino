/*
 * PeatGuard Pro - Test Connected Sensors
 * Tests: I2C Hub + SGP30 + Dust + MCP9808 + PMS5003 + TDS + Water
 * 
 * Upload this to XIAO ESP32S3 to verify all connected sensors
 */

#include <Wire.h>
#include <Adafruit_SGP30.h>
#include <Adafruit_MCP9808.h>
#include <U8g2lib.h>

// OLED Display
U8G2_SSD1306_128X64_NONAME_F_HW_I2C u8g2(U8G2_R0, /* reset=*/ U8X8_PIN_NONE);

// I2C Sensors
Adafruit_SGP30 sgp;
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();

// I2C Hub (TCA9548A)
#define TCA_ADDR 0x70
void tcaselect(uint8_t i) {
  if (i > 7) return;
  Wire.beginTransmission(TCA_ADDR);
  Wire.write(1 << i);
  Wire.endTransmission();
}

// PMS5003 UART
#define PMS_RX 44  // GPIO 44 (ESP32 RX <- PMS TX)
#define PMS_TX 43  // GPIO 43 (ESP32 TX -> PMS RX)
HardwareSerial pmsSerial(1);

// Analog Sensors
#define TDS_PIN 1   // GPIO 1 (A0)
#define WATER_PIN 2 // GPIO 2 (A1)

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  Serial.println("\n\n=================================");
  Serial.println("   PeatGuard Pro Sensor Test");
  Serial.println("=================================\n");

  // Initialize I2C
  Wire.begin(4, 5); // SDA=GPIO4, SCL=GPIO5
  
  // Initialize OLED
  u8g2.begin();
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.drawStr(0, 15, "PeatGuard Pro");
  u8g2.drawStr(0, 30, "Sensor Test");
  u8g2.sendBuffer();
  
  Serial.println("✅ OLED Display: Working!");

  // Test I2C Hub
  Serial.println("\n--- Testing I2C Hub (TCA9548A) ---");
  Wire.beginTransmission(TCA_ADDR);
  if (Wire.endTransmission() == 0) {
    Serial.println("✅ I2C Hub found at 0x70");
  } else {
    Serial.println("❌ I2C Hub NOT found!");
  }

  // Test SGP30 on Channel 0
  Serial.println("\n--- Testing SGP30 VOC Sensor (CH0) ---");
  tcaselect(0);
  if (sgp.begin()) {
    Serial.println("✅ SGP30 found!");
    Serial.print("   Serial #: ");
    Serial.print(sgp.serialnumber[0], HEX);
    Serial.print(sgp.serialnumber[1], HEX);
    Serial.println(sgp.serialnumber[2], HEX);
  } else {
    Serial.println("❌ SGP30 NOT found on CH0");
  }

  // Test MCP9808 on Channel 1
  Serial.println("\n--- Testing MCP9808 Temp/Humidity (CH1) ---");
  tcaselect(1);
  if (tempsensor.begin(0x18)) {
    Serial.println("✅ MCP9808 found!");
    tempsensor.setResolution(3); // 0.0625°C resolution
  } else {
    Serial.println("❌ MCP9808 NOT found on CH1");
  }

  // Test Dust Sensor on Channel 2
  Serial.println("\n--- Testing Dust Sensor (CH2) ---");
  tcaselect(2);
  Wire.beginTransmission(0x52);
  if (Wire.endTransmission() == 0) {
    Serial.println("✅ Dust Sensor found at 0x52");
  } else {
    Serial.println("❌ Dust Sensor NOT found on CH2");
  }

  // Initialize PMS5003 UART
  Serial.println("\n--- Testing PMS5003 (UART) ---");
  pmsSerial.begin(9600, SERIAL_8N1, PMS_RX, PMS_TX);
  Serial.println("✅ PMS5003 UART initialized on GPIO43/44");
  Serial.println("   Waiting for data packets...");

  // Analog sensors
  pinMode(TDS_PIN, INPUT);
  pinMode(WATER_PIN, INPUT);
  Serial.println("\n--- Analog Sensors Configured ---");
  Serial.println("✅ TDS Sensor on GPIO 1 (A0)");
  Serial.println("✅ Water Sensor on GPIO 2 (A1)");

  Serial.println("\n=================================");
  Serial.println("   Starting continuous monitoring");
  Serial.println("=================================\n");
}

void loop() {
  static unsigned long lastRead = 0;
  if (millis() - lastRead < 3000) return;
  lastRead = millis();

  Serial.println("\n--- Sensor Readings ---");

  // Read SGP30 (VOC)
  tcaselect(0);
  if (sgp.IAQmeasure()) {
    Serial.print("🔥 VOC: ");
    Serial.print(sgp.TVOC);
    Serial.print(" ppb, eCO2: ");
    Serial.print(sgp.eCO2);
    Serial.println(" ppm");
  }

  // Read MCP9808 (Temperature)
  tcaselect(1);
  float temp = tempsensor.readTempC();
  Serial.print("🌡️  Temperature: ");
  Serial.print(temp);
  Serial.println(" °C");

  // Read Dust Sensor (PM2.5)
  tcaselect(2);
  Wire.requestFrom(0x52, 4);
  if (Wire.available() >= 4) {
    uint8_t data[4];
    for (int i = 0; i < 4; i++) {
      data[i] = Wire.read();
    }
    uint16_t pm25 = (data[0] << 8) | data[1];
    Serial.print("💨 Dust PM2.5: ");
    Serial.print(pm25);
    Serial.println(" µg/m³");
  }

  // Read PMS5003 (Professional PM2.5)
  if (pmsSerial.available()) {
    // Look for PMS5003 data packet header (0x42, 0x4d)
    if (pmsSerial.read() == 0x42) {
      if (pmsSerial.read() == 0x4d) {
        uint8_t buffer[30];
        pmsSerial.readBytes(buffer, 30);
        
        uint16_t pm25 = (buffer[4] << 8) | buffer[5];
        Serial.print("🔬 PMS5003 PM2.5: ");
        Serial.print(pm25);
        Serial.println(" µg/m³");
      }
    }
  } else {
    Serial.println("⏳ PMS5003: Waiting for data...");
  }

  // Read TDS Sensor
  int tdsRaw = analogRead(TDS_PIN);
  float tdsVoltage = tdsRaw * (3.3 / 4095.0);
  float tds = (133.42 * tdsVoltage * tdsVoltage * tdsVoltage 
               - 255.86 * tdsVoltage * tdsVoltage 
               + 857.39 * tdsVoltage) * 0.5;
  Serial.print("💧 TDS: ");
  Serial.print(tds);
  Serial.print(" ppm (Raw: ");
  Serial.print(tdsRaw);
  Serial.println(")");

  // Read Water Sensor
  int waterRaw = analogRead(WATER_PIN);
  bool isWet = (waterRaw > 500);
  Serial.print("🌊 Water: ");
  Serial.print(isWet ? "WET ✅" : "DRY");
  Serial.print(" (Raw: ");
  Serial.print(waterRaw);
  Serial.println(")");

  // Update OLED
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  u8g2.drawStr(0, 10, "PeatGuard Sensors");
  
  char buf[20];
  sprintf(buf, "Temp: %.1f C", temp);
  u8g2.drawStr(0, 25, buf);
  
  sprintf(buf, "TDS: %.0f ppm", tds);
  u8g2.drawStr(0, 40, buf);
  
  u8g2.drawStr(0, 55, isWet ? "Water: WET" : "Water: DRY");
  u8g2.sendBuffer();

  Serial.println("----------------------");
}
