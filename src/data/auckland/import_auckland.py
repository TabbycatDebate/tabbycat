import csv
import debate.models as m

def main():
    m.Tournament.objects.filter(slug='australs').delete()
    t = m.Tournament(slug='australs')
    t.save()

    for i in range(1, 9):
        if i == 1:
            rtype = m.Round.TYPE_RANDOM
        else:
            rtype = m.Round.TYPE_PRELIM

        m.Round(
            tournament = t,
            seq = i,
            name = 'Round %d' % i,
            type = rtype,
            feedback_weight = min((i-1)*0.1, 0.5),
        ).save()

    t.current_round = m.Round.objects.get(tournament=t, seq=1)
    t.save()

    reader = csv.reader(open('institutions.csv'))
    for code, name in reader:
        i = m.Institution(code=code, name=name, tournament=t)
        i.save()

    reader = csv.reader(open('people.csv'))
    for barcode, ins_name, team, first, last in reader:
        print ins_name
        ins = m.Institution.objects.get(name=ins_name, tournament=t)
        if team == 'Judge':
            m.Adjudicator(
                name = '%s %s' % (first, last),
                institution = ins,
                barcode_id = int(barcode),
            ).save()
        elif team == 'Observer':
            continue
        else:
            team_num = int(team)

            team_name = '%s %d' % (ins.code, team_num)

            team, _ = m.Team.objects.get_or_create(
                institution = ins,
                name = team_name,
            )
            
            m.Speaker(
                name = '%s %s' % (first, last),
                team = team,
            ).save()

    #TODO (dummy venues)
    reader = csv.reader(open('venues.csv'))
    for data in reader:
        building, group, room, priority = data[:4]

        try:
            group = int(group)
        except ValueError:
            group = None

        m.Venue(
            tournament = t,
            group = group,
            name = '%s %s' % (building, room),
            priority = priority,
        ).save()

    # swing team
    ins = m.Institution(
        tournament = t,
        code='SWING',
        name='SWING',
    )
    ins.save()
    team=m.Team(
        institution = ins,
        name = 'SWING',
    )
    team.save()
    for i in range(1, 4):
        m.Speaker(
            name='Swing %d' % i,
            team=team
        ).save()


    # TODO [remove]
    #for r in m.Round.objects.all():
    #    r.activate_all()

    from django.contrib.auth.models import User

    def add_conflicts(adj, teams):
        for team in teams:
            m.AdjudicatorConflict(
                adjudicator = adj,
                team = team,
            ).save()

    from debate.models import Adjudicator
    for adj in Adjudicator.objects.all():
        add_conflicts(adj, m.Team.objects.filter(institution=adj.institution))

    reader = csv.reader(open('conflicts.csv'))
    for data in reader:
        barcode, institution, first, last, personal, add_institution = data
        adj = Adjudicator.objects.get(barcode_id=barcode)

        for ins_code in add_institution.split(','):
            ins_code = ins_code.strip()
            if ins_code:
                print ins_code
                ins = m.Institution.objects.get(code=ins_code, tournament=t)
                add_conflicts(adj, m.Team.objects.filter(institution=ins))

        for team_name in personal.split(','):
            team_name = team_name.strip()
            if team_name:
                print team_name
                team = m.Team.objects.get(name=team_name, institution__tournament=t)
                add_conflicts(adj, [team])



if __name__ == '__main__':
    main()


