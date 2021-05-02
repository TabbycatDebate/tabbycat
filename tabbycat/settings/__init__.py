import os

from split_settings.tools import optional, include


# ==============================================================================
# Environments
# ==============================================================================

base_settings = [
    'core.py',
    optional('local.py'),
]

if os.environ.get('CI', '') == 'true':
    base_settings.append('github.py')

if os.environ.get('IN_DOCKER', '') and bool(int(os.environ['IN_DOCKER'])):
    base_settings.append('docker.py')

if os.environ.get('DJANGO_SECRET_KEY', ''):
    base_settings.append('heroku.py')

if os.environ.get('LOCAL_DEVELOPMENT', ''):
    base_settings.append('development.py')


include(*base_settings)
