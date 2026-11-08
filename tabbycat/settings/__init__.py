import os
import logging

from split_settings.tools import optional, include


logger = logging.getLogger(__name__)

# ==============================================================================
# Environments
# ==============================================================================

base_settings = [
    'core.py',
]

if os.environ.get('GITHUB_CI', '') and bool(os.environ['GITHUB_CI']):
    base_settings.append('github.py')
    logger.info('SPLIT_SETTINGS: imported github.py')
elif os.environ.get('IN_DOCKER', '') and bool(int(os.environ['IN_DOCKER'])):
    base_settings.append('docker.py')
    logger.info('SPLIT_SETTINGS: imported docker.py')
elif os.environ.get('ON_HEROKU', ''):
    base_settings.append('heroku.py')
    logger.info('SPLIT_SETTINGS: imported heroku.py')
elif os.environ.get('ON_RENDER', ''):
    base_settings.append('render.py')
    logger.info('SPLIT_SETTINGS: imported render.py')
else:
    base_settings.append('local.py')
    if os.environ.get('LOCAL_DEVELOPMENT', ''):
        base_settings.append('development.py')
        logger.info('SPLIT_SETTINGS: imported local.py & development.py')
    else:
        logger.info('SPLIT_SETTINGS: imported local.py')

include(*base_settings)
