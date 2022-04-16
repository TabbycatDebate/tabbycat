import os

from split_settings.tools import optional, include


# ==============================================================================
# Environments
# ==============================================================================

base_settings = [
    'core.py',
]

if os.environ.get('GITHUB_CI', ''):
    base_settings.append('github.py')
elif os.environ.get('IN_DOCKER', '') and bool(int(os.environ['IN_DOCKER'])):
    base_settings.append('docker.py')
elif os.environ.get('ON_HEROKU', ''):
    base_settings.append('heroku.py')
elif os.environ.get('ON_RENDER', ''):
    base_settings.append('render.py')
else:
    base_settings.append('local.py')
    if os.environ.get('LOCAL_DEVELOPMENT', ''):
        base_settings.append('development.py')

include(*base_settings)
