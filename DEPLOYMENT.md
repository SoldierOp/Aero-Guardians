# 🚀 PeatGuard Pro - Production Deployment Guide

This guide will help you deploy PeatGuard Pro to your domain with SSL, Docker containers, and production configurations.

## 📋 Prerequisites

- **VPS/Cloud Server** (DigitalOcean, AWS, Azure, Linode, etc.)
  - Minimum: 2 CPU cores, 4GB RAM, 20GB storage
  - Ubuntu 22.04 LTS recommended
- **Domain Name** with DNS access
- **SSH Access** to your server
- **Docker & Docker Compose** installed

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│           Nginx (Port 80/443)           │
│    SSL Termination + Reverse Proxy      │
└────────────┬────────────────────────────┘
             │
      ┌──────┴──────┐
      │             │
┌─────▼──────┐ ┌───▼────────┐
│  Backend   │ │ Dashboard  │
│ (FastAPI)  │ │(Streamlit) │
│  Port 8000 │ │ Port 8501  │
└─────┬──────┘ └────────────┘
      │
┌─────▼──────────┐
│   PostgreSQL   │
│   Port 5432    │
└────────────────┘
```

## 🔧 Step 1: Server Setup

### 1.1 Connect to Your Server

```bash
ssh root@YOUR_SERVER_IP
```

### 1.2 Update System

```bash
apt update && apt upgrade -y
```

### 1.3 Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Start Docker
systemctl start docker
systemctl enable docker

# Verify installation
docker --version
docker-compose --version
```

### 1.4 Install Certbot (for SSL)

```bash
apt install certbot python3-certbot-nginx -y
```

## 📥 Step 2: Deploy PeatGuard

### 2.1 Clone Repository

```bash
cd /opt
git clone https://github.com/SoldierOp/Aero-Guardians.git
cd Aero-Guardians
```

### 2.2 Configure Environment Variables

Create `.env` file:

```bash
nano .env
```

Add the following (replace with your actual values):

```env
# Database Configuration
POSTGRES_DB=peatguard_db
POSTGRES_USER=peatguard_admin
POSTGRES_PASSWORD=YOUR_SUPER_SECRET_PASSWORD_HERE

# Backend Configuration
DATABASE_URL=postgresql://peatguard_admin:YOUR_SUPER_SECRET_PASSWORD_HERE@postgres:5432/peatguard_db
SECRET_KEY=YOUR_RANDOM_SECRET_KEY_HERE_USE_64_CHARS
API_HOST=0.0.0.0
API_PORT=8000

# Twilio Configuration (for WhatsApp alerts)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
ALERT_WHATSAPP_NUMBER=whatsapp:+62XXXXXXXXXX

# Domain Configuration
DOMAIN_NAME=yourdomain.com
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Application Settings
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
```

**Generate secure passwords:**

```bash
# Generate database password
openssl rand -base64 32

# Generate secret key
openssl rand -hex 32
```

### 2.3 Update nginx.conf

Edit `nginx.conf` and replace `yourdomain.com` with your actual domain:

```bash
nano nginx.conf
```

Find and replace all instances of `yourdomain.com` with your domain name.

### 2.4 Build and Start Containers

```bash
# Build images
docker-compose build

# Start services in detached mode
docker-compose up -d

# Check status
docker-compose ps
```

You should see 4 containers running:
- `aero-guardians-nginx`
- `aero-guardians-backend`
- `aero-guardians-dashboard`
- `aero-guardians-postgres`

## 🔒 Step 3: Configure SSL Certificate

### 3.1 Obtain SSL Certificate

```bash
# Stop nginx temporarily
docker-compose stop nginx

# Obtain certificate (replace with your domain and email)
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com \
  --email your-email@example.com --agree-tos --non-interactive

# Certificates will be saved to:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

### 3.2 Update Docker Compose SSL Paths

Edit `docker-compose.yml`:

```bash
nano docker-compose.yml
```

Update the nginx volumes section:

```yaml
volumes:
  - ./nginx.conf:/etc/nginx/nginx.conf:ro
  - ./website:/usr/share/nginx/html:ro
  - /etc/letsencrypt/live/yourdomain.com:/etc/nginx/ssl:ro  # Update this line
  - /etc/letsencrypt:/etc/letsencrypt:ro                     # Add this line
```

### 3.3 Restart Services

```bash
docker-compose up -d
```

### 3.4 Setup SSL Auto-Renewal

```bash
# Test renewal
certbot renew --dry-run

# Renewal is automatic via systemd timer
systemctl status certbot.timer
```

## 🌐 Step 4: Configure DNS

Point your domain to your server IP:

1. **Log into your domain registrar** (Namecheap, GoDaddy, Cloudflare, etc.)
2. **Add A records:**

```
Type    Name    Value               TTL
A       @       YOUR_SERVER_IP      300
A       www     YOUR_SERVER_IP      300
```

3. **Wait for DNS propagation** (5-30 minutes)
4. **Verify:**

```bash
dig yourdomain.com
nslookup yourdomain.com
```

## ✅ Step 5: Verify Deployment

### 5.1 Check Service Health

```bash
# View logs
docker-compose logs -f

# Check individual services
docker-compose logs backend
docker-compose logs dashboard
docker-compose logs postgres
docker-compose logs nginx

# Check container health
docker-compose ps
```

### 5.2 Test Endpoints

```bash
# Test backend API
curl https://yourdomain.com/api/health

