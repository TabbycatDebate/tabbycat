#!/bin/bash

# Environment setup script for Digital Ocean deployment
# This script sets up the required environment variables

echo "🔧 Setting up environment variables for Tabbycat..."

# Generate a secure Django secret key
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Create environment file
cat > /etc/environment << EOF
# Tabbycat Environment Variables
ON_DIGITALOCEAN=1
DJANGO_SECRET_KEY=$SECRET_KEY
DEBUG=0
REDIS_URL=redis://127.0.0.1:6379/0

# Optional: Set timezone (uncomment and modify if needed)
# TIME_ZONE=Australia/Melbourne

# Optional: Email configuration (uncomment and configure if needed)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=1
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Optional: Tab Director Email for error reporting
# TAB_DIRECTOR_EMAIL=admin@yourdomain.com
EOF

echo "✅ Environment variables configured!"
echo "📄 Environment file created at: /etc/environment"
echo ""
echo "🔑 Generated Django Secret Key: $SECRET_KEY"
echo ""
echo "⚠️  IMPORTANT: Keep your secret key secure!"
