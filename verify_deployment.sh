#!/bin/bash

# Verification script to check Tabbycat deployment
# Run this after deployment to verify everything is working

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Tabbycat Deployment Verification${NC}"
echo "=================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    USER_PREFIX="sudo -u tabbycat"
else
    USER_PREFIX=""
fi

# Function to check service status
check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo -e "✅ $service: ${GREEN}Running${NC}"
        return 0
    else
        echo -e "❌ $service: ${RED}Stopped${NC}"
        return 1
    fi
}

# Function to check HTTP response
check_http() {
    local url=$1
    local expected_code=$2
    local response=$(curl -s -o /dev/null -w "%{http_code}" $url 2>/dev/null || echo "000")
    
    if [ "$response" = "$expected_code" ]; then
        echo -e "✅ HTTP $url: ${GREEN}$response${NC}"
        return 0
    else
        echo -e "❌ HTTP $url: ${RED}$response${NC}"
        return 1
    fi
}

echo -e "\n${YELLOW}1. Checking System Services...${NC}"
all_services_ok=true
check_service "nginx" || all_services_ok=false
check_service "redis-server" || all_services_ok=false
check_service "tabbycat-wsgi" || all_services_ok=false
check_service "tabbycat-asgi" || all_services_ok=false
check_service "tabbycat-worker" || all_services_ok=false

echo -e "\n${YELLOW}2. Checking File Permissions...${NC}"
directories_ok=true
if [ -d "/opt/tabbycat" ] && [ -r "/opt/tabbycat" ]; then
    echo -e "✅ Application directory: ${GREEN}OK${NC}"
else
    echo -e "❌ Application directory: ${RED}Missing or not readable${NC}"
    directories_ok=false
fi

if [ -d "/var/www/tabbycat/static" ] && [ -r "/var/www/tabbycat/static" ]; then
    echo -e "✅ Static files directory: ${GREEN}OK${NC}"
else
    echo -e "❌ Static files directory: ${RED}Missing or not readable${NC}"
    directories_ok=false
fi

if [ -d "/var/log/tabbycat" ] && [ -w "/var/log/tabbycat" ]; then
    echo -e "✅ Log directory: ${GREEN}OK${NC}"
else
    echo -e "❌ Log directory: ${RED}Missing or not writable${NC}"
    directories_ok=false
fi

echo -e "\n${YELLOW}3. Checking Database Connection...${NC}"
database_ok=true
if $USER_PREFIX bash -c "source /opt/tabbycat/venv/bin/activate && source /etc/environment && cd /opt/tabbycat && python tabbycat/manage.py check --database default" >/dev/null 2>&1; then
    echo -e "✅ Database connection: ${GREEN}OK${NC}"
else
    echo -e "❌ Database connection: ${RED}Failed${NC}"
    database_ok=false
fi

echo -e "\n${YELLOW}4. Checking Redis Connection...${NC}"
redis_ok=true
if redis-cli ping >/dev/null 2>&1; then
    echo -e "✅ Redis connection: ${GREEN}OK${NC}"
else
    echo -e "❌ Redis connection: ${RED}Failed${NC}"
    redis_ok=false
fi

echo -e "\n${YELLOW}5. Checking HTTP Endpoints...${NC}"
http_ok=true
# Wait a moment for services to be ready
sleep 2

# Check if main site is accessible
if check_http "http://127.0.0.1" "200"; then
    echo -e "✅ Main site: ${GREEN}Accessible${NC}"
else
    echo -e "❌ Main site: ${RED}Not accessible${NC}"
    http_ok=false
fi

# Check static files
if check_http "http://127.0.0.1/static/css/style.css" "200"; then
    echo -e "✅ Static files: ${GREEN}Accessible${NC}"
else
    echo -e "⚠️  Static files: ${YELLOW}May not be properly configured${NC}"
fi

echo -e "\n${YELLOW}6. Checking System Resources...${NC}"
# Memory check
total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
used_mem=$(free -m | awk 'NR==2{printf "%.0f", $3}')
mem_usage=$((used_mem * 100 / total_mem))

if [ $mem_usage -lt 80 ]; then
    echo -e "✅ Memory usage: ${GREEN}${mem_usage}% of ${total_mem}MB${NC}"
else
    echo -e "⚠️  Memory usage: ${YELLOW}${mem_usage}% of ${total_mem}MB (High)${NC}"
fi

# Disk check
disk_usage=$(df /opt/tabbycat | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -lt 80 ]; then
    echo -e "✅ Disk usage: ${GREEN}${disk_usage}%${NC}"
else
    echo -e "⚠️  Disk usage: ${YELLOW}${disk_usage}% (High)${NC}"
fi

echo -e "\n${YELLOW}7. Checking Log Files...${NC}"
logs_ok=true
for logfile in "/var/log/tabbycat/django.log" "/var/log/tabbycat/gunicorn_error.log" "/var/log/nginx/tabbycat_error.log"; do
    if [ -f "$logfile" ]; then
        # Check for recent errors (last 10 lines)
        error_count=$(tail -10 "$logfile" 2>/dev/null | grep -i error | wc -l)
        if [ $error_count -eq 0 ]; then
            echo -e "✅ $(basename $logfile): ${GREEN}No recent errors${NC}"
        else
            echo -e "⚠️  $(basename $logfile): ${YELLOW}$error_count recent errors${NC}"
            logs_ok=false
        fi
    else
        echo -e "❌ $(basename $logfile): ${RED}Missing${NC}"
        logs_ok=false
    fi
done

# Overall status
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                        VERIFICATION SUMMARY${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if $all_services_ok && $directories_ok && $database_ok && $redis_ok && $http_ok; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED! Your Tabbycat deployment is ready!${NC}"
    echo -e "${GREEN}🌐 Access your site at: http://159.223.204.248${NC}"
    echo -e "${GREEN}👤 Create a superuser: sudo -u tabbycat /opt/tabbycat/create_superuser.sh${NC}"
    exit 0
else
    echo -e "${RED}❌ SOME CHECKS FAILED. Please review the issues above.${NC}"
    echo ""
    echo -e "${YELLOW}Common fixes:${NC}"
    echo "• Restart services: /opt/tabbycat/manage_services.sh restart"
    echo "• Check logs: journalctl -u tabbycat-wsgi --lines=20"
    echo "• Verify environment: source /etc/environment && env | grep DJANGO"
    echo "• Test database: cd /opt/tabbycat && source venv/bin/activate && python tabbycat/manage.py check"
    exit 1
fi
