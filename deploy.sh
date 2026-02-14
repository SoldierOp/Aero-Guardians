#!/bin/bash

# PeatGuard Pro - Automated Deployment Script
# This script automates the deployment process on a fresh Ubuntu server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    print_error "Please run as root (use sudo)"
    exit 1
fi

print_info "PeatGuard Pro Deployment Script"
print_info "================================"
echo

# Prompt for domain name
read -p "Enter your domain name (e.g., example.com): " DOMAIN_NAME
read -p "Enter your email for SSL certificate: " EMAIL

if [ -z "$DOMAIN_NAME" ] || [ -z "$EMAIL" ]; then
    print_error "Domain name and email are required!"
    exit 1
fi

print_success "Domain: $DOMAIN_NAME"
print_success "Email: $EMAIL"
echo

# Step 1: Update system
print_info "Step 1/8: Updating system packages..."
apt update -qq && apt upgrade -y -qq
print_success "System updated"
echo

# Step 2: Install Docker
print_info "Step 2/8: Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh > /dev/null 2>&1
    rm get-docker.sh
    systemctl start docker
    systemctl enable docker
    print_success "Docker installed"
else
    print_success "Docker already installed"
fi
echo

# Step 3: Install Docker Compose
print_info "Step 3/8: Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    apt install docker-compose -y -qq
    print_success "Docker Compose installed"
else
    print_success "Docker Compose already installed"
fi
echo

# Step 4: Install Certbot
print_info "Step 4/8: Installing Certbot..."
if ! command -v certbot &> /dev/null; then
    apt install certbot python3-certbot-nginx -y -qq
    print_success "Certbot installed"
else
    print_success "Certbot already installed"
fi
echo

# Step 5: Clone repository
print_info "Step 5/8: Cloning PeatGuard repository..."
cd /opt
if [ -d "Aero-Guardians" ]; then
    print_info "Repository already exists, pulling latest changes..."
    cd Aero-Guardians
    git pull
else
    git clone https://github.com/SoldierOp/Aero-Guardians.git
    cd Aero-Guardians
fi
print_success "Repository ready"
echo

# Step 6: Generate environment variables
print_info "Step 6/8: Generating environment configuration..."

# Generate secure passwords
DB_PASSWORD=$(openssl rand -base64 32)
SECRET_KEY=$(openssl rand -hex 32)

# Create .env file from template
cat > .env << EOF
# ============================================
# DATABASE CONFIGURATION
# ============================================
POSTGRES_DB=peatguard_db
POSTGRES_USER=peatguard_admin
POSTGRES_PASSWORD=$DB_PASSWORD

DATABASE_URL=postgresql://peatguard_admin:$DB_PASSWORD@postgres:5432/peatguard_db

# ============================================
# BACKEND API CONFIGURATION
# ============================================
SECRET_KEY=$SECRET_KEY
API_HOST=0.0.0.0
API_PORT=8000

# ============================================
# DOMAIN & CORS CONFIGURATION
# ============================================
DOMAIN_NAME=$DOMAIN_NAME
ALLOWED_ORIGINS=https://$DOMAIN_NAME,https://www.$DOMAIN_NAME,http://localhost:8501

# ============================================
# TWILIO CONFIGURATION (WhatsApp Alerts)
# ============================================
TWILIO_ACCOUNT_SID=CHANGE_THIS
TWILIO_AUTH_TOKEN=CHANGE_THIS
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
ALERT_WHATSAPP_NUMBER=whatsapp:+62XXXXXXXXXX

# ============================================
# APPLICATION SETTINGS
# ============================================
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO

TEMP_THRESHOLD_HIGH=35.0
TEMP_THRESHOLD_CRITICAL=40.0
VOC_THRESHOLD_HIGH=1000
VOC_THRESHOLD_CRITICAL=2000
PM25_THRESHOLD_HIGH=75
PM25_THRESHOLD_CRITICAL=150

SENSOR_COUNT=3
DATA_RETENTION_DAYS=90
SENSOR_CHECK_INTERVAL=300

ML_MODEL_PATH=../models/fire_prediction_model.h5
TFLITE_MODEL_PATH=../models/fire_prediction_model.tflite
FIRE_RISK_THRESHOLD=0.75

JWT_EXPIRY_MINUTES=1440
RATE_LIMIT_PER_MINUTE=60
MAX_UPLOAD_SIZE_MB=10
EOF

