/*
 * PeatGuard Pro - Final Production Code
 * Sensors: SGP30 (VOC/eCO2) + MCP9808 (Temp) + PMS5003 (PM2.5) + TDS
 * Output: OLED Display + Buzzer Alerts + Serial Monitor
 */

#include <Wire.h>
#include <Adafruit_SGP30.h>
#include <Adafruit_MCP9808.h>
#include <U8g2lib.h>

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
#define BUZZER_PIN A3  // GPIO 3 on XIAO base board

// Sensor data storage
uint16_t pm25 = 0;
int voc = 0;
int eco2 = 0;
float temp = 0;
int tdsRaw = 0;
bool alertActive = false;

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
  u8g2.drawStr(0, 35, "Initializing...");
  u8g2.sendBuffer();
  
  buzzerAlert(1); // Single beep on boot
  
  Serial.println("\n=================================");
  Serial.println("   PeatGuard Pro - Final System");
  Serial.println("=================================\n");

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
  u8g2.drawStr(0, 20, "PeatGuard Pro");
  u8g2.drawStr(0, 40, "System Ready!");
  u8g2.sendBuffer();
  delay(2000);
}

void loop() {
  static unsigned long lastRead = 0;
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
  } else {
    Serial.println("❌ VOC read failed");
  }

  // Read Temperature
  tcaselect(1);
  delay(50);
  temp = tempsensor.readTempC();
  Serial.print("🌡️  Temperature: ");
  Serial.print(temp, 1);
  Serial.println(" °C");

  // Read PMS5003 (PM2.5)
  if (pmsSerial.available() >= 32) {
    if (pmsSerial.read() == 0x42) {
      if (pmsSerial.read() == 0x4d) {
        uint8_t buffer[30];
        pmsSerial.readBytes(buffer, 30);
        pm25 = (buffer[4] << 8) | buffer[5];
      }
    }
  }
  Serial.print("🔬 PM2.5: ");
  if(pm25 > 0) {
    Serial.print(pm25);
    Serial.println(" µg/m³");
  } else {
    Serial.println("Waiting for data...");
  }

  // Read TDS (Water Detection)
  tdsRaw = 0;
  for(int i = 0; i < 10; i++) {
    tdsRaw += analogRead(TDS_PIN);
    delay(5);
  }
  tdsRaw /= 10;
  
  Serial.print("💧 TDS Raw: ");
  Serial.print(tdsRaw);
  if(tdsRaw < 50) {
    Serial.println(" (NO WATER - Probe dry)");
  } else {
    float tdsVoltage = tdsRaw * (3.3 / 4095.0);
    float tds = (133.42 * tdsVoltage * tdsVoltage * tdsVoltage 
                 - 255.86 * tdsVoltage * tdsVoltage 
                 + 857.39 * tdsVoltage) * 0.5;
    Serial.print(" → ");
    Serial.print(tds, 1);
    Serial.println(" ppm (Water present)");
  }

  // Fire Risk Assessment
  alertActive = false;
  String status = "NORMAL";
  
  // Critical conditions
  if(voc > 100 || pm25 > 150 || temp > 40) {
    alertActive = true;
    status = "DANGER!";
    buzzerAlert(3); // 3 beeps for danger
    Serial.println("🚨 FIRE RISK ALERT!");
  } 
  // Warning conditions
  else if(voc > 50 || pm25 > 75 || temp > 35) {
    alertActive = true;
    status = "WARNING";
    buzzerAlert(1); // 1 beep for warning
    Serial.println("⚠️  WARNING - Elevated readings");
  }

  Serial.println("-----------------------");

  // Update OLED Display
  Wire.begin(); // Reset to main I2C bus
  u8g2.clearBuffer();
  u8g2.setFont(u8g2_font_ncenB08_tr);
  
  char buf[22];
  
  // Line 1: Status
  u8g2.drawStr(0, 10, status.c_str());
  
  // Line 2: Temperature & VOC
  sprintf(buf, "T:%.1fC V:%d", temp, voc);
  u8g2.drawStr(0, 25, buf);
  
  // Line 3: PM2.5
  sprintf(buf, "PM2.5:%d ug", pm25);
  u8g2.drawStr(0, 40, buf);
  
  // Line 4: Water status
  if(tdsRaw < 50) {
    u8g2.drawStr(0, 55, "Water: DRY");
  } else {
    sprintf(buf, "Water: %d", tdsRaw);
    u8g2.drawStr(0, 55, buf);
  }
  
  u8g2.sendBuffer();
}
