import csv
import debate.models as m

def main():
    m.Tournament.objects.filter(slug='australs').delete()
    t = m.Tournament(slug='australs')
    t.save()

    for i in range(1, 8):
        if i == 1:
            rtype = m.Round.TYPE_RANDOM
        else:
            rtype = m.Round.TYPE_PRELIM

        m.Round(
            tournament = t,
            seq = i,
            name = 'Round %d' % i,
            type = rtype,
            feedback_weight = max((i-1)*0.1, 0.5),
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
    for i in range(1, 52):
        m.Venue(
            tournament = t,
            name = 'Room %02d' % i,
            priority = 10-(i//10),
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
    for r in m.Round.objects.all():
        r.activate_all()



if __name__ == '__main__':
    main()


