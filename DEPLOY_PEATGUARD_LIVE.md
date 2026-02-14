# 🚀 Deploy PeatGuard to peatguard.live

## ✅ Domain Configured: peatguard.live

All configuration files are ready for **peatguard.live**!

## 📋 Prerequisites

1. **Ubuntu Server** (DigitalOcean, AWS, Azure, Linode, etc.)
   - Minimum: 2 CPU cores, 4GB RAM, 20GB storage
   - Ubuntu 22.04 LTS recommended

2. **DNS Configuration** - Point your domain to server:
   ```
   Type    Name    Value               TTL
   A       @       YOUR_SERVER_IP      300
   A       www     YOUR_SERVER_IP      300
   ```
   Do this at your domain registrar (where you bought peatguard.live)

3. **Server Access** - SSH credentials

## 🚀 One-Command Deployment

SSH into your server and run:

```bash
curl -fsSL https://raw.githubusercontent.com/SoldierOp/Aero-Guardians/main/deploy.sh | sudo bash
```

When prompted:
- **Domain name:** `peatguard.live`
- **Email:** Your email address (for SSL certificate)

The script will automatically:
- ✅ Install Docker & Docker Compose
- ✅ Clone repository
- ✅ Generate secure passwords
- ✅ Obtain SSL certificate for peatguard.live
- ✅ Build and start containers
- ✅ Configure firewall
- ✅ Setup daily backups

**Deployment time:** 5-10 minutes

## 📊 Access Your Deployment

After deployment completes:

- **🌐 Landing Page:** https://peatguard.live
- **📊 Dashboard:** https://peatguard.live/dashboard/
- **🔌 API Docs:** https://peatguard.live/api/docs
- **💓 Health Check:** https://peatguard.live/api/health

## ⚙️ Post-Deployment: Configure WhatsApp Alerts

### 1. Get Twilio Credentials

