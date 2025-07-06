# Tabbycat Digital Ocean Deployment Guide

This guide will help you deploy Tabbycat on a Digital Ocean droplet with an external PostgreSQL database for under $5/month.

## 📋 Prerequisites

- Digital Ocean droplet (Ubuntu 20.04 or later)
- External PostgreSQL database (already configured)
- SSH access to your droplet

## 💰 Cost Breakdown

- **Digital Ocean Droplet (Basic)**: $5/month
  - 1GB RAM
  - 1 vCPU
  - 25GB SSD
  - 1TB transfer
- **Total estimated cost**: ~$5-6/month

## 🚀 Quick Deployment

### Step 1: Connect to Your Droplet

```bash
ssh root@159.223.204.248
# Password: ilove@@45Star
```

### Step 2: Upload and Run Deployment

```bash
# Upload this project to your droplet (use scp, git clone, or copy-paste)
# Then run:
chmod +x complete_deploy.sh
./complete_deploy.sh
```

### Step 3: Create Superuser

```bash
sudo -u tabbycat /opt/tabbycat/create_superuser.sh
```

### Step 4: Access Your Site

Visit: http://159.223.204.248

## 🔧 Manual Deployment (Step by Step)

If you prefer to run each step manually:

### 1. System Setup
```bash
chmod +x deploy_digitalocean.sh
./deploy_digitalocean.sh
```

### 2. Create Services
```bash
chmod +x create_systemd_services.sh
./create_systemd_services.sh
```

### 3. Setup Nginx
```bash
chmod +x setup_nginx.sh
./setup_nginx.sh
```

### 4. Create Superuser
```bash
cd /opt/tabbycat
source venv/bin/activate
source /etc/environment
python tabbycat/manage.py createsuperuser
```

## 🗄️ Database Configuration

The deployment is configured to use your external PostgreSQL database:

- **Host**: dpg-d1l186h5pdvs73bd0nv0-a.oregon-postgres.render.com
- **Database**: tab_2yw0
- **User**: tab
- **Password**: 57yqNclrMENfxxJuYmbBJ0u26FdDzOkB

## 🛠️ Management Commands

### Service Management
```bash
# Check status
/opt/tabbycat/manage_services.sh status

# Restart services
/opt/tabbycat/manage_services.sh restart

# View logs
/opt/tabbycat/manage_services.sh logs
```

### Application Updates
```bash
# Update to latest version
/opt/tabbycat/update_app.sh
```

### Database Backup
```bash
# Create backup
/opt/tabbycat/backup_db.sh
```

### View Live Logs
```bash
# WSGI server logs
journalctl -u tabbycat-wsgi -f

# ASGI server logs
journalctl -u tabbycat-asgi -f

# Worker logs
journalctl -u tabbycat-worker -f

# Nginx logs
tail -f /var/log/nginx/tabbycat_error.log
tail -f /var/log/nginx/tabbycat_access.log
```

## 🔍 Troubleshooting

### Common Issues

1. **Services not starting**
   ```bash
   systemctl status tabbycat-wsgi
   journalctl -u tabbycat-wsgi --lines=50
   ```

2. **Database connection issues**
   ```bash
   cd /opt/tabbycat
   source venv/bin/activate
   source /etc/environment
   python tabbycat/manage.py check --database default
   ```

3. **Static files not loading**
   ```bash
   cd /opt/tabbycat
   source venv/bin/activate
   source /etc/environment
   python tabbycat/manage.py collectstatic --noinput
   systemctl restart nginx
   ```

4. **Memory issues (if droplet runs out of memory)**
   ```bash
   # Add swap space
   fallocate -l 1G /swapfile
   chmod 600 /swapfile
   mkswap /swapfile
   swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

### Checking Resource Usage
```bash
# Memory usage
free -h

# Disk usage
df -h

# CPU usage
top

# Service resource usage
systemctl status tabbycat-wsgi tabbycat-asgi tabbycat-worker
```

## 🔐 Security Considerations

### Recommended Security Enhancements

1. **Setup UFW Firewall** (already done by deployment script)
   ```bash
   ufw status
   ```

2. **SSH Key Authentication** (recommended)
   ```bash
   # Add your public key to /root/.ssh/authorized_keys
   # Then disable password authentication in /etc/ssh/sshd_config
   ```

3. **SSL Certificate** (for production)
   ```bash
   # Install Certbot for Let's Encrypt
   apt install certbot python3-certbot-nginx
   certbot --nginx -d yourdomain.com
   ```

4. **Regular Updates**
   ```bash
   # System updates
   apt update && apt upgrade -y
   
   # Application updates
   /opt/tabbycat/update_app.sh
   ```

## 📊 Performance Optimization

### For Heavy Usage

If you need better performance, consider upgrading to a larger droplet:

- **$10/month**: 2GB RAM, 1 vCPU (recommended for 50+ concurrent users)
- **$20/month**: 4GB RAM, 2 vCPU (recommended for 100+ concurrent users)

### Monitoring
```bash
# Install monitoring tools
apt install htop iotop nethogs

# Monitor in real-time
htop           # Overall system
iotop          # Disk I/O
nethogs        # Network usage per process
```

## 🎯 Next Steps

1. **Custom Domain**: Point your domain to the droplet IP
2. **SSL Certificate**: Setup HTTPS with Let's Encrypt
3. **Monitoring**: Setup basic monitoring/alerting
4. **Backups**: Schedule regular database backups
5. **Updates**: Create a maintenance schedule

## 📞 Support

If you encounter issues:

1. Check the logs (see troubleshooting section)
2. Ensure all services are running
3. Verify database connectivity
4. Check available resources (memory, disk space)

The deployment creates several log files to help with debugging:
- `/var/log/tabbycat/django.log`
- `/var/log/tabbycat/gunicorn_access.log`
- `/var/log/tabbycat/gunicorn_error.log`
- `/var/log/nginx/tabbycat_access.log`
- `/var/log/nginx/tabbycat_error.log`
