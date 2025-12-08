# 🔧 ESP32 WiFi Troubleshooting Guide

## 🚨 Problem: "NO WIFI!" on OLED Display

### ✅ Quick Checklist - Do These First!

#### 1️⃣ **Verify WiFi Credentials**
Open `esp32_sensor_code.ino` and check:

```cpp
#define STASSID "YOUR_WIFI_NAME"    // ❌ Did you change this?
#define STAPSK  "YOUR_WIFI_PASSWORD" // ❌ Did you change this?
```

**Common Mistakes:**
- ❌ Left as "YOUR_WIFI_NAME" (placeholder text)
- ❌ Extra spaces in WiFi name
- ❌ Wrong capitalization (WiFi names are case-sensitive!)
- ❌ Special characters not escaped
- ❌ Password typo

**✅ Correct Example:**
```cpp
#define STASSID "MyHomeWiFi"      // Exact name from your router
#define STAPSK  "MyP@ssw0rd123"   // Exact password
```

#### 2️⃣ **Check WiFi Frequency**
- ⚠️ **ESP32 ONLY supports 2.4GHz WiFi**
- ❌ **ESP32 CANNOT connect to 5GHz WiFi**

**How to check:**
- Look at your router settings
- Most modern routers have both 2.4GHz and 5GHz
- They often have different names like:
  - `MyWiFi` (2.4GHz) ✅
  - `MyWiFi_5G` (5GHz) ❌

#### 3️⃣ **WiFi Signal Strength**
- Move ESP32 **closer to router** (within 5-10 meters for testing)
- Remove obstacles (walls, metal objects)
- Avoid interference from microwaves, Bluetooth devices

---

## 🔍 Debugging Steps

### Step 1: Open Serial Monitor

1. In Arduino IDE: **Tools → Serial Monitor**
2. Set baud rate to **115200**
3. Press ESP32 **RESET button**

### Step 2: Read the Output

**What you should see:**
```
--- WiFi Setup ---
Connecting to: YourWiFiName
.....
✓ WiFi Connected!
IP Address: 192.168.1.XXX
```

**If you see dots forever (.......):**
- WiFi credentials are wrong
- WiFi is 5GHz
- Signal too weak
- Router blocking ESP32

### Step 3: Common Error Messages

| Serial Output | Problem | Solution |
|--------------|---------|----------|
| `Connecting to: YOUR_WIFI_NAME` | ❌ You didn't change WiFi name | Update `STASSID` in code |
| Dots for 10+ seconds | ❌ Can't connect | Check credentials, frequency |
| `✗ WiFi Connection Failed!` | ❌ Max retries reached | Check all settings below |
| Nothing appears | ❌ Wrong baud rate | Set to 115200 |

---

## 🛠️ Solutions

### Solution 1: Verify WiFi Credentials (Most Common)

**Get your EXACT WiFi name:**

**Windows:**
```powershell
netsh wlan show interfaces
```
Look for: `SSID : YourWiFiName`

**Or check your phone:**
- Settings → WiFi → Connected network name
- Copy it EXACTLY (case-sensitive!)

**Update the code:**
```cpp
// BEFORE (Wrong):
#define STASSID "YOUR_WIFI_NAME"
#define STAPSK  "YOUR_WIFI_PASSWORD"

// AFTER (Correct):
#define STASSID "MyHomeNetwork"    // Replace with YOUR exact WiFi name
#define STAPSK  "mypassword123"    // Replace with YOUR exact password
```

**Re-upload to ESP32!**

---

### Solution 2: Check WiFi Frequency

**Is your WiFi 5GHz?**

Most routers broadcast TWO networks:
- `MyWiFi` - 2.4GHz ✅ Works with ESP32
- `MyWiFi_5G` - 5GHz ❌ ESP32 can't use this

**Options:**
1. **Connect to the 2.4GHz network** (recommended)
2. **Check router settings** to ensure 2.4GHz is enabled
3. **Separate 2.4GHz and 5GHz** in router settings (give them different names)

---

### Solution 3: Router Settings

**Some routers block new devices. Check:**

