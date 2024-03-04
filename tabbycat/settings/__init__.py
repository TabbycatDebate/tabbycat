import os
import logging
import sys

from split_settings.tools import optional, include


root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

# ==============================================================================
# Environments
# ==============================================================================

base_settings = [
    'core.py',
]

if os.environ.get('GITHUB_CI', '') and bool(os.environ['GITHUB_CI']):
    base_settings.append('github.py')
    root.info('SPLIT_SETTINGS: imported github.py')
elif os.environ.get('IN_DOCKER', '') and bool(int(os.environ['IN_DOCKER'])):
    base_settings.append('docker.py')
    root.info('SPLIT_SETTINGS: imported docker.py')
elif os.environ.get('ON_HEROKU', ''):
    base_settings.append('heroku.py')
    root.info('SPLIT_SETTINGS: imported heroku.py')
elif os.environ.get('ON_RENDER', ''):
    base_settings.append('render.py')
    root.info('SPLIT_SETTINGS: imported render.py')
else:
    base_settings.append('local.py')
    if os.environ.get('LOCAL_DEVELOPMENT', ''):
        base_settings.append('development.py')
        root.info('SPLIT_SETTINGS: imported local.py & development.py')
    else:
        root.info('SPLIT_SETTINGS: imported local.py')

include(*base_settings)
