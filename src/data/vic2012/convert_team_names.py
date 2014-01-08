import debate.models as m

for team in m.Team.objects.all():
    if team.reference.startswith(team.institution.code):
        new_reference = team.reference[len(team.institution.code):].strip()
        print "Renaming team", team.reference, "to", new_reference
        team.reference = new_reference
        team.save() # Comment this line out for dry run
    else:
        print "Leaving team", team.reference, "alone."