1. **Router Admin Panel** (usually http://192.168.1.1 or http://192.168.0.1)
2. **Security Settings:**
   - Disable MAC filtering temporarily
   - Ensure WPA2 is enabled (not WPA3 only)
   - Check if guest network isolation is enabled
3. **Allow new device** (ESP32 MAC address) if needed

---

### Solution 4: Special Characters in Password

**If your password has special characters:**

```cpp
// Escape special characters with backslash:
#define STAPSK  "My\"Pass\\Word"  // For: My"Pass\Word

// Common characters that may need escaping:
// " → \"
// \ → \\
// ' → \'
```

**Easier solution:** Temporarily change your WiFi password to something simple (no special chars) for testing.

---

### Solution 5: Increase Retry Count

If WiFi is slow to respond, increase timeout:

Find this line in the code (around line 114):
```cpp
const int MAX_WIFI_RETRIES = 20;
```

Change to:
```cpp
const int MAX_WIFI_RETRIES = 40;  // Give it more time
```

---

### Solution 6: Test with Phone Hotspot

**Quick test to isolate the problem:**

1. **Enable hotspot on your phone**
   - Name: `TestESP32`
   - Password: `12345678`

2. **Update ESP32 code:**
   ```cpp
   #define STASSID "TestESP32"
   #define STAPSK  "12345678"
   ```

3. **Upload and test**
   - If it works → Problem is with your main WiFi
   - If it doesn't work → Problem is with ESP32/code

---

## 🔬 Advanced Diagnostics

### Enable WiFi Debug Mode

Add this line after `WiFi.begin()` in the code:

```cpp
WiFi.setAutoReconnect(true);
WiFi.persistent(true);
Serial.setDebugOutput(true);  // Add this for detailed WiFi debug
```

This will show detailed WiFi connection logs in Serial Monitor.

---

## 📝 Updated Code Template

Here's a tested WiFi connection section with better error handling:

```cpp
// --- WIFI INIT ---
Serial.println("\n--- WiFi Setup ---");
Serial.print("Connecting to: ");
Serial.println(STASSID);

// Print WiFi mode and settings
WiFi.mode(WIFI_STA);
WiFi.setAutoReconnect(true);

// Start connection
WiFi.begin(STASSID, STAPSK);

display.setCursor(0,3);
display.print("WiFi...");

// Wait for connection
int wifiRetryCount = 0;
const int MAX_WIFI_RETRIES = 40;

while (WiFi.status() != WL_CONNECTED && wifiRetryCount < MAX_WIFI_RETRIES) {
  delay(500);
  Serial.print(".");
  wifiRetryCount++;
  
  // Show progress on OLED
  if (wifiRetryCount % 5 == 0) {
    display.setCursor(0,4);
    display.print("Try: ");
    display.print(wifiRetryCount);
  }
  
  // Print WiFi status for debugging
  if (wifiRetryCount % 10 == 0) {
    Serial.println();
    Serial.print("Status code: ");
    Serial.println(WiFi.status());
  }
}

// Check result
if (WiFi.status() == WL_CONNECTED) {
  Serial.println("\n✓ WiFi Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Signal Strength: ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
  
  display.setCursor(0,3);
  display.print("WiFi OK!    ");
} else {
  Serial.println("\n✗ WiFi Connection Failed!");
  Serial.print("Final status: ");
  Serial.println(WiFi.status());
  
  display.setCursor(0,3);
  display.print("WiFi FAIL!");
}
```

---

## 🎯 WiFi Status Codes Reference

If you see status codes in Serial Monitor:

| Code | Status | Meaning |
|------|--------|---------|
| 0 | `WL_IDLE_STATUS` | WiFi idle |
| 1 | `WL_NO_SSID_AVAIL` | ❌ WiFi name not found |
| 2 | `WL_SCAN_COMPLETED` | Scan complete |
| 3 | `WL_CONNECTED` | ✅ Connected! |
| 4 | `WL_CONNECT_FAILED` | ❌ Wrong password |
| 5 | `WL_CONNECTION_LOST` | Connection lost |
| 6 | `WL_DISCONNECTED` | Disconnected |

**Status 1 (WL_NO_SSID_AVAIL)** = Wrong WiFi name or 5GHz network
**Status 4 (WL_CONNECT_FAILED)** = Wrong password

---

## ✅ Verification Checklist

Before asking for more help, verify:

- [ ] WiFi credentials changed from placeholder text
- [ ] WiFi name copied EXACTLY (case-sensitive)
- [ ] WiFi password typed correctly
- [ ] WiFi is 2.4GHz (not 5GHz)
- [ ] ESP32 within 10 meters of router
- [ ] Code re-uploaded after changing credentials
- [ ] Serial Monitor set to 115200 baud
- [ ] Serial Monitor shows connection attempts (dots)
- [ ] Tried with phone hotspot (for testing)

---

## 🚀 Quick Fix Script

Use this to test WiFi credentials quickly:

Create a new Arduino sketch with JUST this:

```cpp
#include <WiFi.h>

const char* ssid = "YourWiFiName";      // CHANGE THIS
const char* password = "YourPassword";   // CHANGE THIS

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("\n\n=== WiFi Test ===");
  Serial.print("Connecting to: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int count = 0;
  while (WiFi.status() != WL_CONNECTED && count < 40) {
    delay(500);
    Serial.print(".");
    count++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ SUCCESS!");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n✗ FAILED");
    Serial.print("Status: ");
    Serial.println(WiFi.status());
  }
}

void loop() {
  // Nothing
}
```

Upload this simple test first. If it works, your credentials are correct!

---

## 📞 Still Not Working?

**Provide this info:**

1. **Serial Monitor output** (copy and paste)
2. **WiFi router model**
3. **WiFi frequency** (2.4GHz or 5GHz?)
4. **ESP32 board model**
5. **Distance from router**
6. **Did phone hotspot test work?**

---

## 🎓 Common Scenarios

### Scenario 1: "Connecting to: YOUR_WIFI_NAME"
**❌ You didn't change the WiFi credentials!**
- Open `esp32_sensor_code.ino`
- Find lines 11-12
- Replace `"YOUR_WIFI_NAME"` and `"YOUR_WIFI_PASSWORD"` with actual values
- Click Upload button again

### Scenario 2: Dots forever, then "WiFi FAIL!"
**❌ Wrong credentials or 5GHz WiFi**
- Verify WiFi name is EXACTLY correct (case-sensitive)
- Check password has no typos
- Ensure using 2.4GHz network
- Try phone hotspot test

### Scenario 3: "Status code: 1" in Serial Monitor
**❌ WiFi network not found**
- WiFi name is wrong
- Router is off
- ESP32 too far away
- Using 5GHz network (ESP32 can't see it)

### Scenario 4: "Status code: 4" in Serial Monitor
**❌ Wrong password**
- Double-check password
- Check for special characters
- Try simple password temporarily

---

**💡 Pro Tip:** Start simple! Use a phone hotspot with a simple name like "ESP32Test" and password "12345678" to verify the ESP32 works, then switch to your main WiFi.
