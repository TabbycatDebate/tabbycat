#!/bin/bash

# Complete Digital Ocean Deployment Script for Tabbycat
# Run this script on your Digital Ocean droplet as root

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                 Tabbycat Digital Ocean Setup                ║"
echo "║                                                              ║"
echo "║  This script will deploy Tabbycat on your Digital Ocean     ║"
echo "║  droplet with the external PostgreSQL database.             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run this script as root (sudo)${NC}"
    exit 1
fi

# Make all scripts executable
chmod +x *.sh

echo -e "${GREEN}🚀 Step 1: Running basic deployment setup...${NC}"
./deploy_digitalocean.sh

echo -e "${GREEN}🔧 Step 2: Creating systemd services...${NC}"
./create_systemd_services.sh

echo -e "${GREEN}🌐 Step 3: Setting up Nginx...${NC}"
./setup_nginx.sh

# Create a superuser creation script
echo -e "${GREEN}👤 Step 4: Creating superuser setup script...${NC}"
cat > /opt/tabbycat/create_superuser.sh << 'EOF'
#!/bin/bash
cd /opt/tabbycat
source venv/bin/activate
source /etc/environment
echo "Creating Django superuser..."
python tabbycat/manage.py createsuperuser
EOF

chmod +x /opt/tabbycat/create_superuser.sh
chown tabbycat:tabbycat /opt/tabbycat/create_superuser.sh

# Create maintenance scripts
echo -e "${GREEN}🔧 Step 5: Creating maintenance scripts...${NC}"

# Backup script
cat > /opt/tabbycat/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/tabbycat/backups"
mkdir -p $BACKUP_DIR
DATE=$(date +%Y%m%d_%H%M%S)
PGPASSWORD="57yqNclrMENfxxJuYmbBJ0u26FdDzOkB" pg_dump -h dpg-d1l186h5pdvs73bd0nv0-a.oregon-postgres.render.com -U tab -d tab_2yw0 > $BACKUP_DIR/backup_$DATE.sql
echo "Backup created: $BACKUP_DIR/backup_$DATE.sql"
# Keep only last 7 backups
ls -t $BACKUP_DIR/backup_*.sql | tail -n +8 | xargs -r rm
EOF

# Update script
cat > /opt/tabbycat/update_app.sh << 'EOF'
#!/bin/bash
cd /opt/tabbycat
echo "🔄 Pulling latest changes..."
sudo -u tabbycat git pull
echo "📦 Installing dependencies..."
sudo -u tabbycat bash -c "source venv/bin/activate && pipenv install --system --deploy"
sudo -u tabbycat npm ci --only=production
echo "🔨 Building static files..."
sudo -u tabbycat bash -c "source ~/.bashrc && npm run build"
echo "📁 Collecting static files..."
sudo -u tabbycat bash -c "source venv/bin/activate && source /etc/environment && python tabbycat/manage.py collectstatic --noinput"
echo "🗄️ Running migrations..."
sudo -u tabbycat bash -c "source venv/bin/activate && source /etc/environment && python tabbycat/manage.py migrate"
echo "🔄 Restarting services..."
systemctl restart tabbycat-wsgi tabbycat-asgi tabbycat-worker
echo "✅ Update complete!"
EOF

# Service management script
cat > /opt/tabbycat/manage_services.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        systemctl start tabbycat-wsgi tabbycat-asgi tabbycat-worker nginx redis-server
        echo "✅ All services started"
        ;;
    stop)
        systemctl stop tabbycat-wsgi tabbycat-asgi tabbycat-worker
        echo "🛑 Tabbycat services stopped"
        ;;
    restart)
        systemctl restart tabbycat-wsgi tabbycat-asgi tabbycat-worker nginx
        echo "🔄 Services restarted"
        ;;
    status)
        echo "📊 Service Status:"
        systemctl status tabbycat-wsgi --no-pager
        systemctl status tabbycat-asgi --no-pager
        systemctl status tabbycat-worker --no-pager
        systemctl status nginx --no-pager
        systemctl status redis-server --no-pager
        ;;
    logs)
        echo "📋 Recent logs:"
        journalctl -u tabbycat-wsgi --lines=20 --no-pager
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
EOF

chmod +x /opt/tabbycat/*.sh

# Setup firewall
echo -e "${GREEN}🔥 Step 6: Setting up firewall...${NC}"
ufw --force enable
ufw allow ssh
ufw allow http
ufw allow https
ufw --force reload

# Setup log rotation
echo -e "${GREEN}📋 Step 7: Setting up log rotation...${NC}"
cat > /etc/logrotate.d/tabbycat << EOF
/var/log/tabbycat/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 tabbycat tabbycat
    postrotate
        systemctl reload tabbycat-wsgi tabbycat-asgi tabbycat-worker
    endscript
}
EOF

# Check database connection
echo -e "${GREEN}🗄️ Step 8: Testing database connection...${NC}"
if sudo -u tabbycat bash -c "source /opt/tabbycat/venv/bin/activate && source /etc/environment && cd /opt/tabbycat && python tabbycat/manage.py check --database default"; then
    echo -e "${GREEN}✅ Database connection successful!${NC}"
else
    echo -e "${RED}❌ Database connection failed. Please check your database settings.${NC}"
    exit 1
fi

# Final status check
echo -e "${GREEN}🔍 Step 9: Final system check...${NC}"
sleep 5

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    🎉 DEPLOYMENT COMPLETE! 🎉                ║"
echo "╠══════════════════════════════════════════════════════════════╣"
echo "║                                                              ║"
echo "║  Your Tabbycat installation is ready!                       ║"
echo "║                                                              ║"
echo "║  📍 URL: http://159.223.204.248                              ║"
echo "║                                                              ║"
echo "║  🔧 NEXT STEPS:                                              ║"
echo "║  1. Create superuser: sudo -u tabbycat /opt/tabbycat/create_superuser.sh ║"
echo "║  2. Visit your site and complete setup                      ║"
echo "║                                                              ║"
echo "║  🛠️  USEFUL COMMANDS:                                        ║"
echo "║  • Manage services: /opt/tabbycat/manage_services.sh status  ║"
echo "║  • Update app: /opt/tabbycat/update_app.sh                   ║"
echo "║  • Backup DB: /opt/tabbycat/backup_db.sh                     ║"
echo "║  • View logs: journalctl -u tabbycat-wsgi -f                 ║"
echo "║                                                              ║"
echo "║  💰 Monthly cost estimate: ~$5-6 USD                         ║"
echo "║  (Droplet: $5 + minimal bandwidth)                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Show final service status
echo -e "${GREEN}📊 Service Status:${NC}"
systemctl is-active tabbycat-wsgi && echo "✅ WSGI Server: Running" || echo "❌ WSGI Server: Stopped"
systemctl is-active tabbycat-asgi && echo "✅ ASGI Server: Running" || echo "❌ ASGI Server: Stopped"
systemctl is-active tabbycat-worker && echo "✅ Worker: Running" || echo "❌ Worker: Stopped"
systemctl is-active nginx && echo "✅ Nginx: Running" || echo "❌ Nginx: Stopped"
systemctl is-active redis-server && echo "✅ Redis: Running" || echo "❌ Redis: Stopped"