# Expected response:
# {"status":"healthy","timestamp":"..."}

# Test dashboard (in browser)
# Visit: https://yourdomain.com/dashboard/

# Test landing page
# Visit: https://yourdomain.com
```

### 5.3 Check SSL Certificate

```bash
# Using curl
curl -vI https://yourdomain.com

# Using openssl
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

## 🗄️ Step 6: Database Initialization

### 6.1 Initialize Database Schema

```bash
# Enter backend container
docker-compose exec backend bash

# Run database migrations (if using Alembic)
alembic upgrade head

# Or run initialization script
python -m scripts.init_db

# Exit container
exit
```

### 6.2 Create First Admin User (Optional)

```bash
docker-compose exec backend python -m scripts.create_admin_user
```

## 📊 Step 7: Monitor & Maintain

### 7.1 View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### 7.2 Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Update code and restart
git pull
docker-compose build
docker-compose up -d
```

### 7.3 Backup Database

```bash
# Create backup directory
mkdir -p /opt/backups

# Backup database
docker-compose exec postgres pg_dump -U peatguard_admin peatguard_db > /opt/backups/backup_$(date +%Y%m%d_%H%M%S).sql

# Automate with cron (daily at 2 AM)
crontab -e

# Add this line:
0 2 * * * cd /opt/Aero-Guardians && docker-compose exec postgres pg_dump -U peatguard_admin peatguard_db > /opt/backups/backup_$(date +\%Y\%m\%d_\%H\%M\%S).sql
```

### 7.4 Monitor Resources

```bash
# Container stats
docker stats

# Disk usage
df -h

# Container resource usage
docker-compose top
```

## 🔐 Step 8: Security Hardening

### 8.1 Firewall Configuration

```bash
# Install UFW
apt install ufw -y

# Allow SSH
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

### 8.2 Fail2Ban (Prevent brute force)

```bash
# Install Fail2Ban
apt install fail2ban -y

# Start and enable
systemctl start fail2ban
systemctl enable fail2ban

# Check status
fail2ban-client status
```

### 8.3 Regular Updates

```bash
# Update system
apt update && apt upgrade -y

# Update Docker images
cd /opt/Aero-Guardians
git pull
docker-compose pull
docker-compose up -d --build
```

## 📱 Step 9: Configure WhatsApp Alerts

### 9.1 Setup Twilio Account

1. Visit [Twilio Console](https://console.twilio.com/)
2. Create account and verify phone number
3. Get Account SID and Auth Token
4. Enable WhatsApp sandbox or get approved WhatsApp number

### 9.2 Update Environment Variables

Edit `.env` and add Twilio credentials:

```bash
nano .env
```

### 9.3 Test WhatsApp Integration

```bash
docker-compose exec backend python -m scripts.test_whatsapp
```

## 🚨 Troubleshooting

### Problem: Containers won't start

```bash
# Check logs
docker-compose logs

# Remove and recreate
docker-compose down
docker-compose up -d
```

### Problem: Database connection failed

```bash
# Check postgres container
docker-compose logs postgres

# Verify credentials in .env
cat .env

# Restart postgres
docker-compose restart postgres
```

### Problem: SSL certificate errors

```bash
# Check certificate files
ls -la /etc/letsencrypt/live/yourdomain.com/

# Renew manually
certbot renew

# Check nginx configuration
docker-compose exec nginx nginx -t
```

### Problem: Backend API not responding

```bash
# Check backend logs
docker-compose logs backend

# Check if port 8000 is accessible
docker-compose exec backend curl http://localhost:8000/health

# Restart backend
docker-compose restart backend
```

### Problem: Dashboard not loading

```bash
# Check dashboard logs
docker-compose logs dashboard

# Verify Streamlit is running
docker-compose exec dashboard ps aux | grep streamlit

# Restart dashboard
docker-compose restart dashboard
```

## 📈 Performance Optimization

### Enable Docker BuildKit

```bash
export DOCKER_BUILDKIT=1
docker-compose build
```

### Optimize PostgreSQL

Edit `docker-compose.yml` and add:

```yaml
postgres:
  command: 
    - "postgres"
    - "-c"
    - "max_connections=200"
    - "-c"
    - "shared_buffers=256MB"
    - "-c"
    - "effective_cache_size=1GB"
```

### Enable Gzip Compression

Already configured in `nginx.conf` - verify it's enabled.

## 🎯 Next Steps

- [ ] Configure monitoring (Prometheus + Grafana)
- [ ] Setup automated backups to S3/cloud storage
- [ ] Configure logging aggregation (ELK stack)
- [ ] Setup CI/CD pipeline (GitHub Actions)
- [ ] Enable CDN (Cloudflare) for static assets
- [ ] Configure alerting (PagerDuty, Slack)
- [ ] Setup staging environment

## 📞 Support

- **GitHub Issues:** https://github.com/SoldierOp/Aero-Guardians/issues
- **Documentation:** https://yourdomain.com/docs
- **Email:** contact@yourdomain.com

## 📝 Quick Reference Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend

# Update deployment
git pull && docker-compose build && docker-compose up -d

# Backup database
docker-compose exec postgres pg_dump -U peatguard_admin peatguard_db > backup.sql

# Check SSL expiry
certbot certificates

# Renew SSL
certbot renew && docker-compose restart nginx
```

---

**🎉 Your PeatGuard Pro deployment is complete!**

Visit your domain to see the live dashboard and start monitoring peat fire risks.
