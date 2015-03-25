from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify
import os
import csv
import debate.models as m
from debate.emoji import EMOJI_LIST
import random

class Command(BaseCommand):
    args = '<folder> <num_rounds> <share_data>'
    help = 'Imports data from a folder in the data directory'

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError("Not enough arguments.")

        # Getting the command line variable
        folder = args[0]
        try:
            rounds_to_auto_make = int(args[1])
        except:
            rounds_to_auto_make = 0

        total_errors = 0

        # Where to find the data
        base_path = os.path.join(settings.PROJECT_PATH, 'data')
        data_path = os.path.join(base_path, folder)
        if not os.path.isdir(data_path):
            # If it isn't in the standard data folder try the datasets module
            data_path = os.path.join(base_path, 'tabbycat_datasets', folder)

        if not os.path.isdir(data_path):
            self.stdout.write('Couldn\'t find the specified folder:' + data_path)
        else:
            self.stdout.write('importing from ' + data_path)

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
                rounds_count = 0

                if rounds_to_auto_make > 0:
                    # If using the CLI arg
                    try:
                        for i in range(1, rounds_to_auto_make + 1):
                            if i == 1:
                                draw_type = m.Round.DRAW_RANDOM
                            else:
                                draw_type = m.Round.DRAW_POWERPAIRED

                            m.Round(
                                tournament = t,
                                seq = i,
                                name = 'Round %d' % i,
                                abbreviation = 'R%d' % i,
                                draw_type = draw_type,
                                feedback_weight = min((i-1)*0.1, 0.5),
                                silent = (i >= rounds_to_auto_make),
                            ).save()
                            print "Auto-made round: \tRound %s" % i
                            rounds_count += 1

                    except Exception as inst:
                        total_errors += 1
                        print inst
                else:
                    # If importing from the CSV
                    try:
                        reader = csv.reader(open(os.path.join(data_path, 'rounds.csv')))
                        reader.next() # Skipping header row
                    except Exception as e:
                        print e
                        self.stdout.write('rounds.csv file is missing or damaged - ensure saved as plain CSV (or MS-DOS CSV)')

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
                    reader = csv.reader(open(os.path.join(data_path, 'config.csv')))
                    reader.next() # Skipping header row
                except Exception as e:
                    print e
                    self.stdout.write('config.csv file is missing or damaged - ensure saved as plain CSV (or MS-DOS CSV)')
                    reader = None

                if reader:
                    config_count = 0
                    for line in reader:
                        key = line[0]
                        value_type = line[1]
                        if str(line[2]) == '':
                            value = None
                        elif value_type == "string" or value_type == "str" :
                            value = str(line[2])
                        elif value_type == "int":
                            value = int(line[2])
                        elif value_type == "float":
                            try:
                                value = float(line[2])
                            except:
                                value = float(int(line[2]))
                        elif value_type == "bool" or value_type == "_bool":
                            if line[2] == "True" or line[2] == "1":
                                value = True
                            elif line[2] == "False" or line[2] == "0":
                                value = False
                            else:
                                print "Error %s not properly set" % key

                        if value is not None:
                            t.config.set(key, value)
                            config_count += 1
                            print "Made setting \t%s as %s" % (key, value)


                    self.stdout.write('**** Created ' + str(config_count) + ' settings')

                # Venues
                self.stdout.write('**** Attempting to create the venue groups')
                try:
                    reader = csv.reader(open(os.path.join(data_path, 'venue_groups.csv')))
                    reader.next() # Skipping header row
                except Exception as e:
                    print e
                    self.stdout.write('venues_groups.csv file is missing or damaged - ensure saved as plain CSV (or MS-DOS CSV)')
                    reader = None

                if reader:
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
                except Exception as e:
                    print e
                    self.stdout.write('venues.csv file is missing or damaged - ensure saved as plain CSV (or MS-DOS CSV)')
                    reader = None

                if reader:
                    venue_count = 0
                    venue_group_count = 0
                    for line in reader:
                        room_name = line[0]
                        priority = len(line) > 1 and line[1] or 10
                        group_name = len(line) > 2 and line[2] or None
                        time = len(line) > 3 and str(line[3]) or None

                        if group_name:
                            try:
                                venue_group, created = m.VenueGroup.objects.get_or_create(
                                    name=group_name
                                )

                                if created:
                                    print "Made venue group: \t%s" % group_name
                                    venue_group_count = venue_group_count + 1

                            except ValueError:
                                total_errors += 1
                                self.stdout.write('Couldnt make venue group ' + group_name)
                                venue_group = None
                        else:
                            venue_group = None

                        try:
                            m.Venue(
                                tournament = t,
                                group = venue_group,
                                name = room_name,
                                priority = priority,
                                time = time
                            ).save()
                            #print "Made venue: \t\t%s" % room_name

                            venue_count = venue_count + 1

                        except Exception as inst:
                            total_errors += 1
                            self.stdout.write('Couldnt make venue ' + room_name)
                            print inst


                self.stdout.write('**** Created ' + str(venue_group_count) + ' venue groups')
                self.stdout.write('**** Created ' + str(venue_count) + ' venues')

                # Institutions
                self.stdout.write('**** Attempting to create the institutions')
                try:
                    reader = csv.reader(open(os.path.join(data_path, 'institutions.csv')))
                    reader.next() # Skipping header row
                except Exception as e:
                    print e
                    self.stdout.write('institutions.csv file is missing or damaged - ensure saved as plain CSV (or MS-DOS CSV)')

                institutions_count = 0
                for line in reader:
                    name = str(line[0])
                    code = str(line[1])
                    abbv = len(line) > 2 and line[2] or ""

                    try:
                        inst, created = m.Institution.objects.get_or_create(
                            code=code,
                            name=name
                        )
                        if created:
                            print "Made institution: \t%s" % name
                        else:
                            print "Matched institution: \t%s" % name

                        institutions_count = institutions_count + 1
                    except Exception as inst:
                        total_errors += 1
                        self.stdout.write('Couldnt make institution ' + name)
                        print inst

                self.stdout.write('**** Created ' + str(institutions_count) + ' institutions')

                # Teams
                self.stdout.write('**** Attempting to create the teams')
                try:
                    reader = csv.reader(open(os.path.join(data_path, 'teams.csv'), 'rU'))
                    reader.next() # Skipping header row
                except Exception as e:
                    print e
                    self.stdout.write('teams.csv file is missing or damaged - ensure saved as plain CSV (or MS-DOS CSV)')

                # Getting a list of all assigned emoji
                assigned_emoji_teams = m.Team.objects.filter(emoji_seq__isnull=False).values_list('emoji_seq', flat=True)
                unassigned_emoji_teams = m.Team.objects.filter(emoji_seq__isnull=True).values_list('id', flat=True)

                # The list of possible emoji, then culled to prevent duplicates
                emoji_options = range(0, len(EMOJI_LIST) - 1)

                def get_emoji(emoji_options):
                    try:
                        emoji_id = random.choice(emoji_options)
                        emoji_options.remove(emoji_id)
                    except:
                        emoji_id = random.randint(0, len(EMOJI_LIST) - 1)
                    return emoji_id

                for index in assigned_emoji_teams:
                    if index in emoji_options:
                        emoji_options.remove(index)

                for index in unassigned_emoji_teams:
                    if index in emoji_options:
                        emoji_options.remove(index)


                teams_count = 0
                for line in reader:
                    try:
                        name = line[0]
                        ins = line[1]
                        short_name = name[:34]
                        emoji_id = get_emoji(emoji_options)
                        try:
                            ins = m.Institution.objects.get(name=ins)
                        except:
                            try:
                                ins = m.Institution.objects.get(code=ins)
                            except Exception as inst:
                                self.stdout.write("error with finding inst " + ins)
                                total_errors += 1
                                print type(inst)     # the exception instance
                                print inst           # __str__ allows args to printed directly

                        team, created = m.Team.objects.get_or_create(
                            institution = ins,
                            reference = name,
                            short_reference = short_name,
                            tournament=t,
                            emoji_seq=emoji_id
                        )
                        team.save()

                        m.Speaker(name = "1st Speaker", team = team).save()
                        m.Speaker(name = "2nd Speaker", team = team).save()
                        m.Speaker(name = "3rd Speaker", team = team).save()
                        m.Speaker(name = "Reply Speaker", team = team).save()
                        teams_count = teams_count + 1
                        print "Made team:\t\t%s  %s of %s" % (EMOJI_LIST[emoji_id], name, ins)
                    except Exception as inst:
                        self.stdout.write('Couldnt make the team ' + line[0] + ' of ' + line[1])
                        total_errors += 1
                        print inst

                # Speakers
                self.stdout.write('**** Attempting to create the teams/speakers')
                try:
                    reader = csv.reader(open(os.path.join(data_path, 'speakers.csv'), 'rU'))
                    reader.next() # Skipping header row
                except Exception as e:
                    print e
                    self.stdout.write('speakers.csv file is missing or damaged - ensure saved as plain CSV (or MS-DOS CSV)')

                speakers_count = 0
                teams_count = 0
                for line in reader:
                    name = line[0]
                    ins_name = line[1]
                    team_name = line[2]
                    try:
                        prefix = int(line[3]) or 0
                    except:
                        prefix = False
                    try:
                        gender = str(line[4]) or None
                        if gender != "M" and gender != "F" and gender != "O":
                            gender = None
                    except:
                        gender = None
                    try:
                        novice_status = int(line[5]) or 0
                    except:
                        novice_status = 0

                    try:
                        ins = m.Institution.objects.get(code=ins_name)
                    except:
                        try:
                            ins = m.Institution.objects.get(name=ins_name)
                        except Exception as inst:
                            self.stdout.write("error with " + ins_name)
                            total_errors += 1
                            print type(inst)     # the exception instance
                            print inst           # __str__ allows args to printed directly

                    try:
                        team, created = m.Team.objects.get_or_create(
                            institution = ins,
                            reference = team_name,
                            use_institution_prefix = prefix,
                            tournament=t
                        )
                        if created:
                            team.emoji_seq = get_emoji(emoji_options)
                            team.save()
                            teams_count = teams_count + 1
                            print "Made team:\t\t%s  %s of %s" % (EMOJI_LIST[team.emoji_seq], name, ins)

                    except Exception as inst:
                        total_errors += 1
                        self.stdout.write("error with " + str(team_name))
                        print type(inst)     # the exception instance
                        print inst           # __str__ allows args to printed directly


                    # Resetting the variable incase create/get above fails
                    speakers_team = m.Team.objects.get(institution=ins, reference=team_name, tournament=t)

                    name = name.strip()
                    try:
                        m.Speaker(
                            name = name,
                            team = speakers_team,
                            gender = gender,
                            novice = novice_status
                        ).save()
                        speakers_count = speakers_count + 1
                    except Exception as inst:
                        self.stdout.write('Couldnt make the speaker ' + name)
                        total_errors += 1
                        print inst

                    print "Made speaker:\t\t%s  %s (%s) of %s" % (EMOJI_LIST[speakers_team.emoji_seq], name, gender, ins)

                self.stdout.write('**** Created ' + str(speakers_count) +
                                  ' speakers and ' + str(teams_count) + ' teams')

                # Judges
                self.stdout.write('**** Attempting to create the judges')
                try:
                    reader = csv.reader(open(os.path.join(data_path, 'judges.csv')))
                    reader.next() # Skipping header row
                except Exception as e:
                    print e
                    self.stdout.write('judges.csv file is missing or damaged - ensure saved as plain CSV (or MS-DOS CSV)')

                adjs_count = 0
                for line in reader:
                    name, ins_name, test_score = line[0:3]
                    try:
                        gender = str(line[3]) or None
                        if gender != "M" and gender != "F" and gender != "O":
                            gender = None
                    except:
                        gender = None
                    try:
                        novice_status = int(line[4]) or 0
                    except:
                        novice_status = 0
                    phone = len(line) > 4 and line[5] or None
                    email = len(line) > 5 and line[6] or None
                    notes = len(line) > 6 and line[7] or None
                    institution_conflicts = len(line) > 8 and line[8] or None
                    team_conflicts = len(line) > 9 and line[9] or None

                    try:
                        test_score = float(test_score)
                    except ValueError:
                        self.stdout.write('Could not interpret adj score for {0}: {1}'.format(name, test_score))
                        test_score = 0
                        total_errors += 1

                    try:
                        phone = str(phone)
                    except ValueError:
                        self.stdout.write('Could not interpret adj phone for {0}: {1}'.format(name, phone))
                        phone = None
                        total_errors += 1

                    try:
                        email = str(email)
                    except ValueError:
                        self.stdout.write('Could not interpret adj email for {0}: {1}'.format(name, email))
                        email = None
                        total_errors += 1

                    try:
                        notes = str(notes)
                    except ValueError:
                        self.stdout.write('Could not interpret adj note for {0}: {1}'.format(name, notes))
                        notes = None
                        total_errors += 1

                    # People can either input instutions as name or short name
                    ins_name = ins_name.strip()
                    try:
                        ins = m.Institution.objects.get(name=ins_name)
                    except m.Institution.DoesNotExist:
                        try:
                            ins = m.Institution.objects.get(code=ins_name)
                        except:
                            self.stdout.write('Could not find the institution of {0} for {1}'.format(ins_name, name))


                    name = name.strip()

                    adj = m.Adjudicator(
                        name = name,
                        institution = ins,
                        test_score = test_score,
                        gender = gender,
                        novice = novice_status,
                        phone = phone,
                        email = email,
                        notes = notes,
                        tournament = t
                    )
                    adj.save()
                    print "Made adjudicator: \t%s (%s) of %s" % (name, gender, ins)

                    m.AdjudicatorTestScoreHistory(adjudicator=adj, score=test_score, round=None).save()
                    m.AdjudicatorInstitutionConflict(adjudicator=adj, institution=ins).save()

                    if institution_conflicts:
                        for ins_conflict_name in institution_conflicts.split(","):
                            ins_conflict_name = ins_conflict_name.strip()
                            try:
                                ins_conflict = m.Institution.objects.get(name=ins_conflict_name)
                            except m.Institution.DoesNotExist:
                                print ins_conflict_name
                                ins_conflict = m.Institution.objects.get(code=ins_conflict_name)
                            m.AdjudicatorInstitutionConflict(adjudicator=adj, institution=ins_conflict).save()
                            print "    conflicts with", ins_conflict.name

                    if team_conflicts:
                        for team_conflict_name in team_conflicts.split(","):
                            team_conflict_ins_name, team_conflict_ref = team_conflict_name.rsplit(None, 1)
                            team_conflict_ins_name = team_conflict_ins_name.strip()
                            try:
                                team_conflict_ins = m.Institution.objects.get(name=team_conflict_ins_name)
                            except m.Institution.DoesNotExist:
                                team_conflict_ins = m.Institution.objects.get(code=team_conflict_ins_name)
                            try:
                                team_conflict = m.Team.objects.get(institution=team_conflict_ins, reference=team_conflict_ref)
                            except m.Team.DoesNotExist:
                                self.stdout.write('No team exists to conflict with {0}: {1}'.format(name, team_conflict_name))
                                total_errors += 1
                            m.AdjudicatorConflict(adjudicator=adj, team=team_conflict).save()
                            print "    conflicts with", team_conflict.short_name

                    adjs_count = adjs_count + 1

                self.stdout.write('**** Created ' + str(adjs_count) + ' judges')

                # Motions
                try:
                    reader = csv.reader(open(os.path.join(data_path, 'motions.csv')))
                    reader.next() # Skipping header row
                except Exception as e:
                    print e
                    self.stdout.write('motions.csv file is missing or damaged - ensure saved as plain CSV (or MS-DOS CSV)')

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

                # Sides
                if os.path.isfile(os.path.join(data_path, 'sides.csv')):
                    sides_count = 0
                    reader = csv.reader(open(os.path.join(data_path, 'sides.csv')))
                    reader.next() # Skipping header row
                    for line in reader:
                        ins_name = line[0]
                        team_name = line[1]
                        ins_name = ins_name.strip()
                        try:
                            ins = m.Institution.objects.get(name=ins_name)
                        except m.Institution.DoesNotExist:
                            ins = m.Institution.objects.get(code=ins_name)
                        team = m.Team.objects.get(institution=ins, reference=team_name, tournament=t)
                        for seq, side in enumerate(line[2:], start=1):
                            round = m.Round.objects.get(seq=seq)
                            if side.lower() in ["a", "aff"]:
                                pos = m.TeamPositionAllocation.POSITION_AFFIRMATIVE
                            elif side.lower() in ["n", "neg"]:
                                pos = m.TeamPositionAllocation.POSITION_NEGATIVE
                            else:
                                self.stdout.write("Skipping round {0} allocation for team {1}, invalid side: {2}".format(seq, team.short_name, side))
                            m.TeamPositionAllocation(round=round, team=team, position=pos).save()
                            sides_count += 1
                        self.stdout.write(team.short_name)

                    self.stdout.write('**** Created ' + str(sides_count) + ' side allocations')

                if total_errors == 0:
                    self.stdout.write('**** Successfully imported all data')
                else:
                    self.stdout.write('**** Successfully all data but with %d ERRORS' % total_errors)


            except Exception:
                import traceback
                traceback.print_exc()
                self.stdout.write('Failed')