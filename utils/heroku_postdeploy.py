from django.core import management
from django.conf import settings

# Run migrations
management.call_command('migrate')

# Create a superuser with a default name and password
settings.AUTH_USER_MODEL.create_superuser('admin', '', 'admin')
