import csv
import debate.models as m

def main():
    m.Tournament.objects.filter(slug='preaustrals').delete()
    t = m.Tournament(slug='preaustrals')
    t.save()

    for i in range(1, 6):
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

    reader = csv.reader(open('speakers.csv'))
    for _, ins_name, name, in reader:
        print ins_name
        ins = m.Institution.objects.get(name=ins_name, tournament=t)
        team_name = ins.code
        team, _ = m.Team.objects.get_or_create(
            institution = ins,
            name = team_name
        )
        m.Speaker(
            name = name,
            team = team
        ).save()

    reader = csv.reader(open('judges.csv'))
    for _, ins_name, name, score in reader:
        print ins_name
        ins = m.Institution.objects.get(name=ins_name, tournament=t)
        m.Adjudicator(
            name = name,
            institution = ins
        ).save()

    reader = csv.reader(open('venues.csv'))
    for room, priority, group in reader:

        try:
            group = int(group)
        except ValueError:
            group = None

        m.Venue(
            tournament = t,
            group = group,
            name = room,
            priority = priority
        ).save()

if __name__ == '__main__':
    main()


