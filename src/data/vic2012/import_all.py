import csv
import debate.models as m

NUM_ROUNDS = 8

def add_conflicts(adj, teams):
    for team in teams:
        m.AdjudicatorConflict(
            adjudicator = adj,
            team = team,
        ).save()

def get_priority(room):
    for i in xrange(1, len(room)):
        candidate = room[0:i]
        if not (candidate.isalpha() and candidate.isupper()):
            break
    i -= 1
    building = room[0:i]
    priority = 50
    priorities = {"FT": 0, "WR": 20, "KP": 30, "SUB": 40}
    if building in priorities:
        priority = priorities[building]
    return priority

def main(suffix=None, verbose=False):

    def make_filename(name):
        if suffix:
            return name + "-" + suffix + ".csv"
        else:
            return name + ".csv"

    def verbose_print(message):
        if verbose:
            print message

    print "Deleting and re-creating tournament..."
    m.Tournament.objects.filter(slug='australs2012').delete()
    t = m.Tournament(slug='australs2012')
    t.save()

    print "Adding rounds..."

    for i in range(1, NUM_ROUNDS+1):
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

    print "Importing from files..."

    print('institutions.csv')
    reader = csv.reader(open('institutions.csv'))
    for name, code in reader:
        i = m.Institution(code=code, name=name, tournament=t)
        i.save()

    filename = make_filename('debaters')
    print filename
    reader = csv.reader(open(filename))
    header_row = reader.next() # skip the first row (headers)
    first_column = header_row.index("Name")
    for row in reader:
        # for some reason there are a bunch of stray cells at the end of each row
        # we only care about the non-blank cells, i.e. the first four
        name, ins_name, attendance, team_number = row[first_column:first_column+4]
        verbose_print(ins_name)

        if attendance != "Debater":
            print("{0} is not a debater? ({1})".format(name, attendance))

        ins_name_full = ins_name
        # extract the institution name from Seb's longer institution name
        # These are in the format "Name of University 1 Member 1", where the
        # first number is the team number and the second number is the member number
        if ins_name[-1].isdigit():
            member_number = ins_name[-1]
            ins_name = ins_name[:-1].rstrip()
        else:
            member_number = None
            print("No member number in: {0}".format(ins_name_full))

        if ins_name.endswith("Member"):
            ins_name = ins_name[:-6].rstrip()
        else:
            print("No 'Member' in: {0}".format(ins_name_full))

        if ins_name[-1].isdigit():
            ins_name_team_number = ins_name[-1]
            ins_name = ins_name[:-1].rstrip()
        else:
            ins_name_team_number = None
            print("No team number in: {0}".format(ins_name_full))

        if ins_name_team_number is not None and ins_name_team_number != team_number:
            print("Team numbers don't match: {0}, {1}".format(ins_name_full, team_number))

        ins = m.Institution.objects.get(name=ins_name, tournament=t)
        team_name = ins.code + " " + team_number
        team, _ = m.Team.objects.get_or_create(
            institution = ins,
            name = team_name
        )
        m.Speaker(
            name = name,
            team = team
        ).save()

    filename = make_filename('judges')
    print filename
    reader = csv.reader(open(filename))
    header_row = reader.next() # skip the first row (headers)
    first_column = header_row.index("Name")
    for row in reader:
        verbose_print(ins_name)

        name, ins_name, attendance = row[first_column:first_column+3]

        if attendance not in ["Judge", "Independent", "CA", "DCA", "Observer", "Org Comm"]:
            print("{0} is not a judge, independent, CA, DCA, observer or org comm? ({1})".format(name, attendance))

        ins_name_full = ins_name

        if ins_name == "Adjudication Core":
            if attendance not in ["CA", "DCA"]:
                print("{0} is in the adjudication core, but not a CA or DCA".format(name))

        elif ins_name == "Org Comm":
            # Do nothing, we don't care about org comms
            continue

        elif attendance == "Observer" and "Observer" in ins_name:
            # Do nothing, we don't care about observers
            continue

        else:
            # extract the institution name from Seb's longer institution name
            # These are in the format "Name of University 1 Judge 1", where the
            # first number is the team number and the second number is the member number
            if ins_name[-1].isdigit():
                member_number = ins_name[-1]
                ins_name = ins_name[:-1].rstrip()
            else:
                member_number = None
                print("No member number in: {0}".format(ins_name_full))

            if ins_name.endswith("Judge"):
                ins_name_attendance = ins_name[-5:]
                ins_name = ins_name[:-5].rstrip()
            elif ins_name.endswith("Independent"):
                ins_name_attendance = ins_name[-11:]
                ins_name = ins_name[:-11].rstrip()
            else:
                ins_name_attendance = None
                print("No 'Judge' or 'Independent' in: {0}".format(ins_name_full))

            if ins_name[-1].isdigit():
                ins_name = ins_name[:-1].rstrip()
                print("Judge has team number in: {0}".format(ins_name_full))

            if ins_name_attendance is not None and ins_name_attendance != attendance:
                print("Attendances don't match: {0}, {1}".format(ins_name_full, attendance))

        # Override institution name for independents, put in independents pseudo-institution instead
        if attendance == "Independent":
            ins = m.Institution.objects.get(name="Independent Adjudicators", tournament=t)
            adj = m.Adjudicator(
                name = name,
                institution = ins,
                test_score = 2
            )
            adj.save()
            try:
                home_ins = m.Institution.objects.get(name=ins_name, tournament=t)
            except m.Institution.DoesNotExist:
                print("No institution '{0}', institution conflict not added for independent {1}".format(ins_name, name))
            else:
                add_conflicts(adj, m.Team.objects.filter(institution=home_ins))

        else:
            ins = m.Institution.objects.get(name=ins_name, tournament=t)
            m.Adjudicator(
                name = name,
                institution = ins,
                test_score = ins_name == "Adjudication Core" and 5 or 1
            ).save()

    # Add conflicts for own institutions
    for adj in m.Adjudicator.objects.all():
        add_conflicts(adj, m.Team.objects.filter(institution=adj.institution))

    reader = csv.reader(open('venues.csv'))
    print('venues.csv')
    reader.next() # skip the first row (headers)
    for row in reader:
        group, rooms = row[0:2]
        rooms = rooms.split("/")

        try:
            group = int(group)
        except ValueError:
            group = None

        for room in rooms:
            m.Venue(
                tournament = t,
                group = group,
                name = room,
                priority = get_priority(room)
            ).save()

if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser()
    parser.add_option("--verbose", "-v", action="store_true", default=False)
    options, args = parser.parse_args()
    try:
        suffix = args[0]
    except IndexError:
        print("The first argument must be the file suffix.")
        exit(1)

    # Now import all
    main(suffix, options.verbose)
