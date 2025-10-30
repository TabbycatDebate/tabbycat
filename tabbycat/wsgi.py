import os

from django.core.wsgi import get_wsgi_application

# Needed for WSGI Callable
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tabbycat.settings")

# Needed for waitress/gunicorn serving
application = get_wsgi_application()
