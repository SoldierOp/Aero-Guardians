# 🔧 PeatSense Hardware Guide

Complete hardware specifications and assembly instructions for the PeatSense peatland monitoring system.

---

## 📦 Complete Bill of Materials (BOM)

### Core Controller Unit
| Component | Model | Quantity | Price (USD) | Purpose |
|-----------|-------|----------|-------------|---------|
| XIAO ESP32S3 | Seeed Studio | 1 | $6.90 | Main microcontroller with WiFi/BT |
| Grove Base Board for XIAO | Seeed Studio | 1 | $7.90 | Provides Grove ports + OLED display |
| Grove I2C Hub (6-port) | Seeed Studio | 1 | $4.90 | Expands I2C sensor capacity |

**Subtotal: $19.70**

### Water Monitoring Sensors
| Component | Model | Quantity | Price (USD) | Purpose |
|-----------|-------|----------|-------------|---------|
| Grove Ultrasonic Distance Sensor | HC-SR04 | 1 | $4.90 | Measures water level in canal |
| Grove TDS Sensor | Gravity Analog | 1 | $9.90 | Total Dissolved Solids (salinity proxy) |
| USB-to-UART Grove Adapter | Seeed Studio | 1 | $4.90 | Interfaces with TDS sensor |

**Subtotal: $19.70**

### Fire Risk & Air Quality Sensors
| Component | Model | Quantity | Price (USD) | Purpose |
|-----------|-------|----------|-------------|---------|
| Grove VOC & eCO₂ Sensor | SGP30 | 1 | $9.90 | Detects peat drying/burning gases |
| Grove Dust Sensor | PPD42NS | 1 | $8.90 | PM2.5 smoke/haze detection |
| Grove Temperature & Humidity Sensor | MCP9808 | 1 | $5.90 | Microclimate monitoring |

**Subtotal: $24.70**

### Connectivity & Power
| Component | Model | Quantity | Price (USD) | Purpose |
|-----------|-------|----------|-------------|---------|
| Grove 4-pin cables | 20cm | 10 | $4.90 | Connect all Grove modules |
| USB-C cable | 1m | 1 | $2.50 | Power and programming |
| Solar charging board | Seeed Solar Charger | 1 | $8.90 | Field power management |
| 5V Solar panel | 5W | 1 | $12.90 | Outdoor power source |
| LiPo battery | 3.7V 2500mAh | 1 | $7.90 | Backup power |

**Subtotal: $37.10**

### Enclosure & Display
| Component | Model | Quantity | Price (USD) | Purpose |
|-----------|-------|----------|-------------|---------|
| Weatherproof enclosure | IP65 | 1 | $15.00 | Protects electronics from elements |
| RGB LED strip | WS2812 | 1 | $3.90 | Physical risk indicator |
| Buzzer module | Grove | 1 | $2.90 | Local audio alerts |

**Subtotal: $21.80**

---

## 💰 Total System Cost

| Category | Cost (USD) |
|----------|-----------|
| Core Controller | $19.70 |
| Water Monitoring | $19.70 |
| Fire Risk Sensors | $24.70 |
| Power & Connectivity | $37.10 |
| Enclosure & Display | $21.80 |
| **TOTAL** | **$123.00** |

**Target cost reduction strategies:**
- Use local solar panels (reduce by $10)
- 3D print enclosure (reduce by $10)
- Bulk purchasing (10+ units: ~$100/unit)

---

## 🔌 Pin Mapping & Connections

### XIAO ESP32S3 Grove Base Board Ports

```
Grove Base Board Layout:
┌─────────────────────────────────────┐
│   [OLED Display - Built-in]         │
├─────────────────────────────────────┤
│  I2C Port 1  │  I2C Port 2          │
│  ═══════════ │  ═══════════         │
│  To I2C Hub  │  (Reserved)          │
├──────────────┴──────────────────────┤
│  A0/A1 Port         D0/D1 Port      │
│  ═══════════        ═══════════     │
│  TDS Sensor         Ultrasonic      │
└─────────────────────────────────────┘
```

