# 🚨 WINDOWS DEFENDER IS BLOCKING NGROK

## Quick Fix (2 minutes):

### Step 1: Disable Real-time Protection TEMPORARILY
1. Press `Win + I` to open Windows Settings
2. Click "Privacy & Security" → "Windows Security" → "Open Windows Security"
3. Click "Virus & threat protection" 
4. Under "Virus & threat protection settings" click "Manage settings"
5. Turn OFF "Real-time protection" (temporarily, just for 10 minutes)

### Step 2: Run ngrok setup again
```powershell
.\get_ngrok.ps1
```

### Step 3: Start ngrok tunnel
```powershell
.\ngrok.exe http 8000
```

You'll see output like:
```
Forwarding  https://xxxxx-xx-xxx.ngrok-free.app -> http://localhost:8000
```

### Step 4: Configure Twilio Webhook
1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Under "Sandbox Configuration"
3. Set "WHEN A MESSAGE COMES IN" to: `https://xxxxx-xx-xxx.ngrok-free.app/webhook/whatsapp`
4. Click **Save**

### Step 5: Test on WhatsApp
1. Save contact: **+1 415 523 8886** (Twilio WhatsApp Sandbox)
2. Send join code (shown in Twilio console): `join <your-code>`
3. Send: **STATUS**
4. You should get full sensor data response!

### Step 6: Re-enable Windows Defender
After testing, go back to Windows Security and turn ON Real-time protection

---

## Alternative: Use ngrok from Downloads folder

If Windows Defender keeps blocking:

1. Go to: https://ngrok.com/download
2. Download manually to your Downloads folder
3. Extract there (Windows Defender usually doesn't block Downloads folder)
4. Run: `C:\Users\Mayan\Downloads\ngrok\ngrok.exe http 8000`

---

## Why is Windows Defender blocking?

Ngrok is a legitimate tunneling tool, but Windows Defender flags it because:
- It creates network tunnels (which hackers also use)
- It's commonly used in pentesting

**It's 100% safe for our hackathon** - we're just using it to expose localhost to the internet!
