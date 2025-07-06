#!/bin/bash

# Setup Nginx configuration for Tabbycat

set -e

DOMAIN="159.223.204.248"  # Your droplet IP
STATIC_DIR="/var/www/tabbycat"

echo "🌐 Setting up Nginx configuration..."

# Create Nginx site configuration
cat > /etc/nginx/sites-available/tabbycat << EOF
# Upstream servers
upstream wsgi_server {
    server 127.0.0.1:8000;
}

upstream asgi_server {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name $DOMAIN;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Static files
    location /static/ {
        alias $STATIC_DIR/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Media files
    location /media/ {
        alias $STATIC_DIR/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # WebSocket connections (for real-time features)
    location /ws/ {
        proxy_pass http://asgi_server;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
    
    # Main application
    location / {
        proxy_pass http://wsgi_server;
        proxy_set_header Host \$http_host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }
    
    # Error pages
    error_page 500 502 503 504 /50x.html;
    location = /50x.html {
        root /var/www/html;
    }
    
    # Logging
    access_log /var/log/nginx/tabbycat_access.log;
    error_log /var/log/nginx/tabbycat_error.log;
    
    # Security: hide nginx version
    server_tokens off;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/tabbycat /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Start and enable nginx
systemctl start nginx
systemctl enable nginx

echo "✅ Nginx configured and started!"
echo "🌐 Your site should be accessible at: http://$DOMAIN"
