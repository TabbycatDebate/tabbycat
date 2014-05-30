"""Prints the entire action log."""

import header
import debate.models as m

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.parse_args()

AL = m.ActionLog

for al in m.ActionLog.objects.order_by('-timestamp'):
    print repr(al)