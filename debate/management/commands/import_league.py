from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify
import os
import csv
import debate.models as m

class Command(BaseCommand):
    args = '<folder>'
    help = 'Imports data from a folder in the data directory'

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError("Not enough arguments.")

        # Getting the command line variable
        folder = args[0]
        total_errors = 0

        # Where to find the data
        base_path = os.path.join(settings.PROJECT_PATH, 'data')
        data_path = os.path.join(base_path, folder)
        self.stdout.write('importing from ' + data_path)

        # Where to find the data
        template_path = os.path.join(base_path, "league_template")
        self.stdout.write('using template from ' + data_path)

        try:
            if m.Tournament.objects.filter(slug=slugify(unicode(folder))).exists():
                self.stdout.write("WARNING! A tournament called '" + folder + "' already exists.")
                self.stdout.write("You are about to delete EVERYTHING for this tournament.")
                response = raw_input("Are you sure? ")
                if response != "yes":
                    self.stdout.write("Cancelled.")
                    raise CommandError("Cancelled by user.")
                m.Tournament.objects.filter(slug=slugify(unicode(folder))).delete()

            # Tournament
            self.stdout.write('**** Attempting to create tournament ' + folder)
            try:
                slug = slugify(unicode(folder))
                short_name = (folder[:24] + '..') if len(folder) > 75 else folder
                t = m.Tournament(name=folder, short_name=short_name, slug=slugify(unicode(folder)))
                t.save()
            except Exception as inst:
                total_errors += 1
                print inst

            self.stdout.write('Made tournament: \t' + folder)
            self.stdout.write('**** Attempting to create rounds ')


            # If importing from the CSV
            try:
                reader = csv.reader(open(os.path.join(template_path, 'rounds.csv')))
                reader.next() # Skipping header row
            except:
                self.stdout.write('rounds.csv file is missing or damaged')

            rounds_count = 0
            i = 1
            for line in reader:
                seq = line[0]
                if not seq:
                    seq = i
                name = str(line[1])
                abbv = str(line[2])
                draw_stage = str(line[3]) or "Preliminary"
                draw_type = str(line[4]) or "Random"
                is_silent = int(line[5]) or 0
                feedback_weight = float(line[6]) or 0.7

                if draw_stage.lower() in ("preliminary", "p"):
                    draw_stage = "P"
                elif draw_stage.lower() in ("elimination", "break", "e", "b"):
                    draw_stage = "E"
                else:
                    draw_stage = None

                if draw_type.lower() in ("random", "r"):
                    draw_type = "R"
                elif draw_type.lower() in ("round-robin", "round robin", "d"):
                    draw_type = "D"
                elif draw_type.lower() in ("power-paired", "power paired", "p"):
                    draw_type = "P"
                elif draw_type.lower() in ("first elimination", "first-elimination", "1st elimination", "1", "e"):
                    draw_type = "F"
                elif draw_type.lower() in ("subsequent elimination", "subsequent-elimination", "2nd elimination", "2"):
                    draw_type = "B"
                else:
                    draw_type = None

                if is_silent > 0:
                    is_silent = True
                else:
                    is_silent = False

                try:
                    m.Round(
                        tournament = t,
                        seq = seq,
                        name = name,
                        abbreviation = abbv,
                        draw_type = draw_type,
                        stage = draw_stage,
                        feedback_weight = min((int(seq)-1)*0.1, 0.5),
                        silent = is_silent
                    ).save()
                    rounds_count += 1
                    i += 1
                    print "Made round: \t\t%s" % name
                except Exception as inst:
                    total_errors += 1
                    self.stdout.write('Couldnt make round ' + name)
                    print inst

            t.current_round = m.Round.objects.get(tournament=t, seq=1)
            t.save()
            self.stdout.write('**** Created ' + str(rounds_count) + ' rounds')

            # Config
            try:
                reader = csv.reader(open(os.path.join(template_path, 'config.csv')))
                reader.next() # Skipping header row
            except:
                self.stdout.write('config.csv file is missing or damaged')

            for line in reader:
                key = line[0]
                value_type = line[1]
                if value_type == "str":
                    value = str(line[2])
                elif value_type == "int":
                    value = int(line[2])
                elif value_type == "float":
                    value = float(line[2])
                elif value_type == "bool":
                    if line[2] == "True":
                        value = True
                    elif line[2] == "False":
                        value = False
                    else:
                        print "Error %s not properly set" % key


                t.config.set(key, value)
                print "Made setting \t%s as %s" % (key, value)

            # Venues
            self.stdout.write('**** Attempting to create the venue groups')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'venue_groups.csv')))
                reader.next() # Skipping header row
            except:
                self.stdout.write('venues_groups.csv file is missing or damaged')

            venue_count = 0
            venue_group_count = 0
            for line in reader:
                long_name = line[0] or None
                short_name = line[1] or None
                team_capacity = line[2] or None
                try:
                    venue_group, created = m.VenueGroup.objects.get_or_create(
                       name=long_name,
                       short_name=short_name,
                       team_capacity=team_capacity,
                       tournament=t
                    )

                    if created:
                        print "Made venue group: \t%s" % venue_group
                        venue_group_count = venue_group_count + 1
                    else:
                        print "Matched venue group: \t%s" % venue_group


                except ValueError:
                    total_errors += 1
                    self.stdout.write('Couldnt make venue group ' + group)
                    venue_group = None


            # Venues
            self.stdout.write('**** Attempting to create the venues')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'venues.csv')))
                reader.next() # Skipping header row
            except:
                self.stdout.write('venues.csv file is missing or damaged')

            venue_count = 0
            venue_group_count = 0
            for line in reader:
                round_abbv = line[0]
                group_name = line[1]
                time = line[2]

                try:
                    venue_group = m.VenueGroup.objects.get(name=group_name, tournament=t)
                except:
                    try:
                        venue_group = m.VenueGroup.objects.get(short_name=group_name, tournament=t)
                    except Exception as inst:
                        self.stdout.write('Couldnt find the venue group ' + group_name)
                        total_errors += 1
                        print inst

                venue_rooms = int(float(venue_group.team_capacity) / 2)
                venue_round = m.Round.objects.get(abbreviation=round_abbv, tournament=t)

                for i in range(1, venue_rooms + 1):
                    room_name = "Room %s" % i
                    try:
                        m.Venue(
                            tournament = t,
                            group = venue_group,
                            name = room_name,
                            priority = venue_round.seq,
                            time = time
                        ).save()
                        venue_count = venue_count + 1

                    except Exception as inst:
                        total_errors += 1
                        self.stdout.write('Couldnt make venue ' + room_name)
                        print inst

            # Teams by Institution
            self.stdout.write('**** Attempting to create the teams')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'institutional_teams_and_prefs.csv'), 'rU'))
                reader.next() # Skipping header row
            except:
                self.stdout.write('institutional_teams_and_prefs.csv file is missing or damaged')

            institution_tally = {}
            for line in reader:
                try:
                    ins_name = line[0]
                    teams_count = int(line[1])
                    pref1 = line[2] or None
                    pref2 = line[3] or None
                    pref3 = line[4] or None
                    pref4 = line[5] or None
                    pref5 = line[6] or None
                    pref6 = line[7] or None
                    pref7 = line[8] or None
                    pref8 = line[9] or None
                    pref9 = line[10] or None
                    pref10 = line[11] or None
                    venue_preferences = [pref1,pref2,pref3,pref4,pref5,pref6,pref7,pref8,pref9,pref10]

                    if ins_name not in institution_tally:
                        institution_tally[ins_name] = 0

                    try:
                        ins = m.Institution.objects.get(name=ins_name)
                    except:
                        try:
                            ins = m.Institution.objects.get(code=ins_name)
                        except Exception as inst:
                            self.stdout.write("error with finding inst " + ins_name)
                            total_errors += 1
                            print type(inst)     # the exception instance
                            print inst           # __str__ allows args to printed directly


                    for i in range(1, teams_count + 1):
                        name = str(i + institution_tally[ins_name])
                        short_name = str(i + institution_tally[ins_name])
                        team, created = m.Team.objects.get_or_create(
                            institution = ins,
                            reference = name,
                            short_reference = short_name,
                            tournament=t,
                            use_institution_prefix = True
                        )
                        team.save()

                        m.Speaker(name = "1st Speaker", team = team).save()
                        m.Speaker(name = "2nd Speaker", team = team).save()
                        m.Speaker(name = "3rd Speaker", team = team).save()
                        m.Speaker(name = "Reply Speaker", team = team).save()

                        for index, venue in enumerate(venue_preferences):
                            if venue:
                                try:
                                    venue_group = m.VenueGroup.objects.get(name=venue,tournament=t)
                                except:
                                    try:
                                        venue_group = m.VenueGroup.objects.get(short_name=venue,tournament=t)
                                    except Exception as inst:
                                        self.stdout.write("error with finding venue: " + venue)
                                        total_errors += 1
                                        print type(inst)     # the exception instance
                                        print inst           # __str__ allows args to printed directly

                                preference = m.TeamVenuePreference(
                                    team = team,
                                    venue_group = venue_group,
                                    priority = index
                                )
                                preference.save()

                    institution_tally[ins_name] += teams_count
                    print "Made %s teams for\t%s (total of %s)" % (teams_count, ins, institution_tally[ins_name])

                except Exception as inst:
                    self.stdout.write('Couldnt make the teams for ' + line[0])
                    total_errors += 1
                    print inst

            # Motions
            try:
                reader = csv.reader(open(os.path.join(template_path, 'motions.csv')))
                reader.next() # Skipping header row
            except:
                self.stdout.write('motions.csv file is missing or damaged')

            motions_count = 0
            for line in reader:
                round_abbv = str(line[0])
                motion_seq = int(line[1])
                reference = str(line[2])
                text = str(line[3])

                try:
                    round = m.Round.objects.get(abbreviation=round_abbv, tournament=t)
                    m.Motion(round=round, seq=motion_seq, reference=reference, text=text).save()
                    self.stdout.write('Made motion: \t\t' + round_abbv + ': ' + text )
                    motions_count += 1
                except m.Round.DoesNotExist:
                    total_errors += 1
                    self.stdout.write('Couldnt find round with abbreviation: ' + round_abbv)

            self.stdout.write('**** Created ' + str(motions_count) + ' motions')

        except Exception:
            import traceback
            traceback.print_exc()
            self.stdout.write('Failed')