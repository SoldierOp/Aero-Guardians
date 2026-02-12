/*
 * Test TDS Sensor ONLY
 * Pin: GPIO 1 (A0)
 */

#define TDS_PIN 1

void setup() {
  Serial.begin(115200);
  delay(2000);
  
  pinMode(TDS_PIN, INPUT);
  
  Serial.println("=== TDS Sensor Test ===");
  Serial.println("GPIO 1 (A0)");
  Serial.println("=======================\n");
}

void loop() {
  // Read raw value
  int raw = analogRead(TDS_PIN);
  
  Serial.print("TDS Raw: ");
  Serial.print(raw);
  Serial.print("  |  ");
  
  // Convert to voltage
  float voltage = raw * (3.3 / 4095.0);
  Serial.print("Voltage: ");
  Serial.print(voltage, 3);
  Serial.println("V");
  
  // Status
  if(raw == 0) {
    Serial.println("⚠️ Reading ZERO - Check wiring or probe not in water");
  } else if(raw == 4095) {
    Serial.println("⚠️ Reading MAX - Pin floating or short to 3.3V");
  } else if(raw < 100) {
    Serial.println("⚠️ Very low - Probe likely NOT in water");
  } else {
    Serial.println("✅ Getting readings - Probe connected");
  }
  
  Serial.println();
  delay(1000);
}
