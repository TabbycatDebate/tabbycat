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

# Make local settings optional: on some build environments (Heroku slug compile)
# the repository may not include a `local.py`. To avoid raising OSError during
# collectstatic or other build-time management commands, only include files
# that actually exist on disk, and keep `local.py` optional.
settings_dir = os.path.dirname(__file__)
final_includes = []
for s in base_settings:
    # compute the filesystem path for the candidate settings file
    candidate = os.path.join(settings_dir, s)
    if os.path.exists(candidate):
        # file exists — include it (wrap local.py with optional() for clarity)
        final_includes.append(optional(s) if s.endswith('local.py') else s)
    else:
        # file missing
        if s.endswith('local.py'):
            root.info(f"SPLIT_SETTINGS: skipping missing optional settings file: {s}")
            # don't include missing optional local.py
            continue
        # For required files, raise a clear error so builds fail loudly
        raise OSError(f'No such file: {candidate}')

include(*final_includes)
