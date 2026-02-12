# 🔌 PeatGuard Hardware Wiring Guide

## 📦 What You Have

- ✅ Seeed Studio XIAO ESP32S3
- ✅ Board Base for XIAO with Grove OLED Display
- ✅ Grove 8 Channel I2C Hub (TCA9548A)
- ✅ SGP30 VOC Sensor
- ✅ PMS5003 PM2.5 Sensor
- ✅ Grove Dust Sensor
- ✅ MCP9808 Temperature & Humidity Sensor
- ✅ Grove Ultrasonic Ranger
- ✅ Grove TDS Sensor
- ✅ Grove Water Sensor
- ✅ Grove Relay (5V/10A)
- ⛔ ~~CP2102 USB to TTL UART Converter~~ **NOT NEEDED - PMS5003 connects directly!**
- ✅ Grove cables and jumper wires
- ✅ Breadboard

---

## ⚡ STEP-BY-STEP WIRING

### **STEP 1: Mount XIAO ESP32S3 on Base Board**

1. **Take the Board Base for XIAO with Grove OLED**
2. **Insert XIAO ESP32S3** into the socket on the base board
   - Make sure all pins align correctly
   - Press firmly but gently until seated
3. **OLED Display is already connected** (built into base board)
   - OLED uses I2C pins on the base

✅ **Result:** You now have XIAO + OLED as one unit

---

### **STEP 2: Connect I2C Hub (TCA9548A)**

The I2C Hub prevents address conflicts and lets you connect multiple I2C devices.

**Connection:**
```
Base Board I2C Grove Connector → Grove Cable → I2C Hub Input
```

**Details:**
- Use a Grove 4-pin cable
- Connect from **I2C connector on base board** to **IN port on TCA9548A hub**
- The hub has 8 output channels (CH0-CH7)

✅ **Result:** I2C hub is now the master, manages all I2C sensors

---

### **STEP 3: Connect Fire Detection Sensors**

#### **3A: SGP30 VOC Sensor** (Fire gas detection)

```
I2C Hub CH0 → Grove Cable → SGP30 VOC Sensor
```

- Connect SGP30 to **Channel 0** on I2C Hub
- I2C Address: 0x58

#### **3B: MCP9808 Temperature & Humidity Sensor**

```
I2C Hub CH1 → Grove Cable → MCP9808 Temp/Humidity
```

- Connect MCP9808 to **Channel 1** on I2C Hub
- I2C Address: 0x18

#### **3C: Grove Dust Sensor** (Backup PM2.5)

```
I2C Hub CH2 → Grove Cable → Grove Dust Sensor
```

- Connect Dust Sensor to **Channel 2** on I2C Hub
- I2C Address: 0x52

✅ **Result:** 3 I2C fire sensors connected through hub

---

### **STEP 4: Connect PMS5003 (Professional PM2.5 Sensor)**

The PMS5003 uses UART, not I2C. **Connect it directly to ESP32 - NO CP2102 needed!**

**Direct Connection (RECOMMENDED):**

```
PMS5003 → XIAO ESP32S3 Direct Connection

PMS5003 Pin 1 (VCC) → XIAO 5V pin
PMS5003 Pin 2 (GND) → XIAO GND
PMS5003 Pin 4 (RXD) → XIAO GPIO 43 (TX)  ← Note: Cross connection!
PMS5003 Pin 5 (TXD) → XIAO GPIO 44 (RX)  ← Cross RX/TX
```

**PMS5003 Pinout:** 
```
Pin 1: VCC (5V power input)
Pin 2: GND (ground)
Pin 3: SET (leave unconnected for continuous mode)
Pin 4: RXD (receives commands) → Connect to XIAO TX
Pin 5: TXD (sends data) → Connect to XIAO RX
Pin 6-8: Not used
```

**Why No CP2102 Needed?**
- PMS5003 uses 3.3V TTL UART (ESP32 compatible!)
- CP2102 is only for USB-to-computer connection
- Direct ESP32 connection is simpler and more reliable

