# 📱 Real WhatsApp Testing - Step by Step

## ✅ Current Status:
- Backend running on port 8000
- Chatbot webhook working (tested locally)
- Ready for real WhatsApp integration

---

## 🚀 STEP 1: Download & Setup ngrok

**Option A: Quick Download**
1. Go to: https://ngrok.com/download
2. Click "Download for Windows"
3. Extract the zip file
4. Move `ngrok.exe` to: `C:\Users\Mayan\Downloads\aero-guardians-master\`

**Option B: Command Line (if you have Chocolatey)**
```powershell
choco install ngrok
```

---

## 🌐 STEP 2: Expose Your Backend

Open a **NEW PowerShell terminal** (keep backend running in the other):

```powershell
# Navigate to your project folder
cd C:\Users\Mayan\Downloads\aero-guardians-master

# Start ngrok (this creates public URL to your localhost:8000)
.\ngrok http 8000
```

**You'll see output like:**
```
ngrok                                                                           

Session Status    online
Account           Your Account (Plan: Free)
Version           3.x.x
Region            United States (us)
Latency           -
Web Interface     http://127.0.0.1:4040
Forwarding        https://abc123-random.ngrok-free.app -> http://localhost:8000

Connections       ttl     opn     rt1     rt5     p50     p90
                  0       0       0.00    0.00    0.00    0.00
```

**📝 COPY THIS URL:** `https://abc123-random.ngrok-free.app`
(Your actual URL will be different - copy yours!)

**⚠️ IMPORTANT:** Keep this terminal open! If you close it, the URL stops working.

---

## 🔗 STEP 3: Configure Twilio Webhook

1. **Go to Twilio Console:**
   - Open browser: https://console.twilio.com/
   - Login with your account

2. **Navigate to WhatsApp Sandbox:**
   - Left sidebar: Click **Messaging**
   - Click **Try it out**
   - Click **Send a WhatsApp message**
   - You'll see your sandbox number: +1 (415) 523-8886

3. **Set Webhook URL:**
   - Look for **"Sandbox settings"** or **"Settings"** button
   - Find section: **"WHEN A MESSAGE COMES IN"**
   - Paste your ngrok URL + `/webhook/whatsapp`:
     ```
     https://abc123-random.ngrok-free.app/webhook/whatsapp
     ```
   - Set **HTTP Method:** `POST`
   - Click **Save**

**✅ Checkpoint:** You should see "Configuration saved" message

---

## 📱 STEP 4: Join WhatsApp Sandbox (If Not Already Joined)

On your phone (+919306912663):

1. Open WhatsApp
2. Start new chat with: **+1 (415) 523-8886**
3. Send the join code (shown in Twilio console): 
   ```
   join [your-sandbox-code]
   ```
   Example: `join happy-elephant`
4. You'll get confirmation: "You are all set!"

---

## 🧪 STEP 5: TEST THE CHATBOT!

Send these messages to **+1 (415) 523-8886**:

### Test 1: STATUS
```
STATUS
```
**Expected:** Response with water level, fire risk, salinity, temperature

### Test 2: FARMING ADVICE
```
TANAM
```
**Expected:** Crop recommendations based on salinity levels

### Test 3: NATURAL LANGUAGE
```
kondisi aman?
```
**Expected:** Same as STATUS (bot understands Indonesian variations)

### Test 4: HELP MENU
```
BANTUAN
```
**Expected:** Full command menu in Indonesian

### Test 5: EMERGENCY
```
BAHAYA
```
**Expected:** Emergency contact numbers

---

## 🔍 Monitoring & Debugging

### Watch Backend Logs:
In your backend terminal, you should see:
```
📥 WhatsApp message from whatsapp:+919306912663: STATUS
📤 Response sent: 📊 *STATUS PEATGUARD*...
INFO: 127.0.0.1:xxxxx - "POST /webhook/whatsapp HTTP/1.1" 200 OK
```

### Check ngrok Dashboard:
- Open browser: http://localhost:4040
- See all webhook requests in real-time
- Helpful for debugging if messages don't arrive

### Twilio Debugger:
- Twilio Console → Monitor → Logs → Messaging
- See all messages sent/received
- Check for webhook errors

---

## ❌ Troubleshooting

### Problem: No response from bot

**Check 1:** Backend still running?
```powershell
# In backend terminal, should see "Uvicorn running"
```

**Check 2:** ngrok still active?
```powershell
# Should see ngrok status screen
# If closed, restart: .\ngrok http 8000
```

**Check 3:** Webhook URL correct?
- Twilio → Messaging → Sandbox settings
- URL should be: `https://YOUR-NGROK.ngrok-free.app/webhook/whatsapp`
- Must include `/webhook/whatsapp` at the end!
- Method must be `POST`

**Check 4:** Test ngrok URL directly:
```powershell
curl https://YOUR-NGROK-URL.ngrok-free.app/webhook/whatsapp
# Should return JSON with chatbot info
```

### Problem: "System offline" message

This shouldn't happen anymore (we added demo data fallback).
But if it does:
- Backend is running ✅
- Webhook is receiving messages ✅
- Response logic needs check (should have demo data)

### Problem: Twilio says "Webhook Error"

- Copy your ngrok URL again (it might have changed)
- Make sure URL ends with `/webhook/whatsapp`
- Check ngrok isn't showing blocked requests

---

## 🎬 Demo Day Preparation

### Before Judges Arrive:
1. ✅ Backend running
2. ✅ ngrok tunnel active
3. ✅ Webhook configured
4. ✅ Test message sent successfully
5. ✅ Phone charged & WhatsApp ready

### During Demo:
"Let me show you real-time community interaction..."
[Send "STATUS" on phone]
[Wait 1-2 seconds]
"See? Instant reply in Indonesian with real sensor data."
[Send "TANAM"]
"And it gives actionable farming advice, not just numbers."

### Backup:
If ngrok fails during demo:
- Show `test_webhook.py` output instead
- Explain: "This simulates the exact Twilio webhook"
- Responses are identical to real WhatsApp

---

## 🎯 Success Checklist

- [ ] ngrok running and showing forwarding URL
- [ ] Backend terminal showing no errors
- [ ] Twilio webhook configured with ngrok URL
- [ ] Joined WhatsApp sandbox
- [ ] Sent "STATUS" and got sensor data response
- [ ] Sent "TANAM" and got crop recommendations
- [ ] Tried natural language ("kondisi aman?") and it worked
- [ ] All responses in Indonesian with proper formatting

---

## 💡 Pro Tips

1. **ngrok URL Changes:** Free ngrok URLs change each restart. If you restart ngrok, update Twilio webhook!

2. **Keep It Running:** Don't close backend or ngrok terminals before demo

3. **Test Before Demo:** Send one test message 5 minutes before presenting

4. **Show Natural Language:** During demo, type "ada asap?" instead of "API" to show intelligence

5. **Emphasize Speed:** Point out responses arrive in < 2 seconds

6. **Bilingual Flex:** Show BANTUAN (Indonesian) then HELP (English) both work

---

## 🏆 What This Achieves

✅ **Problem Statement:** "WhatsApp chatbots for information dissemination"  
✅ **Two-way communication:** Community can query anytime  
✅ **Local language:** Indonesian with natural understanding  
✅ **Actionable insights:** TDS → crop recommendations  
✅ **Accessible:** Any phone with WhatsApp works  
✅ **No app needed:** Uses existing communication channel  

**This single feature addresses multiple problem requirements! 🎯**

---

Ready to start? Run these commands!
