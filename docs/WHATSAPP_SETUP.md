# WhatsApp Alert Configuration

## Overview
PeatSense sends critical alerts to village leaders via WhatsApp when dangerous conditions are detected.

## Alert Rules

### What Gets Sent
✅ **DANGER level alerts only** (critical situations)
- 🌊 **Flood DANGER**: Water level > 150 cm OR Salinity > 2000 ppm
- 🔥 **Fire DANGER**: VOC > 1500 ppb OR PM2.5 > 250 µg/m³

### What Doesn't Get Sent
❌ **WARNING level alerts** (stored in database but no WhatsApp)
- Water level 100-150 cm
- VOC 800-1500 ppb
- PM2.5 100-250 µg/m³

### Cooldown Protection
⏰ **60 minutes between alerts** per node/type
- Prevents spam from continuous dangerous conditions
- Resets after 1 hour
- Each node and alert type tracked separately

## Message Format

### Flood Alert (Indonesian)
```
🚨 *PERINGATAN BANJIR*

Lokasi: SungaiTohor_Node01
Status: DANGER

Ketinggian Air: 165.0 cm
Salinitas: 2100 ppm

Air sangat tinggi! Risiko banjir.

Segera koordinasikan evakuasi jika diperlukan.
Salam, PeatSense System
```

### Fire Alert (Indonesian)
```
🔥 *PERINGATAN KEBAKARAN*

Lokasi: SungaiTohor_Node01
Status: DANGER

Gas VOC: 1650 ppb
Asap (PM2.5): 280 µg/m³

Asap tinggi! Risiko kebakaran.

Aktifkan tim pemadam kebakaran desa.
Salam, PeatSense System
```

## Twilio Setup

### 1. Get Twilio Account
1. Sign up at [twilio.com](https://www.twilio.com/try-twilio)
2. Verify your account with phone number
3. Get free trial credits ($15 USD)

### 2. WhatsApp Sandbox (Testing)
1. Go to **Console → Messaging → Try it out → Send a WhatsApp message**
2. Scan QR code or send join code to Twilio sandbox number
3. Use sandbox number for testing: `whatsapp:+14155238886`

### 3. Production WhatsApp (Approved)
For production deployment:
1. Apply for WhatsApp Business API access
2. Get approved WhatsApp sender number
3. Configure message templates (required by Meta)

### 4. Get Credentials
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

## Backend Configuration

### Environment Variables
Create `.env` file in project root:
```bash
# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/peatsense

# MQTT
MQTT_BROKER=localhost
MQTT_PORT=1883
```

### Recipient Numbers
Edit `backend_api.py` line 51-55:
```python
VILLAGE_LEADERS = [
    'whatsapp:+628123456789',  # Village Head (Sungai Tohor)
    'whatsapp:+628234567890',  # PM.Haze Coordinator
    'whatsapp:+628345678901',  # Agricultural Officer
]
```

**Format**: `whatsapp:+[country_code][number]`
- Indonesia: `+62` (remove leading 0)
- Example: `081234567890` → `whatsapp:+628123456789`

## Customization Options

### Change Alert Frequency
In `backend_api.py` line 59:
```python
ALERT_COOLDOWN_MINUTES = 60  # Change to 30, 120, etc.
```

### Enable WARNING Alerts
In `backend_api.py` line 62:
```python
WHATSAPP_DANGER_ONLY = False  # Send both WARNING and DANGER
```

### Customize Thresholds
Edit thresholds in `peatsense_firmware.ino`:
```cpp
// Flood risk levels
int WATER_SAFE = 100;      // < 100cm = Safe
int WATER_WARNING = 150;   // 100-150cm = Warning
// > 150cm = DANGER (WhatsApp sent)

// Fire risk levels
int VOC_SAFE = 800;        // < 800 ppb = Safe
int VOC_WARNING = 1500;    // 800-1500 ppb = Warning
// > 1500 ppb = DANGER (WhatsApp sent)
```

## Testing

### Test WhatsApp Integration
```bash
# Test alert endpoint
curl -X POST http://localhost:8000/api/alerts/test \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "TEST_NODE",
    "type": "FLOOD",
    "level": "DANGER",
    "message": "Test alert from API",
    "water_level": 180,
    "tds": 2200
  }'
```

### Monitor Logs
```bash
# Watch backend logs for WhatsApp delivery
tail -f backend.log

# Look for:
✓ WhatsApp sent to whatsapp:+628123456789: SMxxxx
📱 WhatsApp alerts sent: 2/2
```

## Costs

### Twilio Pricing (as of 2024)
- **WhatsApp messages**: $0.005 USD per message
- **Free trial**: $15 USD credit (~3000 messages)
- **Monthly estimate**: ~60 alerts/month × 2 recipients = $0.60/month

### Cost Optimization
- ✅ 60-minute cooldown reduces spam
- ✅ DANGER-only mode (enabled by default)
- ✅ Per-node, per-type tracking
- 💡 Estimated: 1-2 messages per day = $3-6/month for 2 recipients

## Troubleshooting

### No Messages Received
1. Check Twilio account active: [console.twilio.com](https://console.twilio.com)
2. Verify sandbox join code sent: `join <code>` to sandbox number
3. Check backend logs: `WhatsApp sent to...`
4. Verify recipient number format: `whatsapp:+628xxx`

### Messages Delayed
- Twilio typical delivery: 1-5 seconds
- Check alert cooldown: May be within 60-minute window
- Verify MQTT broker running: Backend needs MQTT to receive alerts

### Wrong Language
Messages are in **Bahasa Indonesia** by default. To change to English, edit `backend_api.py` lines 358-387.

## Security Notes

⚠️ **Never commit credentials to GitHub**
- Use `.env` file (add to `.gitignore`)
- Rotate tokens if exposed
- Limit Twilio API access by IP

✅ **Production recommendations**:
- Use WhatsApp Business API (not sandbox)
- Configure message templates
- Enable two-factor auth on Twilio account
- Monitor usage in Twilio console

## Support

- **Twilio Docs**: [twilio.com/docs/whatsapp](https://www.twilio.com/docs/whatsapp)
- **WhatsApp Business API**: [business.whatsapp.com](https://business.whatsapp.com)
- **PeatSense Issues**: Create GitHub issue with logs