print_success "Environment configuration created"
print_info "Database password and secret key generated securely"
echo

# Step 7: Update nginx.conf with domain
print_info "Step 7/8: Updating nginx configuration..."
sed -i "s/yourdomain\.com/$DOMAIN_NAME/g" nginx.conf
sed -i "s/yourdomain\.com/$DOMAIN_NAME/g" website/index.html
print_success "Domain configured in nginx and website"
echo

# Step 8: Obtain SSL certificate
print_info "Step 8/8: Obtaining SSL certificate..."
# Stop nginx if running
docker-compose down 2>/dev/null || true

# Obtain certificate
certbot certonly --standalone -d $DOMAIN_NAME -d www.$DOMAIN_NAME \
    --email $EMAIL \
    --agree-tos \
    --non-interactive \
    --preferred-challenges http

if [ $? -eq 0 ]; then
    print_success "SSL certificate obtained"
else
    print_error "Failed to obtain SSL certificate"
    print_info "You may need to:"
    print_info "  1. Ensure DNS is pointing to this server"
    print_info "  2. Ensure ports 80 and 443 are open"
    print_info "  3. Wait a few minutes for DNS propagation"
    exit 1
fi
echo

# Update docker-compose.yml with SSL paths
sed -i "s|/etc/letsencrypt/live/yourdomain.com|/etc/letsencrypt/live/$DOMAIN_NAME|g" docker-compose.yml

# Configure firewall
print_info "Configuring firewall..."
if command -v ufw &> /dev/null; then
    ufw --force enable
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    print_success "Firewall configured"
fi
echo

# Build and start containers
print_info "Building Docker containers (this may take a few minutes)..."
docker-compose build --quiet
print_success "Containers built"
echo

print_info "Starting services..."
docker-compose up -d
print_success "Services started"
echo

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 10

# Check service health
print_info "Checking service health..."
BACKEND_HEALTH=$(docker-compose exec -T backend curl -s http://localhost:8000/health 2>/dev/null || echo "failed")

if [[ $BACKEND_HEALTH == *"healthy"* ]]; then
    print_success "Backend API is healthy"
else
    print_error "Backend API health check failed"
fi
echo

# Setup automatic backups
print_info "Setting up daily database backups..."
mkdir -p /opt/backups

# Create backup script
cat > /opt/backup-peatguard.sh << 'BACKUP_EOF'
#!/bin/bash
cd /opt/Aero-Guardians
docker-compose exec -T postgres pg_dump -U peatguard_admin peatguard_db > /opt/backups/backup_$(date +%Y%m%d_%H%M%S).sql
# Keep only last 30 days of backups
find /opt/backups -name "backup_*.sql" -mtime +30 -delete
BACKUP_EOF

chmod +x /opt/backup-peatguard.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/backup-peatguard.sh") | crontab -
print_success "Daily backups configured"
echo

# Display summary
echo
print_success "================================"
print_success "Deployment Complete!"
print_success "================================"
echo
print_info "Your PeatGuard Pro deployment is live at:"
print_success "  🌐 Website: https://$DOMAIN_NAME"
print_success "  📊 Dashboard: https://$DOMAIN_NAME/dashboard/"
print_success "  🔌 API: https://$DOMAIN_NAME/api/docs"
echo
print_info "Important Security Information:"
print_success "  Database password: $DB_PASSWORD"
print_success "  Secret key: $SECRET_KEY"
print_info "  (These are saved in /opt/Aero-Guardians/.env)"
echo
print_info "Next Steps:"
echo "  1. Configure Twilio credentials in .env for WhatsApp alerts"
echo "  2. Update email settings in .env (optional)"
echo "  3. Test the dashboard: https://$DOMAIN_NAME/dashboard/"
echo "  4. Deploy your IoT sensors and configure them to send data"
echo
print_info "Useful Commands:"
echo "  View logs:        cd /opt/Aero-Guardians && docker-compose logs -f"
echo "  Restart services: cd /opt/Aero-Guardians && docker-compose restart"
echo "  Stop services:    cd /opt/Aero-Guardians && docker-compose down"
echo "  Update code:      cd /opt/Aero-Guardians && git pull && docker-compose build && docker-compose up -d"
echo
print_info "SSL Certificate renewal is automatic via certbot"
print_info "Database backups run daily at 2:00 AM and are stored in /opt/backups/"
echo
print_success "Happy monitoring! 🌳🔥"
