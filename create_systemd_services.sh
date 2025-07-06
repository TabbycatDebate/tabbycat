#!/bin/bash

# Create systemd service files for Tabbycat

set -e

APP_DIR="/opt/tabbycat"
APP_USER="tabbycat"

echo "🔧 Creating systemd service files..."

# Create Gunicorn service for WSGI
cat > /etc/systemd/system/tabbycat-wsgi.service << EOF
[Unit]
Description=Tabbycat WSGI Server
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=ON_DIGITALOCEAN=1
EnvironmentFile=/etc/environment
ExecStart=$APP_DIR/venv/bin/gunicorn wsgi:application --config ./config/gunicorn_digitalocean.conf
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create Daphne service for ASGI (WebSockets)
cat > /etc/systemd/system/tabbycat-asgi.service << EOF
[Unit]
Description=Tabbycat ASGI Server (WebSockets)
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=ON_DIGITALOCEAN=1
EnvironmentFile=/etc/environment
ExecStart=$APP_DIR/venv/bin/python ./tabbycat/run-asgi.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create worker service for background tasks
cat > /etc/systemd/system/tabbycat-worker.service << EOF
[Unit]
Description=Tabbycat Background Worker
After=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
Environment=ON_DIGITALOCEAN=1
EnvironmentFile=/etc/environment
ExecStart=$APP_DIR/venv/bin/python tabbycat/manage.py runworker notifications adjallocation venues
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable services
systemctl daemon-reload
systemctl enable tabbycat-wsgi.service
systemctl enable tabbycat-asgi.service
systemctl enable tabbycat-worker.service

# Start services
systemctl start tabbycat-wsgi.service
systemctl start tabbycat-asgi.service
systemctl start tabbycat-worker.service

echo "✅ Systemd services created and started!"
echo "📊 Service status:"
systemctl status tabbycat-wsgi.service --no-pager
systemctl status tabbycat-asgi.service --no-pager
systemctl status tabbycat-worker.service --no-pager
