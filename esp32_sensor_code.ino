#include <Arduino.h>
#include <Wire.h>
#include <U8x8lib.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "Adafruit_SGP30.h"
#include "Adafruit_MCP9808.h"

// ---------------- CONFIGURATION ----------------
// WI-FI CREDENTIALS - REPLACE WITH YOUR WIFI
#define STASSID "YOUR_WIFI_NAME"
#define STAPSK  "YOUR_WIFI_PASSWORD"

// WEB APP ENDPOINT - REPLACE WITH YOUR COMPUTER'S IP
// To find your IP: Open Command Prompt and type "ipconfig"
// Look for "IPv4 Address" under your active network adapter
// Example: "http://192.168.1.100:5000/api/data"
const char* serverName = "http://YOUR_COMPUTER_IP:5000/api/data"; 

// Pin Configuration
#define DUST_PIN D0 
#define BUZZER_PIN D3

// Threshold Settings
#define THRESH_DUST 1000  
#define THRESH_TVOC 500   
#define THRESH_ECO2 1000  
#define THRESH_TEMP 40.0  

// ---------------- VARIABLES ----------------
unsigned long duration;
unsigned long starttime;
unsigned long sampletime_ms = 5000; // Send data every 5 seconds
unsigned long lowpulseoccupancy = 0;
float ratio = 0;
float dustConcentration = 0;

// Connection retry settings
int wifiRetryCount = 0;
const int MAX_WIFI_RETRIES = 40;  // Increased from 20 to 40

// ---------------- OBJECTS ----------------
U8X8_SSD1306_128X64_NONAME_HW_I2C display;
Adafruit_SGP30 sgp;
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();

// ---------------- FUNCTIONS ----------------
void playIndigoChime() {
  tone(BUZZER_PIN, 659); delay(400); 
  tone(BUZZER_PIN, 523); delay(600);
  noTone(BUZZER_PIN); 
}

void playErrorBeep() {
  tone(BUZZER_PIN, 400); delay(200);
  noTone(BUZZER_PIN);
  delay(100);
  tone(BUZZER_PIN, 400); delay(200);
  noTone(BUZZER_PIN);
}

void playSuccessBeep() {
  tone(BUZZER_PIN, 800); delay(100);
  noTone(BUZZER_PIN);
  delay(50);
  tone(BUZZER_PIN, 1000); delay(100);
  noTone(BUZZER_PIN);
}

// Send data to the Web App
void sendDataToWeb(float dust, float temp, int tvoc, int eco2) {
  if(WiFi.status() == WL_CONNECTED){
    HTTPClient http;
    
    // Start connection
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(10000); // 10 second timeout
    
    // Create JSON Payload
    String jsonPayload = "{";
    jsonPayload += "\"dust\":" + String(dust, 2) + ",";
    jsonPayload += "\"temp\":" + String(temp, 2) + ",";
    jsonPayload += "\"tvoc\":" + String(tvoc) + ",";
    jsonPayload += "\"eco2\":" + String(eco2);
    jsonPayload += "}";

    // Debug output
    Serial.println("\n--- Sending to Server ---");
    Serial.println("URL: " + String(serverName));
    Serial.println("Payload: " + jsonPayload);
    
    // Send POST Request
    int httpResponseCode = http.POST(jsonPayload);
    
    // Check Result
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("✓ SUCCESS! Response Code: ");
      Serial.println(httpResponseCode);
      Serial.println("Response: " + response);
      
      // Display success on OLED
      display.setCursor(0,0); 
      display.print("SENT OK!");
      playSuccessBeep();
    } else {
      Serial.print("✗ ERROR! Code: ");
      Serial.println(httpResponseCode);
      Serial.print("Error: ");
      Serial.println(http.errorToString(httpResponseCode));
      
      // Display error on OLED
      display.setCursor(0,0); 
      display.print("SEND FAIL");
      playErrorBeep();
    }
    
    http.end();
  } else {
    Serial.println("✗ WiFi Disconnected!");
    display.setCursor(0,0); 
    display.print("NO WIFI!");
    
    // Try to reconnect
    WiFi.disconnect();
    delay(100);
    WiFi.begin(STASSID, STAPSK);
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(DUST_PIN, INPUT);
  Wire.begin(); 

  // --- OLED INIT ---
  Serial.println("Initializing OLED...");
  display.begin();
  display.setPowerSave(0);
  display.setFlipMode(1);
  display.setFont(u8x8_font_chroma48medium8_r);
  display.clear();
  display.setCursor(0,0);
  display.print("AeroGuardian");
  display.setCursor(0,1);
  display.print("Starting...");

  // --- WIFI INIT ---
  Serial.println("\n--- WiFi Setup ---");
  Serial.print("Connecting to: ");
  Serial.println(STASSID);
  Serial.print("Password length: ");
  Serial.println(strlen(STAPSK));
  
  display.setCursor(0,3);
  display.print("WiFi...");
  
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);
  WiFi.begin(STASSID, STAPSK);
  
  while (WiFi.status() != WL_CONNECTED && wifiRetryCount < MAX_WIFI_RETRIES) {
    delay(500);
    Serial.print(".");
    wifiRetryCount++;
    
    // Print status code every 10 attempts
    if (wifiRetryCount % 10 == 0) {
      Serial.println();
      Serial.print("WiFi Status: ");
      Serial.print(WiFi.status());
      Serial.print(" | Attempt: ");
      Serial.println(wifiRetryCount);
    }
    
    if (wifiRetryCount % 5 == 0) {
      display.setCursor(0,4);
      display.print("Try: ");
      display.print(wifiRetryCount);
    }
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    
    display.setCursor(0,3); 
    display.print("WiFi OK!    ");
    display.setCursor(0,4);
    display.print(WiFi.localIP().toString().substring(0,15).c_str());
  } else {
    Serial.println("\n✗ WiFi Connection Failed!");
    Serial.print("Final WiFi Status: ");
    Serial.println(WiFi.status());
    Serial.println("\nStatus Codes:");
    Serial.println("0=IDLE, 1=NO_SSID, 3=CONNECTED, 4=FAILED, 6=DISCONNECTED");
    
    display.setCursor(0,3); 
    display.print("WiFi FAIL!");
    display.setCursor(0,4);
    display.print("Code:");
    display.print(WiFi.status());
    playErrorBeep();
  }
  
  delay(2000);

  // --- SENSORS INIT ---
  Serial.println("\n--- Sensor Setup ---");
  display.setCursor(0,5);
  
  if (!sgp.begin()) { 
    Serial.println("✗ SGP30 sensor not found!");
    display.print("SGP30 FAIL"); 
    playErrorBeep();
  } else { 
    Serial.println("✓ SGP30 sensor initialized");
    sgp.IAQinit(); 
    display.print("SGP30 OK  "); 
  }
  
  display.setCursor(0,6);
  if (!tempsensor.begin(0x18)) { 
    Serial.println("✗ MCP9808 sensor not found!");
    display.print("Temp FAIL"); 
    playErrorBeep();
  } else { 
    Serial.println("✓ MCP9808 sensor initialized");
    tempsensor.setResolution(1); 
    display.print("Temp OK   "); 
  }
  
  Serial.println("\n--- Setup Complete ---");
  Serial.print("Server endpoint: ");
  Serial.println(serverName);
  Serial.println("Ready to send data!\n");
  
  playIndigoChime();
  delay(1000);
  display.clear();
  starttime = millis(); 
}