### Grove I2C Hub Connections (6-port)
```
Port 1: Grove SGP30 (VOC & eCO₂)
Port 2: Grove Dust Sensor (I2C mode)
Port 3: Grove MCP9808 (Temperature & Humidity)
Port 4: RGB LED strip (I2C addressable)
Port 5: Grove Buzzer
Port 6: (Reserved for expansion)
```

### Detailed Pin Assignments

#### Water Level Sensor (Grove Ultrasonic HC-SR04)
- **Port**: D0/D1 Digital Port
- **Trigger Pin**: D0 (GPIO 1)
- **Echo Pin**: D1 (GPIO 2)
- **Power**: 5V from Grove port
- **Protocol**: Digital pulse timing

#### TDS Sensor (Salinity)
- **Port**: A0/A1 Analog Port
- **Signal Pin**: A0 (GPIO 26)
- **Power**: 5V from USB-UART adapter
- **Protocol**: Analog voltage (0-5V)
- **Calibration**: TDS ppm = (133.42 × voltage³ - 255.86 × voltage² + 857.39 × voltage) × 0.5

#### SGP30 VOC Sensor
- **Port**: I2C Hub Port 1
- **Address**: 0x58
- **SDA/SCL**: Via I2C hub
- **Protocol**: I2C
- **Warm-up**: 15 seconds

#### Dust Sensor (PM2.5)
- **Port**: I2C Hub Port 2
- **Address**: 0x69
- **Protocol**: I2C
- **Range**: 0-500 µg/m³

#### MCP9808 Temperature/Humidity
- **Port**: I2C Hub Port 3
- **Address**: 0x18
- **Protocol**: I2C
- **Accuracy**: ±0.25°C

#### RGB LED Status Indicator
- **Port**: I2C Hub Port 4
- **Type**: WS2812 addressable
- **Count**: 8 LEDs
- **Colors**:
  - Green: Safe conditions
  - Yellow: Warning level
  - Red: Danger (flood or fire risk)
  - Blue: Offline/maintenance mode

---

## 🛠️ Assembly Instructions

### Step 1: Base Setup (10 minutes)
1. Mount XIAO ESP32S3 onto Grove Base Board
2. Ensure it clicks into place securely
3. Connect USB-C cable to computer for initial testing
4. Verify OLED display powers on

### Step 2: I2C Hub Installation (5 minutes)
1. Connect Grove I2C Hub to **I2C Port 1** on base board
2. Use included 4-pin Grove cable
3. Ensure cable is fully seated in both connectors

### Step 3: Water Monitoring Sensors (15 minutes)

**Ultrasonic Sensor (Water Level):**
1. Connect to **D0/D1 port** on base board
2. Mount sensor 50cm above expected maximum water level
3. Point sensor straight down at water surface
4. Secure with waterproof mounting bracket
5. Shield sensor from direct rain with small hood

**TDS Sensor (Salinity):**
1. Connect TDS probe to USB-UART adapter
2. Connect adapter to **A0/A1 port**
3. Probe must be submerged at consistent depth (mark on probe)
4. Use PVC pipe holder to keep probe at fixed position
5. Clean probe monthly with distilled water

### Step 4: Fire Risk Sensors (15 minutes)

**SGP30 VOC Sensor:**
1. Connect to **I2C Hub Port 1**
2. Mount in well-ventilated area
3. Protect from direct water but allow airflow
4. Allow 15-minute warm-up before first readings

**Dust Sensor:**
1. Connect to **I2C Hub Port 2**
2. Mount horizontally with inlet facing ambient air
3. Keep inlet free from obstructions
4. Clean inlet screen monthly

**Temperature/Humidity Sensor:**
1. Connect to **I2C Hub Port 3**
2. Mount in shaded location
3. Avoid direct sunlight and rain
4. Provide ventilation around sensor

### Step 5: Status Indicators (10 minutes)

**RGB LED Strip:**
1. Connect to **I2C Hub Port 4**
2. Mount on exterior of enclosure (visible from distance)
3. Use clear waterproof adhesive
4. Test color changes: Green → Yellow → Red

**Buzzer:**
1. Connect to **I2C Hub Port 5**
2. Mount inside enclosure near ventilation holes
3. Adjust volume with potentiometer (if available)

