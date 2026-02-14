# 🚀 Deploy PeatGuard to Render.com + peatguard.live

## ✅ Why Render.com?

- ✅ **FREE** tier available
- ✅ No SSH or server management needed
- ✅ Automatic SSL certificates
- ✅ Auto-deploys from GitHub
- ✅ PostgreSQL database included
- ✅ Easy setup (10 minutes)

## 📋 What You'll Get

After deployment:
- **Backend API:** `https://peatguard-backend.onrender.com`
- **Dashboard:** `https://peatguard-dashboard.onrender.com`
- **Landing Page:** `https://peatguard.live` (your custom domain)
- **Database:** PostgreSQL (managed by Render)

## 🚀 Step-by-Step Deployment

### Step 1: Create Render Account

1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub (recommended)
4. Authorize Render to access your repositories

### Step 2: Deploy Backend API

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Click "Connect a repository"
3. Select **"SoldierOp/Aero-Guardians"**
4. Configure:
   ```
   Name: peatguard-backend
   Region: Singapore (closest to Indonesia)
   Branch: main
   Runtime: Docker
   Dockerfile Path: ./Dockerfile.backend
   Docker Command: (leave empty)
   Plan: Free
   ```
5. Add Environment Variables:
   ```
   POSTGRES_DB = peatguard_db
   POSTGRES_USER = peatguard_admin
   POSTGRES_PASSWORD = <click Generate> (creates secure password)
   DATABASE_URL = (will add after database is created)
   SECRET_KEY = <click Generate>
   ENVIRONMENT = production
   TWILIO_ACCOUNT_SID = (leave blank for now)
   TWILIO_AUTH_TOKEN = (leave blank for now)
   TWILIO_WHATSAPP_NUMBER = whatsapp:+14155238886
   ALERT_WHATSAPP_NUMBER = (your WhatsApp number)
   ```
6. Click **"Create Web Service"**
7. Wait 5-10 minutes for deployment
8. Copy the URL (e.g., `https://peatguard-backend.onrender.com`)

### Step 3: Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   ```
   Name: peatguard-db
   Database: peatguard_db
   User: peatguard_admin
   Region: Singapore
   Plan: Free
   ```
3. Click **"Create Database"**
4. After creation, click on the database
5. Copy **"Internal Database URL"** (starts with `postgresql://`)

### Step 4: Connect Backend to Database

1. Go back to **peatguard-backend** service
2. Click **"Environment"** tab
3. Update **DATABASE_URL** with the Internal Database URL you copied
4. Click **"Save Changes"**
5. Service will automatically redeploy

### Step 5: Deploy Dashboard

1. Click **"New +"** → **"Web Service"**
2. Select **"SoldierOp/Aero-Guardians"** repository
3. Configure:
   ```
   Name: peatguard-dashboard
   Region: Singapore
   Branch: main
   Runtime: Docker
   Dockerfile Path: ./Dockerfile.dashboard
   Plan: Free
   ```
4. Add Environment Variables:
   ```
   BACKEND_URL = https://peatguard-backend.onrender.com
   ```
   (Use the backend URL from Step 2)
5. Click **"Create Web Service"**
6. Wait 5-10 minutes for deployment

### Step 6: Configure Custom Domain (peatguard.live)

#### Option A: Point to Backend (API + Dashboard Routing)

1. Go to **peatguard-backend** service
2. Click **"Settings"** tab
3. Scroll to **"Custom Domains"**
4. Click **"Add Custom Domain"**
5. Enter: `peatguard.live`
6. Render will show DNS records to add:
   ```
   Type: CNAME
   Name: @
   Value: peatguard-backend.onrender.com
   ```
7. Go to your domain registrar (name.com) DNS settings
8. Add the CNAME record
9. Wait 5-30 minutes for DNS propagation
10. Render will automatically provision SSL certificate

#### Option B: Deploy Landing Page Separately (Recommended)

**6a. Deploy Static Landing Page**

1. Click **"New +"** → **"Static Site"**
2. Select **"SoldierOp/Aero-Guardians"** repository
3. Configure:
   ```
   Name: peatguard-web
   Branch: main
   Build Command: (leave empty)
   Publish Directory: ./website
   ```
4. Click **"Create Static Site"**

**6b. Add Custom Domain to Landing Page**

1. In **peatguard-web** service, go to **"Settings"**
2. **"Custom Domains"** → **"Add Custom Domain"**
3. Enter: `peatguard.live`
4. Add DNS records at name.com:
   ```
   Type: CNAME
   Name: @
   Value: peatguard-web.onrender.com
   ```

**6c. Add Subdomains for API and Dashboard**

Add these DNS records at name.com:
```
Type: CNAME
Name: api
Value: peatguard-backend.onrender.com

Type: CNAME
Name: dashboard
Value: peatguard-dashboard.onrender.com
```