1. Go to [Twilio Console](https://console.twilio.com/)
2. Create account (free trial available)
3. Get your **Account SID** and **Auth Token**
4. Get a WhatsApp-enabled number or use sandbox

### 2. Update Environment Variables

```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Edit environment file
nano /opt/Aero-Guardians/.env
```

Update these values:
```env
TWILIO_ACCOUNT_SID=your_actual_account_sid_here
TWILIO_AUTH_TOKEN=your_actual_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
ALERT_WHATSAPP_NUMBER=whatsapp:+62XXXXXXXXXX
```

### 3. Restart Backend

```bash
cd /opt/Aero-Guardians
docker-compose restart backend
```

### 4. Test WhatsApp Integration

```bash
docker-compose exec backend python -m scripts.test_whatsapp
```

## 🔧 Management Commands

### View Logs
```bash
cd /opt/Aero-Guardians

# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f dashboard
```

### Restart Services
```bash
cd /opt/Aero-Guardians
docker-compose restart

# Or restart specific service
docker-compose restart backend
```

### Update Deployment
```bash
cd /opt/Aero-Guardians
git pull
docker-compose build
docker-compose up -d
```

### Check Service Status
```bash
cd /opt/Aero-Guardians
docker-compose ps
```

Expected output:
```
NAME                          STATUS    PORTS
aero-guardians-backend        Up        0.0.0.0:8000->8000/tcp
aero-guardians-dashboard      Up        0.0.0.0:8501->8501/tcp
aero-guardians-nginx          Up        0.0.0.0:80->80/tcp, 443->443/tcp
aero-guardians-postgres       Up        5432/tcp
```

## 🔐 Database Credentials

After deployment, find your generated credentials:

```bash
cat /opt/Aero-Guardians/.env | grep POSTGRES_PASSWORD
cat /opt/Aero-Guardians/.env | grep SECRET_KEY
```

**Important:** Save these credentials securely!

## 📱 Configure IoT Sensors

Once deployment is complete, configure your ESP32 sensors to send data:

### WiFi Configuration
Update in your Arduino sketch:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "https://peatguard.live/api/sensors/data";
```

### API Endpoint
```
POST https://peatguard.live/api/sensors/data

{
  "sensor_id": "SENSOR_001",
  "temperature": 32.5,
  "humidity": 65.2,
  "voc": 450,
  "eco2": 800,
  "pm25": 45.3,
  "water_level": 85.0,
  "timestamp": "2026-02-14T12:30:00Z"
}
```

## 🔒 Security Notes

The deployment automatically:
- ✅ Generates secure random passwords
- ✅ Obtains SSL certificates (Let's Encrypt)
- ✅ Configures firewall (ports 22, 80, 443 only)
- ✅ Enables rate limiting
- ✅ Sets up automatic SSL renewal

### Firewall Status
```bash
ufw status
```

### SSL Certificate Renewal
Automatic via certbot. Check status:
```bash
certbot certificates
```

## 📦 Backup & Restore

### Manual Backup
```bash
cd /opt/Aero-Guardians
docker-compose exec postgres pg_dump -U peatguard_admin peatguard_db > backup_$(date +%Y%m%d).sql
```

### Automatic Backups
- **Scheduled:** Daily at 2:00 AM
- **Location:** `/opt/backups/`
- **Retention:** 30 days

### Restore from Backup
```bash
cd /opt/Aero-Guardians
docker-compose exec -T postgres psql -U peatguard_admin peatguard_db < backup_20260214.sql
```

## 🚨 Troubleshooting

### Problem: Can't access peatguard.live

**Check DNS:**
```bash
nslookup peatguard.live
dig peatguard.live
```

**Verify nginx is running:**
```bash
docker-compose ps nginx
```

**Check nginx logs:**
```bash
docker-compose logs nginx
```

### Problem: SSL certificate error

**Check certificate:**
```bash
certbot certificates
ls -la /etc/letsencrypt/live/peatguard.live/
```

**Manually renew:**
```bash
docker-compose stop nginx
certbot renew
docker-compose start nginx
```

### Problem: Backend not responding

**Check backend logs:**
```bash
docker-compose logs backend
```

**Check database connection:**
```bash
docker-compose exec backend curl http://localhost:8000/health
```

**Restart backend:**
```bash
docker-compose restart backend
```

### Problem: Dashboard not loading

**Check dashboard logs:**
```bash
docker-compose logs dashboard
```

**Verify it's running:**
```bash
docker-compose ps dashboard
```

**Restart dashboard:**
```bash
docker-compose restart dashboard
```

## 📈 Monitoring

### View Resource Usage
```bash
docker stats
```

### Check Disk Space
```bash
df -h
```

### View System Logs
```bash
journalctl -u docker -f
```

## 🎯 Next Steps

1. ✅ Deploy to server (5-10 minutes)
2. ✅ Configure WhatsApp alerts
3. ✅ Test dashboard access
4. ✅ Configure IoT sensors
5. ✅ Deploy sensors in field
6. 📊 Monitor peat fire risks in real-time!

## 📞 Support

- **Documentation:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **GitHub:** https://github.com/SoldierOp/Aero-Guardians
- **Email:** contact@peatguard.live

---

## 🎉 Quick Start Summary

```bash
# 1. SSH into your server
ssh root@YOUR_SERVER_IP

# 2. Run deployment script
curl -fsSL https://raw.githubusercontent.com/SoldierOp/Aero-Guardians/main/deploy.sh | sudo bash

# 3. When prompted:
#    Domain: peatguard.live
#    Email: your-email@example.com

# 4. Wait 5-10 minutes

# 5. Visit https://peatguard.live

# 6. Configure WhatsApp (optional):
nano /opt/Aero-Guardians/.env
# Add Twilio credentials
docker-compose restart backend
```

**That's it!** Your PeatGuard system is live at **peatguard.live** 🌳🔥