### Step 6: Power System (20 minutes)

**Lab/Testing Mode:**
- Simply use USB-C cable to 5V USB power adapter
- Good for indoor testing and initial development

**Field Deployment Mode:**
1. Install solar charging board on XIAO ESP32S3
2. Connect LiPo battery to charging board
3. Connect 5V solar panel to charging input
4. Mount solar panel facing south (in Northern Hemisphere) at 15° angle
5. Secure all connections with hot glue
6. Test battery charging in sunlight

### Step 7: Enclosure Assembly (30 minutes)

1. **Drill mounting holes** in weatherproof enclosure:
   - Ultrasonic sensor mount (top)
   - TDS probe cable gland (bottom)
   - RGB LED window (front)
   - Ventilation holes with dust filters (sides)

2. **Mount electronics inside:**
   - Secure base board with standoffs
   - Use cable ties for wire management
   - Leave access to USB-C port for programming

3. **Seal all penetrations:**
   - Use silicone sealant around cable glands
   - Apply weatherproof membrane over ventilation holes
   - Ensure IP65 rating maintained

4. **Final checks:**
   - All sensors accessible for cleaning
   - OLED display visible through clear window
   - RGB LED visible from 50m distance
   - USB-C accessible without opening enclosure

---

## 📏 Physical Installation Guide

### Site Selection
1. **Location**: Beside peat canal or field
2. **Height**: 1.5m above ground (flood protection)
3. **Distance to water**: Ultrasonic range 2cm-400cm
4. **Sunlight**: Solar panel needs 4+ hours direct sun
5. **Accessibility**: Reachable for monthly maintenance

### Mounting Structure
```
     [Solar Panel]
          │
    ╔═════╪═════╗
    ║  [ENCLOS] ║  ← 1.5m above ground
    ║   URE     ║
    ╚═══════════╝
          │
    [Support Pole]
          │
     [Ground Level]
          │
   [Water Surface] ← Ultrasonic measures this
          │
    [Canal Bottom]
```

### Water Sensor Positioning

**Ultrasonic Sensor:**
- Install 50cm above maximum expected water level
- Clear line of sight to water (no vegetation)
- Measures 0-400cm range
- Update firmware with "zero point" (distance to canal bottom)

**TDS Probe:**
- Constant depth: 10cm below minimum water level
- Fixed mounting with PVC pipe guide
- Monthly cleaning essential for accuracy
- Calibration: 0ppm (distilled water), 1413ppm (calibration solution)

---

## 🔬 Sensor Calibration Procedures

### Initial Calibration (Before Deployment)

**1. TDS Sensor Calibration**
```
Equipment needed:
- Distilled water (0 TDS)
- 1413 µS/cm calibration solution
- Clean containers

Steps:
1. Rinse probe with distilled water
2. Immerse in 0 TDS water → record voltage = V0
3. Immerse in 1413 µS/cm solution → record voltage = V1
4. Update firmware calibration coefficients
5. Verify readings: distilled (0-10 ppm), tap water (~100-300 ppm)
```

**2. Ultrasonic Sensor Calibration**
```
Steps:
1. Measure exact distance from sensor to canal bottom (D_total)
2. Update firmware: CANAL_DEPTH = D_total
3. Test by measuring known distances
4. Water level = CANAL_DEPTH - measured_distance
```

**3. SGP30 VOC Sensor**
```
No manual calibration needed - auto-calibrates over 12 hours
First deployment: Allow 24h outdoor exposure before trusting readings
Baseline values will stabilize after 1 week
```

### Monthly Maintenance Calibration

- **TDS**: Verify with calibration solution, clean probe
- **Ultrasonic**: Check for sensor fouling, clean ultrasonic transducer
- **Dust Sensor**: Clean inlet filter, verify zero reading in clean air
- **All sensors**: Visual inspection for corrosion, water ingress

---

## 🔋 Power Consumption & Battery Life

### Power Budget (Typical Operation)