Then access:
- Landing: `https://peatguard.live`
- API: `https://api.peatguard.live`
- Dashboard: `https://dashboard.peatguard.live`

### Step 7: Test Deployment

#### Test Backend API
```bash
curl https://peatguard-backend.onrender.com/health
```
Expected: `{"status":"healthy"}`

#### Test Dashboard
Visit in browser: `https://peatguard-dashboard.onrender.com`

#### Test Landing Page
Visit: `https://peatguard.live` (after DNS propagates)

### Step 8: Configure WhatsApp Alerts (Optional)

1. Get Twilio credentials from https://console.twilio.com/
2. In Render dashboard, go to **peatguard-backend**
3. Click **"Environment"** tab
4. Update:
   ```
   TWILIO_ACCOUNT_SID = your_account_sid
   TWILIO_AUTH_TOKEN = your_auth_token
   ALERT_WHATSAPP_NUMBER = whatsapp:+62XXXXXXXXXX
   ```
5. Click **"Save Changes"** (auto-redeploys)

## ⚙️ DNS Configuration Summary

At name.com, add these records:

### Option A: Simple (Everything through load balancer)
```
Type    Name       Value
CNAME   @          peatguard-backend.onrender.com
CNAME   www        peatguard-backend.onrender.com
```

### Option B: Separate Services (Recommended)
```
Type    Name       Value
CNAME   @          peatguard-web.onrender.com
CNAME   www        peatguard-web.onrender.com
CNAME   api        peatguard-backend.onrender.com
CNAME   dashboard  peatguard-dashboard.onrender.com
```

Then access:
- `https://peatguard.live` → Landing page
- `https://api.peatguard.live` → Backend API
- `https://dashboard.peatguard.live` → Dashboard

## 🔄 Auto-Deployment

Render automatically redeploys when you push to GitHub:
```bash
git add .
git commit -m "Update feature"
git push origin main
```
Render will detect changes and redeploy in ~5 minutes.

## 📊 Monitor Your Services

1. Go to Render dashboard
2. Click on any service
3. View:
   - **Logs** - Real-time application logs
   - **Metrics** - CPU, memory, bandwidth usage
   - **Events** - Deployment history
   - **Shell** - Access service terminal

## 💰 Free Tier Limitations

- **750 hours/month per service** (not 24/7 after ~31 days)
- **Services spin down after 15 min inactivity**
- **First request after sleep takes ~30 seconds** (cold start)
- **100GB bandwidth/month**
- **PostgreSQL: 1GB storage, 1GB RAM**

**Workaround:** Use a free uptime monitor (UptimeRobot) to ping your services every 5 minutes to keep them awake.

## 🚨 Troubleshooting

### Backend Won't Start

**Check logs:**
1. Go to peatguard-backend service
2. Click "Logs" tab
3. Look for errors

**Common issues:**
- Database connection failed → Check DATABASE_URL
- Missing environment variables → Add from Step 2
- Port error → Render uses PORT env var automatically

### Dashboard Not Connecting to Backend

**Fix:**
1. Update dashboard BACKEND_URL to correct backend URL
2. Add backend URL to ALLOWED_ORIGINS in backend env vars

### Custom Domain Not Working

**Check:**
1. DNS propagation (can take up to 48 hours)
2. Verify DNS records at name.com match Render instructions
3. Check domain status in Render (should say "Verified")

**Verify DNS:**
```bash
nslookup peatguard.live
```

### Database Connection Issues

**Fix:**
1. Check database is running (green status in Render)
2. Verify DATABASE_URL in backend matches database Internal URL
3. Check database logs for connection attempts

## 📈 Upgrade to Paid (Optional)

If you need 24/7 uptime:

**Starter Plan ($7/month per service):**
- No sleep/spin-down
- 24/7 availability
- Faster cold starts
- More resources

**Upgrade:**
1. Go to service settings
2. Click "Change Plan"
3. Select "Starter"

## 🎯 Your URLs After Deployment

**Option A (Simple):**
- Everything: `https://peatguard.live`

**Option B (Separate):**
- Landing: `https://peatguard.live`
- API: `https://api.peatguard.live`
- Dashboard: `https://dashboard.peatguard.live`
- API Docs: `https://api.peatguard.live/docs`

## 🎉 Next Steps

1. ✅ Deploy to Render (30 minutes setup)
2. ✅ Configure DNS at name.com
3. ✅ Wait for DNS propagation (5-30 minutes)
4. ✅ Test all services
5. ✅ Configure WhatsApp alerts (optional)
6. 📊 Start monitoring peat fires!

## 📞 Support

- **Render Docs:** https://render.com/docs
- **Render Support:** https://render.com/support
- **GitHub:** https://github.com/SoldierOp/Aero-Guardians/issues
- **Email:** contact@peatguard.live

---

**Ready to deploy?** Go to https://render.com and follow the steps above! 🚀
