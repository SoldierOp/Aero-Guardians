# PeatGuard Pro - Quick Start Deployment

## 🚀 One-Command Deployment

For a fresh Ubuntu server, run this single command:

```bash
wget -O - https://raw.githubusercontent.com/SoldierOp/Aero-Guardians/main/deploy.sh | sudo bash
```

**Or** follow these steps:

### 1️⃣ Copy Script to Server

```bash
# SSH into your server
ssh root@YOUR_SERVER_IP

# Download deployment script
wget https://raw.githubusercontent.com/SoldierOp/Aero-Guardians/main/deploy.sh

# Make executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 2️⃣ Follow Prompts

The script will ask for:
- **Domain name** (e.g., peatguard.com)
- **Email** (for SSL certificate)

### 3️⃣ Wait 5-10 Minutes

The script will automatically:
- ✅ Install Docker & Docker Compose
- ✅ Clone PeatGuard repository
- ✅ Generate secure passwords
- ✅ Obtain SSL certificate
- ✅ Build and start containers
- ✅ Configure firewall
- ✅ Setup automatic backups

### 4️⃣ Access Your Deployment

After completion, visit:
- **Website:** `https://YOUR_DOMAIN.com`
- **Dashboard:** `https://YOUR_DOMAIN.com/dashboard/`
- **API Docs:** `https://YOUR_DOMAIN.com/api/docs`

## 📋 Prerequisites

- Ubuntu 22.04 LTS server (2 CPU, 4GB RAM minimum)
- Domain name with DNS pointing to server IP
- Ports 80 and 443 open

## ⚙️ Post-Deployment Configuration

### Configure WhatsApp Alerts

1. Edit environment file:
```bash
nano /opt/Aero-Guardians/.env
```

2. Update Twilio credentials:
```env
TWILIO_ACCOUNT_SID=your_actual_sid
TWILIO_AUTH_TOKEN=your_actual_token
ALERT_WHATSAPP_NUMBER=whatsapp:+62XXXXXXXXX
```

3. Restart backend:
```bash
cd /opt/Aero-Guardians
docker-compose restart backend
```

### Test WhatsApp Integration

```bash
cd /opt/Aero-Guardians
docker-compose exec backend python -m scripts.test_whatsapp
```

## 🔧 Management Commands

```bash
# View logs
cd /opt/Aero-Guardians
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update deployment
git pull
docker-compose build
docker-compose up -d

# Manual backup
docker-compose exec postgres pg_dump -U peatguard_admin peatguard_db > backup.sql
```

## 📊 Service Status

Check if services are running:

```bash
docker-compose ps
```

Expected output:
```
NAME                          STATUS    PORTS
aero-guardians-backend        Up        0.0.0.0:8000->8000/tcp
aero-guardians-dashboard      Up        0.0.0.0:8501->8501/tcp
aero-guardians-nginx          Up        0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
aero-guardians-postgres       Up        5432/tcp
```

## 🔒 Security

The deployment script automatically:
- Generates secure random passwords
- Obtains SSL certificates
- Configures firewall (UFW)
- Sets up rate limiting
- Enables automatic SSL renewal

## 📞 Support

- **Documentation:** [DEPLOYMENT.md](DEPLOYMENT.md)
- **GitHub Issues:** https://github.com/SoldierOp/Aero-Guardians/issues

## 🎯 What Gets Deployed

1. **PostgreSQL Database** (port 5432) - Sensor data storage
2. **FastAPI Backend** (port 8000) - REST API endpoints
3. **Streamlit Dashboard** (port 8501) - Real-time monitoring UI
4. **Nginx Reverse Proxy** (ports 80/443) - SSL termination & routing
5. **Landing Page** - Professional website at domain root

## ⏱️ Estimated Time

- Fresh server: **5-10 minutes**
- Update existing: **2-3 minutes**

---

**Ready to deploy?** Just run:

```bash
curl -fsSL https://raw.githubusercontent.com/SoldierOp/Aero-Guardians/main/deploy.sh | sudo bash
```

🌳 Protecting Indonesia's Peatlands, One Deployment at a Time