| Component | Current Draw | Duty Cycle | Avg Power |
|-----------|--------------|------------|-----------|
| XIAO ESP32S3 (active) | 180 mA | 30% | 54 mA |
| XIAO ESP32S3 (sleep) | 15 µA | 70% | ~0 mA |
| SGP30 VOC | 48 mA | 100% | 48 mA |
| Dust Sensor | 90 mA | 10% | 9 mA |
| TDS Sensor | 5 mA | 10% | 0.5 mA |
| Ultrasonic | 15 mA | 1% | 0.15 mA |
| MCP9808 | 0.4 mA | 100% | 0.4 mA |
| OLED Display | 20 mA | 50% | 10 mA |
| RGB LED | 60 mA | 20% | 12 mA |
| **TOTAL** | | | **134 mA** |

### Battery Life Calculations

**With 2500 mAh LiPo battery:**
- Theoretical runtime: 2500 mAh / 134 mA = **18.6 hours**
- Real-world (80% depth of discharge): **~15 hours**

**With 5W solar panel (average 3 hours sun/day):**
- Solar charging: 5W / 3.7V = 1350 mA
- Daily harvest: 1350 mA × 3 hours = **4050 mAh**
- Daily consumption: 134 mA × 24 hours = **3216 mAh**
- **Surplus: 834 mAh/day** → Indefinite operation

### Power Optimization Tips
1. Enable deep sleep between readings (30-second intervals)
2. Disable OLED during nighttime (8pm-6am)
3. Reduce RGB LED brightness (50% sufficient)
4. WiFi only transmits every 5 minutes (MQTT buffer locally)

---

## 🌧️ Weatherproofing & Environmental Protection

### IP Rating Target: IP65
- **IP6X**: Dust-tight (complete protection)
- **IPX5**: Water jets from any direction