**Direct Connection vs CP2102:**

| Feature | Direct Connection ✅ | With CP2102 ⛔ |
|---------|---------------------|---------------|
| Wiring Complexity | 4 wires | 8 wires |
| Components Needed | PMS5003 only | PMS5003 + CP2102 |
| Signal Quality | Direct (best) | Two conversions (worse) |
| Power Consumption | 100mA | 120mA (adds 20mA) |
| Cost | $0 extra | $5-10 extra |
| Failure Points | 1 (sensor) | 2 (sensor + converter) |

**Wiring Tips:**
- Use **jumper wires** or solder directly
- **Cross TX/RX:** XIAO TX goes to PMS RX, and vice versa
- PMS5003 needs **5V power** but data pins are 3.3V (perfect!)
- Make sure GND is common with all other sensors

✅ **Result:** Professional laser PM2.5 sensor connected directly via UART

---

### **STEP 5: Connect Flood Detection Sensors**

#### **5A: Grove TDS Sensor** (Salinity measurement)

```
XIAO GPIO 1 (A0) → Grove TDS Sensor Signal Pin
```

- TDS is **analog sensor**
- Connect using Grove cable or jumper wires:
  - TDS Signal (Yellow) → XIAO GPIO 1 (A0)
  - TDS VCC (Red) → XIAO 3.3V
  - TDS GND (Black) → XIAO GND

#### **5B: Grove Water Sensor** (Water presence detection)

```
XIAO GPIO 2 (A1) → Grove Water Sensor Signal Pin
```

- Water Sensor is **analog**
- Connect:
  - Water Sensor Signal → XIAO GPIO 2 (A1)
  - Water Sensor VCC → XIAO 3.3V
  - Water Sensor GND → XIAO GND

#### **5C: Grove Ultrasonic Ranger** (Water level measurement)

```
XIAO GPIO 6 → Grove Ultrasonic Ranger
```

- Ultrasonic is **digital** (single pin for trigger/echo)
- Connect using Grove cable:
  - Ultrasonic SIG → XIAO GPIO 6
  - Ultrasonic VCC → XIAO 5V
  - Ultrasonic GND → XIAO GND

✅ **Result:** 3 flood sensors connected (analog + digital)

---

### **STEP 6: Connect Grove Relay** (For alarm/siren)

```
XIAO GPIO 7 → Grove Relay
```

- Relay is **digital output**
- Connect:
  - Relay Signal → XIAO GPIO 7
  - Relay VCC → XIAO 5V
  - Relay GND → XIAO GND
  
**Later:** Connect siren/alarm to relay output terminals (COM, NO)

✅ **Result:** Relay ready to control alarms

---

## 🎨 COMPLETE WIRING DIAGRAM

```
┌─────────────────────────────────────────────────────────┐
│         XIAO ESP32S3 + Base Board + OLED               │
│                                                         │
│  GPIO 1 (A0) ────→ TDS Sensor (analog)                │
│  GPIO 2 (A1) ────→ Water Sensor (analog)              │
│  GPIO 6 ──────────→ Ultrasonic Ranger (digital)       │
│  GPIO 7 ──────────→ Relay (digital)                   │
│  GPIO 43 (TX) ────→ PMS5003 RXD (direct!)            │
│  GPIO 44 (RX) ←──── PMS5003 TXD (direct!)            │
│  5V ──────────────→ PMS5003 VCC                       │
│  GND ─────────────→ PMS5003 GND                       │
│                                                         │
│  I2C Grove Port ───→ TCA9548A I2C Hub (IN)            │
└─────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │       TCA9548A I2C Hub (8 Channels)     │
         │                                         │
         │  CH0 ─→ SGP30 VOC Sensor               │
         │  CH1 ─→ MCP9808 Temp/Humidity          │
         │  CH2 ─→ Grove Dust Sensor              │
         │  CH3-7 ─→ Reserved                     │
         └─────────────────────────────────────────┘
```

---

## 🔋 POWER REQUIREMENTS

