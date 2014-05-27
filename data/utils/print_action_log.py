"""Prints the entire action log."""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import sys
sys.path.append(os.path.abspath(os.path.join(os.environ.get("VIRTUAL_ENV"), "..")))
import debate.models as m

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

AL = m.ActionLog

for al in m.ActionLog.objects.order_by('-timestamp'):
    print repr(al)