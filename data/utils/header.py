"""Generic header for all utils scripts.
Use 'import header' at the top of every script."""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
venv = os.environ.get("VIRTUAL_ENV")
pyhome = os.environ.get("PYTHONHOME", "")
if venv is not None:
    root_path = os.path.abspath(os.path.join(venv, ".."))
elif "heroku" in pyhome:
    root_path = os.environ.get("PYTHONPATH")
else:
    print("You must be in the virtual environment or Heroku to run this script.")
    exit()
if root_path not in sys.path: sys.path.append(root_path)
import django
django.setup()
