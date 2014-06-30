from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import os
import csv
import debate.models as m

class Command(BaseCommand):
    args = '<folder>'
    help = 'Imports data from a folder in the data directory'

    def handle(self, *args, **options):
        # Getting the command line variable
        folder = args[0]

        # Where to find the data
        base_path = os.path.join(settings.PROJECT_PATH, 'data')
        data_path = os.path.join(base_path, folder)
        self.stdout.write('importing from ' + data_path)

        try:
            if m.Tournament.objects.filter(slug=folder).exists():
                self.stdout.write("WARNING! A tournament called '" + folder + "' already exists.")
                self.stdout.write("You are about to delete EVERYTHING for this tournament.")
                response = raw_input("Are you sure? ")
                if response != "yes":
                    self.stdout.write("Cancelled.")
                    raise CommandError("Cancelled by user.")
                m.Tournament.objects.filter(slug=folder).delete()

            # Tournament
            self.stdout.write('*** Attempting to create tournament ' + folder)
            try:
                t = m.Tournament(slug=folder)
                t.save()
            except Exception as inst:
                print inst

            self.stdout.write('*** Created the tournament: ' + folder)

            self.stdout.write('*** Attempting to create rounds ')
            # TODO get this to use rounds.csv
            rounds_count = 8
            try:
                for i in range(1, rounds_count+1):
                    if i == 1:
                        draw_type = m.Round.DRAW_RANDOM
                    else:
                        draw_type = m.Round.DRAW_POWERPAIRED

                    m.Round(
                        tournament = t,
                        seq = i,
                        name = 'Round %d' % i,
                        draw_type = draw_type,
                        feedback_weight = 0,# min((i-1)*0.1, 0.5),
                        silent = (i > 7),
                    ).save()

                t.current_round = m.Round.objects.get(tournament=t, seq=1)
                t.save()
                self.stdout.write('*** Created ' + str(rounds_count) + ' rounds')
            except Exception as inst:
                print inst

            # Venues
            self.stdout.write('*** Attempting to create the venues')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'venues.csv')))
            except:
                self.stdout.write('venues.csv file is missing or damaged')

            venue_count = 0
            for line in reader:
                if len(line) == 3:
                    room, priority, group = line
                    try:
                        group = int(group)
                    except ValueError:
                        group = None
                elif len(line) == 2:
                    room, priority = line
                    group = None
                else:
                    continue

                try:
                    priority = int(priority)
                except ValueError:
                    priority = None

                m.Venue(
                    tournament = t,
                    group = group,
                    name = room,
                    priority = priority
                ).save()
                print room

                venue_count = venue_count + 1

            self.stdout.write('*** Created ' + str(venue_count) + ' venues')

            # Institutions
            self.stdout.write('*** Attempting to create the institutions')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'institutions.csv')))
            except:
                self.stdout.write('institutions.csv file is missing or damaged')

            institutions_count = 0
            for line in reader:
                if len(line) == 3:
                    abbreviation, code, name = line
                elif len(line) == 2:
                    abbreviation = None
                    code, name = line
                else:
                    continue
                i = m.Institution(code=code, name=name, tournament=t)
                i.save()
                institutions_count = institutions_count + 1
                print name

            self.stdout.write('*** Created ' + str(institutions_count) + ' institutions')

            # Speakers
            self.stdout.write('*** Attempting to create the teams/speakers')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'speakers.csv'), 'rU'))
            except:
                self.stdout.write('speakers.csv file is missing or damaged')

            speakers_count = 0
            teams_count = 0
            for name, ins_name, team_name in reader:
                try:
                    ins = m.Institution.objects.get(code=ins_name)
                    print ins
                except:
                    try:
                        ins = m.Institution.objects.get(name=ins_name)
                    except Exception as inst:
                        self.stdout.write("error with " + ins_name)
                        print type(inst)     # the exception instance
                        print inst           # __str__ allows args to printed directly

                try:
                    team, created = m.Team.objects.get_or_create(institution = ins,
                           reference = team_name,
                           use_institution_prefix = True)
                    if created:
                        teams_count = teams_count + 1
                except Exception as inst:
                    self.stdout.write("error with " + str(team_name))
                    print type(inst)     # the exception instance
                    print inst           # __str__ allows args to printed directly


                # Resetting the variable incase create/get above fails
                speakers_team = m.Team.objects.get(institution=ins, reference=team_name)

                name = name.strip()
                try:
                    m.Speaker(
                        name = name,
                        team = speakers_team
                    ).save()
                    speakers_count = speakers_count + 1
                except:
                    self.stdout.write('Couldnt make the speaker ' + name)

                print team, "-", name

            self.stdout.write('*** Created ' + str(speakers_count) +
                              ' speakers and ' + str(teams_count) + ' teams')

            # Judges
            self.stdout.write('*** Attempting to create the judges')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'institutions.csv')))
            except:
                self.stdout.write('institutions.csv file is missing or damaged')

            adjs_count = 0
            reader = csv.reader(open(os.path.join(data_path, 'judges.csv')))
            for line in reader:
                ins_name, name, test_score, phone, email = line[0:5]
                if len(line) > 5:
                    institution_conflicts = line[5]
                else:
                    institution_conflicts = None
                if len(line) > 6:
                    team_conflicts = line[6]
                else:
                    team_conflicts = None

                try:
                    test_score = float(test_score)
                except ValueError:
                    self.stdout.write('Could not interpret adj score for {0}: {1}'.format(name, test_score))
                    test_score = 0

                try:
                    phone = str(phone)
                except ValueError:
                    self.stdout.write('Could not interpret adj phone for {0}: {1}'.format(name, phone))
                    phone = None

                try:
                    email = str(email)
                except ValueError:
                    self.stdout.write('Could not interpret adj email for {0}: {1}'.format(name, email))
                    email = None

                # People can either input instutions as name or short name
                ins_name = ins_name.strip()
                try:
                    ins = m.Institution.objects.get(name=ins_name, tournament=t)
                except m.Institution.DoesNotExist:
                    ins = m.Institution.objects.get(code=ins_name, tournament=t)

                name = name.strip()
                adj = m.Adjudicator(
                    name = name,
                    institution = ins,
                    test_score = test_score,
                    phone = phone,
                    email = email
                )
                adj.save()
                print "Adjudicator", name

                m.AdjudicatorTestScoreHistory(adjudicator=adj, score=test_score, round=None).save()

                m.AdjudicatorInstitutionConflict(adjudicator=adj, institution=ins).save()

                if institution_conflicts:
                    for ins_conflict_name in institution_conflicts.split(","):
                        ins_conflict_name = ins_conflict_name.strip()
                        try:
                            ins_conflict = m.Institution.objects.get(name=ins_conflict_name, tournament=t)
                        except m.Institution.DoesNotExist:
                            print ins_conflict_name
                            ins_conflict = m.Institution.objects.get(code=ins_conflict_name, tournament=t)
                        m.AdjudicatorInstitutionConflict(adjudicator=adj, institution=ins_conflict).save()
                        print "    conflicts with", ins_conflict.name

                if team_conflicts:
                    for team_conflict_name in team_conflicts.split(","):
                        team_conflict_ins_name, team_conflict_ref = team_conflict_name.rsplit(None, 1)
                        team_conflict_ins_name = team_conflict_ins_name.strip()
                        try:
                            team_conflict_ins = m.Institution.objects.get(name=team_conflict_ins_name, tournament=t)
                        except m.Institution.DoesNotExist:
                            team_conflict_ins = m.Institution.objects.get(code=team_conflict_ins_name, tournament=t)
                        try:
                            team_conflict = m.Team.objects.get(institution=team_conflict_ins, reference=team_conflict_ref)
                        except m.Team.DoesNotExist:
                            self.stdout.write('No team exists to conflict with {0}: {1}'.format(name, team_conflict_name))
                        m.AdjudicatorConflict(adjudicator=adj, team=team_conflict).save()
                        print "    conflicts with", team_conflict.short_name

                adjs_count = adjs_count + 1

            self.stdout.write('*** Created ' + str(adjs_count) + ' judges')

            self.stdout.write('*** Successfully import all data')

        except Exception:
            import traceback
            traceback.print_exc()
            self.stdout.write('Failed')