**Power from USB (5V):**
- XIAO ESP32S3: ~200mA
- PMS5003: 100mA (max)
- All other sensors: ~50mA total
- **Total: ~350mA** (well within USB 500mA limit)
- ✅ **Saved 20mA** by removing CP2102!

**Power Distribution:**
- USB powers XIAO
- XIAO 5V pin powers: PMS5003, ultrasonic, relay
- XIAO 3.3V pin powers: TDS, water sensor
- I2C Hub gets 3.3V from base board

✅ **USB power is sufficient** - no external power needed!

---

## ⚠️ IMPORTANT NOTES

### **I2C Address Conflict Prevention**
The TCA9548A hub **eliminates address conflicts** by switching between channels:
- Each sensor gets its own dedicated channel
- No two sensors communicate simultaneously
- Professional solution!

### **Ground All Sensors**
Make sure **all GND pins are connected** to XIAO GND:
- Common ground is critical for analog sensors
- Use breadboard to create common GND bus if needed

### **3.3V vs 5V**
- **3.3V sensors:** TDS, Water Sensor
- **5V sensors:** PMS5003, Ultrasonic, Relay
- **I2C sensors:** Get voltage from base board (typically 3.3V)

### **UART vs I2C**
- **UART:** PMS5003 only (TX/RX pins)
- **I2C:** All other sensors (through hub)
- These are **separate communication methods**

---

## 🧪 TESTING CHECKLIST

After wiring, test each sensor individually:

### 1. **OLED Display Test**
- Upload simple sketch to display "Hello"
- If OLED works, I2C communication is good

### 2. **I2C Sensor Scan**
- Run I2C scanner sketch
- Should detect TCA9548A hub address (0x70)
- Switch channels and detect SGP30, MCP9808, Dust sensor

### 3. **PMS5003 Test**
- Upload UART read sketch
- Should receive PM2.5 data packets
- Check for valid readings (not all zeros)

### 4. **Analog Sensors Test**
- Read TDS sensor (GPIO 1): Should show ~0-1023 value
- Read Water sensor (GPIO 2): Dry = low, wet = high
- Test by touching water sensor with wet finger

### 5. **Ultrasonic Test**
- Upload ultrasonic sketch
- Point at object, should show distance in cm
- Range: 3-400cm

### 6. **Relay Test**
- Toggle relay HIGH/LOW
- Should hear clicking sound
- LED on relay should turn on/off

---

## 🚀 NEXT STEPS

1. **Wire everything** following this guide
2. **Upload test firmware** (I'll help you with this)
3. **Verify each sensor** works individually
4. **Upload complete PeatGuard firmware**
5. **Calibrate sensors** (TDS, ultrasonic)
6. **Mount in weatherproof enclosure**
7. **Deploy to peatland!** 🌿

---

## 📸 PHOTO CHECKLIST

Before powering on, verify:
- ✅ XIAO seated correctly on base board
- ✅ All Grove cables connected firmly
- ✅ PMS5003 wired correctly (RX↔TX crossed)
- ✅ TDS and water sensor on analog pins
- ✅ All grounds connected
- ✅ No loose wires
- ✅ USB cable ready to power XIAO

---

## 🆘 TROUBLESHOOTING

**OLED doesn't display:**
- Check I2C hub connection
- Try connecting OLED directly to base board I2C

**PMS5003 no data:**
- Verify RX↔TX are crossed (XIAO TX → PMS5003 RX)
- Check 5V power to PMS5003
- Wait 30 seconds for warmup

**I2C sensor not detected:**
- Run I2C scanner
- Check TCA9548A hub connection
- Verify Grove cables are good

**Analog sensors give weird readings:**
- Check common ground connection
- Verify 3.3V power
- Test with multimeter

**Relay doesn't click:**
- Check 5V power
- Verify GPIO 7 connection
- Test with LED first (to verify GPIO works)

---

Ready to start wiring? Let me know which sensor you want to connect first, or if you need clarification on any steps!
