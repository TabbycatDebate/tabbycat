#!/bin/bash

# Digital Ocean Deployment Script for Tabbycat
# This script sets up Tabbycat on a Ubuntu Digital Ocean droplet

set -e

echo "🚀 Starting Tabbycat deployment on Digital Ocean..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=""  # Add your domain here if you have one
APP_DIR="/opt/tabbycat"
LOG_DIR="/var/log/tabbycat"
STATIC_DIR="/var/www/tabbycat"
DB_NAME="tab_2yw0"
DB_USER="tab"
DB_PASSWORD="57yqNclrMENfxxJuYmbBJ0u26FdDzOkB"
DB_HOST="dpg-d1l186h5pdvs73bd0nv0-a.oregon-postgres.render.com"

# System user for the application
APP_USER="tabbycat"

echo -e "${GREEN}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}📦 Installing required packages...${NC}"
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    nginx \
    redis-server \
    curl \
    git \
    supervisor \
    postgresql-client \
    libpq-dev \
    nodejs \
    npm

# Install Node Version Manager and Node.js
echo -e "${GREEN}📦 Installing Node.js via NVM...${NC}"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

# Create application user
echo -e "${GREEN}👤 Creating application user...${NC}"
if ! id "$APP_USER" &>/dev/null; then
    useradd --system --create-home --shell /bin/bash $APP_USER
    usermod -aG www-data $APP_USER
fi

# Create directories
echo -e "${GREEN}📁 Creating application directories...${NC}"
mkdir -p $APP_DIR
mkdir -p $LOG_DIR
mkdir -p $STATIC_DIR/{static,media}
chown -R $APP_USER:$APP_USER $APP_DIR
chown -R $APP_USER:$APP_USER $LOG_DIR
chown -R $APP_USER:www-data $STATIC_DIR
chmod -R 755 $STATIC_DIR

# Clone or copy the application
echo -e "${GREEN}📂 Setting up application code...${NC}"
if [ -d "$APP_DIR/.git" ]; then
    echo "Application already exists, pulling latest changes..."
    cd $APP_DIR
    sudo -u $APP_USER git pull
else
    # Copy current directory to app directory
    cp -r . $APP_DIR/
    chown -R $APP_USER:$APP_USER $APP_DIR
fi

cd $APP_DIR

# Install Python dependencies
echo -e "${GREEN}🐍 Installing Python dependencies...${NC}"
sudo -u $APP_USER python3 -m venv venv
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install --upgrade pip"
sudo -u $APP_USER bash -c "source venv/bin/activate && pip install pipenv"
sudo -u $APP_USER bash -c "source venv/bin/activate && pipenv install --system --deploy"

# Install Node.js dependencies and build static files
echo -e "${GREEN}📦 Installing Node.js dependencies...${NC}"
sudo -u $APP_USER bash -c "source ~/.bashrc && cd $APP_DIR && npm ci --only=production"

# Build static files
echo -e "${GREEN}🔨 Building static files...${NC}"
sudo -u $APP_USER bash -c "source ~/.bashrc && cd $APP_DIR && npm run build"

# Set environment variables
echo -e "${GREEN}🔧 Setting up environment...${NC}"
cat > /etc/environment << EOF
ON_DIGITALOCEAN=1
DJANGO_SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=0
REDIS_URL=redis://127.0.0.1:6379/0
EOF

# Collect static files
echo -e "${GREEN}📁 Collecting static files...${NC}"
sudo -u $APP_USER bash -c "source $APP_DIR/venv/bin/activate && source /etc/environment && cd $APP_DIR && python tabbycat/manage.py collectstatic --noinput"

# Run database migrations
echo -e "${GREEN}🗄️ Running database migrations...${NC}"
sudo -u $APP_USER bash -c "source $APP_DIR/venv/bin/activate && source /etc/environment && cd $APP_DIR && python tabbycat/manage.py migrate"

# Start and enable Redis
echo -e "${GREEN}🔴 Starting Redis...${NC}"
systemctl start redis-server
systemctl enable redis-server

echo -e "${GREEN}✅ Basic setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Run ./create_systemd_services.sh to create systemd services"
echo "2. Run ./setup_nginx.sh to configure nginx"
echo "3. Create a superuser: cd $APP_DIR && source venv/bin/activate && python tabbycat/manage.py createsuperuser"
echo "4. Access your site at http://159.223.204.248"
