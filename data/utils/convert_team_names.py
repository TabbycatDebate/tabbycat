"""Changes team names from e.g. 'Auckland 1' to '1'."""

import header
from participants.models import Team

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--dry-run", action="store_true")
args = parser.parse_args()

for team in Team.objects.all():
    if team.reference.startswith(team.institution.code):
        new_reference = team.reference[len(team.institution.code):].strip()
        print "Renaming team", team.reference, "to", new_reference
        team.reference = new_reference
        if not args.dry_run:
            team.save()
    else:
        print "Leaving team", team.reference, "alone."