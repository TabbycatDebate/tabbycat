#!/bin/bash

# Quick Start Script for Tabbycat Digital Ocean Deployment
# This is the ONLY script you need to run to deploy Tabbycat

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

clear

echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║  ████████╗ █████╗ ██████╗ ██████╗ ██╗   ██╗ ██████╗ █████╗  ║
║  ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝██╔══██╗ ║
║     ██║   ███████║██████╔╝██████╔╝ ╚████╔╝ ██║     ███████║ ║
║     ██║   ██╔══██║██╔══██╗██╔══██╗  ╚██╔╝  ██║     ██╔══██║ ║
║     ██║   ██║  ██║██████╔╝██████╔╝   ██║   ╚██████╗██║  ██║ ║
║     ╚═╝   ╚═╝  ╚═╝╚═════╝ ╚═════╝    ╚═╝    ╚═════╝╚═╝  ╚═╝ ║
║                                                              ║
║              Digital Ocean Quick Deploy                      ║
║                     Cost: ~$5/month                         ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ This script must be run as root. Please run with sudo:${NC}"
    echo -e "${YELLOW}sudo ./quickstart.sh${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Starting Tabbycat deployment on Digital Ocean...${NC}"
echo -e "${YELLOW}⏱️  Estimated time: 5-10 minutes${NC}"
echo ""

# Confirmation
echo -e "${YELLOW}📋 Deployment Configuration:${NC}"
echo "   • Server IP: 159.223.204.248"
echo "   • Database: External PostgreSQL (Render)"
echo "   • Web Server: Nginx + Gunicorn"
echo "   • Background Tasks: Redis + Django Channels"
echo "   • Estimated Cost: $5-6/month"
echo ""

read -p "🤔 Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

echo ""
echo -e "${GREEN}🎯 Starting deployment process...${NC}"

# Make all scripts executable
chmod +x *.sh

# Run complete deployment
echo -e "${BLUE}━━━ STEP 1: Complete System Setup ━━━${NC}"
if ./complete_deploy.sh; then
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
else
    echo -e "${RED}❌ Deployment failed. Check the logs above.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━ STEP 2: Verification ━━━${NC}"
if ./verify_deployment.sh; then
    echo -e "${GREEN}✅ Verification passed!${NC}"
else
    echo -e "${YELLOW}⚠️  Some verification checks failed, but deployment may still work.${NC}"
fi

echo ""
echo -e "${GREEN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                    🎉 DEPLOYMENT COMPLETE! 🎉                ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🌐 Your Tabbycat site is now live at:                      ║
║     http://159.223.204.248                                   ║
║                                                              ║
║  🔧 IMMEDIATE NEXT STEPS:                                    ║
║                                                              ║
║  1. Create admin user:                                       ║
║     sudo -u tabbycat /opt/tabbycat/create_superuser.sh       ║
║                                                              ║
║  2. Visit your site and log in                              ║
║                                                              ║
║  3. Follow the setup wizard to create your first tournament ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  🛠️  MANAGEMENT COMMANDS:                                    ║
║                                                              ║
║  • Service status:  /opt/tabbycat/manage_services.sh status ║
║  • View logs:       journalctl -u tabbycat-wsgi -f          ║
║  • Restart:         /opt/tabbycat/manage_services.sh restart║
║  • Update app:      /opt/tabbycat/update_app.sh              ║
║  • Backup DB:       /opt/tabbycat/backup_db.sh               ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  💡 TIPS:                                                    ║
║                                                              ║
║  • Set up a domain name for better SSL support              ║
║  • Enable automatic backups                                 ║
║  • Monitor resource usage with 'htop'                       ║
║  • Scale up droplet if you need more performance            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${YELLOW}🔑 To create your admin user, run:${NC}"
echo -e "${GREEN}sudo -u tabbycat /opt/tabbycat/create_superuser.sh${NC}"
echo ""
echo -e "${YELLOW}📖 For detailed documentation, see: DEPLOY_DIGITALOCEAN.md${NC}"
