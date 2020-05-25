import os
import pathlib

from split_settings.tools import optional, include


# ==============================================================================
# Environments
# ==============================================================================

base_settings = [
    'core.py',
    optional('local.py'),
]

if os.environ.get('TRAVIS', '') == 'true':
    base_settings.append('travis.py')

if os.environ.get('IN_DOCKER', '') and bool(int(os.environ['IN_DOCKER'])):
    base_settings.append('docker.py')

if os.environ.get('DJANGO_SECRET_KEY', ''):
    base_settings.append('heroku.py')

if os.environ.get('LOCAL_DEVELOPMENT', ''):
    expected_file = pathlib.Path(__file__).parent / 'development.py'
    if not expected_file.exists():
        raise RuntimeError("development.py not found\n"
            "Hint: Copy settings/development.example to settings/development.py and modify,\n"
            "      or unset the LOCAL_DEVELOPMENT environment variable.")
    base_settings.append('development.py')


include(*base_settings)
