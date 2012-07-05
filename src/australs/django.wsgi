import os
import sys
sys.path.append("/home/czlee/www/bios/debate/src")

os.environ["DJANGO_SETTINGS_MODULE"] = "australs.settings"

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()