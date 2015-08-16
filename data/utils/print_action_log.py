"""Prints the entire action log."""

import header
from actionlog.models import ActionLog

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

AL = ActionLog

for al in ActionLog.objects.order_by('-timestamp'):
    print repr(al)