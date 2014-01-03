import csv
import debate.models as m

for adj in m.Adjudicator.objects.all():

    original_conflicts = m.AdjudicatorConflict.objects.filter(adjudicator = adj)
    if len(original_conflicts) == 0:
        print adj.name + " doesn't have any team conflicts"
        continue

    institutions = set(conflict.team.institution for conflict in original_conflicts)
    if len(institutions) > 1:
        print adj.name + " has conflicts associated with more than one team - check manually"
        continue

    ins = institutions.pop()

    # Check if all teams from the institution have an existing conflict
    for team in m.Team.objects.filter(institution = ins):
        try:
            m.AdjudicatorConflict.objects.get(adjudicator = adj, team = team)
        except m.AdjudicatorConflict.DoesNotExist:
            print adj.name + " did not have conflicts for all teams from " + ins.code + " - check manually"

    assert len(m.Team.objects.filter(institution = ins)) == len(original_conflicts)

    m.AdjudicatorInstitutionConflict(adjudicator = adj, institution = ins).save()

    # Remove the team conflicts that are the same as the institution conflict
    for conflict in original_conflicts:
        conflict.delete()