"""Generic header for all utils scripts.
Use 'import header' at the top of every script."""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
venv = os.environ.get("VIRTUAL_ENV")
pyhome = os.environ.get("PYTHONHOME", "")
if venv is None and "heroku" not in pyhome:
    print("You must be in the virtual environment or Heroku to run this script.")
    exit()
root_path = os.path.abspath(os.path.join(venv, ".."))
if root_path not in sys.path: sys.path.append(root_path)
import django
django.setup()