void loop() {
  // Read Dust Sensor
  duration = pulseIn(DUST_PIN, LOW);
  lowpulseoccupancy += duration;
  
  // Read Air Quality Sensor
  if(sgp.IAQmeasure()){
    // Measurement successful
  } 

  // Update Cycle - Send data every sampletime_ms
  if ((millis() - starttime) > sampletime_ms) {
    
    // Calculate dust concentration
    ratio = lowpulseoccupancy / (sampletime_ms * 10.0);  
    dustConcentration = 1.1 * pow(ratio, 3) - 3.8 * pow(ratio, 2) + 520 * ratio + 0.62; 
    
    // Read temperature
    float cTemp = tempsensor.readTempC();
    
    // Display on OLED - Current readings
    display.clear();
    display.setCursor(0,1); 
    display.print("D:");
    display.print((int)dustConcentration); 
    display.setCursor(8,1); 
    display.print("T:");
    display.print((int)cTemp);
    
    display.setCursor(0,2); 
    display.print("V:");
    display.print(sgp.TVOC); 
    display.setCursor(8,2); 
    display.print("C:");
    display.print(sgp.eCO2);
    
    // Print to Serial
    Serial.println("========================================");
    Serial.println("Current Readings:");
    Serial.print("  Dust: "); Serial.print(dustConcentration, 1); Serial.println(" µg/m³");
    Serial.print("  Temp: "); Serial.print(cTemp, 1); Serial.println(" °C");
    Serial.print("  TVOC: "); Serial.print(sgp.TVOC); Serial.println(" ppb");
    Serial.print("  eCO2: "); Serial.print(sgp.eCO2); Serial.println(" ppm");
    
    // SEND TO WEB APP
    sendDataToWeb(dustConcentration, cTemp, sgp.TVOC, sgp.eCO2);
    
    // Alert system - Play chime if thresholds exceeded
    if (dustConcentration > THRESH_DUST || sgp.TVOC > THRESH_TVOC || 
        sgp.eCO2 > THRESH_ECO2 || cTemp > THRESH_TEMP) { 
       Serial.println("⚠️  ALERT: Threshold exceeded!");
       playIndigoChime(); 
       
       display.setCursor(0,7);
       display.print("! ALERT !");
    }
    
    Serial.println("========================================\n");

    // Reset for next cycle
    lowpulseoccupancy = 0;
    starttime = millis();
  }
  
  // Small delay to prevent CPU overload
  delay(10);
}