### Weatherproofing Checklist
- ✅ Sealed enclosure with gasket
- ✅ Cable glands for all external wires
- ✅ Silicone sealant on all penetrations
- ✅ Ventilation holes with Gore-Tex membrane (breathable, waterproof)
- ✅ Ultrasonic sensor rain hood (doesn't block beam)
- ✅ TDS probe cable sealed with heat shrink + silicone
- ✅ Solar panel mounted with stainless steel hardware
- ✅ Conformal coating on PCBs (optional for humid climates)

### Expected Operational Environment
- **Temperature**: 20°C - 35°C (tropical)
- **Humidity**: 70% - 95% RH
- **Rain**: Heavy monsoon (direct water jets)
- **Dust**: Peat fire smoke and ash
- **Submersion**: NO (mount above flood level)

---

## 🧪 Lab Testing Setup (Before Field Deployment)

### Simulated Peat Environment

**Materials needed:**
- Large cardboard box (60cm × 40cm × 40cm)
- Water container (simulates canal)
- Incense sticks (simulates peat smoke)
- Salt solution (simulates saltwater intrusion)
- Ruler for water level reference

**Test Protocol:**

**1. Water Level Detection (30 min)**
```
- Fill water container to 10cm depth
- Mount ultrasonic sensor 30cm above water
- Verify reading: ~20cm
- Add water to 20cm → verify reading ~10cm
- Trigger flood alert threshold
```

**2. Salinity Detection (30 min)**
```
- Start with fresh water → TDS ~0 ppm
- Add 1 tablespoon salt → TDS ~500-1000 ppm
- Add more salt → TDS >2000 ppm (danger)
- Verify agricultural thresholds:
  • Fresh (<500 ppm): Safe for rice
  • Brackish (500-2000 ppm): Warning
  • Saline (>2000 ppm): Danger, crop loss
```

**3. Fire Risk Simulation (20 min)**
```
- Burn incense stick near sensors
- SGP30 VOC should spike >1000 ppb
- Dust sensor PM2.5 should rise >100 µg/m³
- Humidity drops trigger warning state
- Verify fire alert triggers correctly
```

**4. Combined Hazard Test (20 min)**
```
- Simulate both flood + fire scenarios simultaneously
- Verify system prioritizes most critical hazard
- Check OLED display shows correct status
- Confirm RGB LED matches risk level
- Test offline mode (disconnect WiFi)
```

---

## 🔧 Troubleshooting Guide

### Common Issues & Solutions

**Ultrasonic sensor reads 0 or unstable:**
- Check cable connections (D0/D1)
- Ensure sensor faces flat water surface
- Remove any foam/debris on transducer
- Verify voltage: should be 5V on Vcc pin

**TDS sensor always reads high:**
- Clean probe with distilled water + soft brush
- Check for polarization damage (reverse polarity)
- Recalibrate with known solutions
- Replace probe if readings don't stabilize

**SGP30 VOC sensor shows 400 ppb constantly:**
- Normal initial reading during warm-up
- Allow 15 min warm-up time
- Check I2C address (should be 0x58)
- Verify good airflow around sensor

**WiFi won't connect:**
- Check SSID and password in firmware
- Verify 2.4 GHz network (ESP32 doesn't support 5 GHz)
- Reduce distance to router (<30m)
- Check for WiFi interference
- Enable offline mode in firmware

**Battery drains quickly (<8 hours):**
- Check solar panel voltage (should be 5-6V in sun)
- Verify battery connection polarity
- Measure actual current draw (should be <150 mA avg)
- Disable power-hungry features (OLED dim, reduce RGB)

**OLED display is blank:**
- Check power LED on Grove base board
- Verify USB-C connection
- Re-seat ESP32S3 on base board
- Test with simple display code

---

## 📦 Recommended Suppliers

### International (Ships Worldwide)
- **Seeed Studio**: Grove system components (official)
- **Adafruit**: Alternative sensors and power components
- **DFRobot**: TDS sensor and analog sensors
- **AliExpress**: Low-cost bulk Grove cables and enclosures

### Indonesia Local Suppliers
- **Tokopedia**: Electronics marketplace (Jakarta)
- **Bukalapak**: Local electronics
- **Distrelec**: Industrial components
- **Local electronics markets**: Glodok (Jakarta), ITC Surabaya

### Budget Optimization
- Order Grove sensors as kit from Seeed (10-20% discount)
- Source solar panels locally in Indonesia (avoid import fees)
- 3D print custom enclosures (STL files in `/hardware` folder)
- Use recycled waterproof containers (cleaned food containers)

---

## 🎓 Community Training Materials

### Installation Workshop (2 hours)
**Target audience**: Village technicians, farmer leaders

**Topics covered:**
1. Basic electronics safety
2. Grove system plug-and-play assembly
3. Sensor mounting and positioning
4. Solar panel installation
5. Basic troubleshooting
6. Monthly maintenance procedures

**Materials needed:**
- Printed installation manual (this document)
- One complete kit for demonstration
- Toolkit: screwdrivers, wire cutters, multimeter
- Laminated quick reference cards

### Maintenance Training (1 hour)
**Monthly tasks:**
- Clean TDS probe
- Check solar panel for debris
- Verify all cable connections
- Test battery voltage
- Clean ultrasonic sensor
- Verify sensor readings against manual measurements

**Quarterly tasks:**
- Full system test with simulated flood/fire
- Recalibrate TDS sensor
- Check enclosure seals
- Update firmware if available

---

## 📞 Technical Support

**For hardware issues:**
- PM.Haze field coordinator: [Contact info]
- Seeed Studio support: forum.seeedstudio.com
- Community Discord: [Link to project Discord]

**For replacement parts:**
- Order form: [Link to Google Form]
- Lead time: 2-3 weeks from Seeed Studio
- Local spare parts inventory at PM.Haze Riau office

---

## 🔮 Future Hardware Upgrades

### Version 2.0 Roadmap (6-12 months)
- **LoRa radio module**: Mesh network between nodes (no internet required)
- **Soil moisture sensor**: Direct peat dryness measurement
- **pH sensor**: Water acidity for agriculture
- **Camera module**: Visual verification of water level
- **Cellular backup**: 4G LTE for areas without WiFi

### Community Requests
- Solar panel tilt adjustment (optimize for seasonal sun angle)
- Larger battery (3-day autonomy during monsoon)
- Louder buzzer for village-wide alerts
- Integration with existing sirens/alarm systems

---

**Last Updated**: January 2026  
**Document Version**: 1.0  
**Hardware Version**: PeatSense v1.0  
**Target Deployment**: Sungai Tohor, Riau, Indonesia
