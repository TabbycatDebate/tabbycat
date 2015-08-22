"""Prints the entire action log."""

import header
from actionlog.models import ActionLogEntry

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

AL = ActionLogEntry

for al in ActionLogEntry.objects.order_by('-timestamp'):
    print(repr(al))