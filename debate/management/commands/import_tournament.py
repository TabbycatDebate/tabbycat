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
            # Tournament
            self.stdout.write('Attempting to create tournament ' + folder)
            try:
                m.Tournament.objects.filter(slug=folder).delete()
                t = m.Tournament(slug=folder)
                t.save()
            except Exception as inst:
                print inst

            self.stdout.write('Created the tournament: ' + folder)

            self.stdout.write('Attempting to create rounds ')
            rounds_count = 4
            try:
                for i in range(1, rounds_count):
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
                self.stdout.write('Created ' + str(rounds_count) + ' rounds')
            except Exception as inst:
                print inst

            # Venues
            self.stdout.write('Attempting to create the venues')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'venues.csv')))
            except:
                self.stdout.write('venues.csv file is missing or damaged')

            venue_count = 0
            for room, priority, group in reader:
                try:
                    group = int(group)
                except ValueError:
                    group = None

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

                venue_count = venue_count + 1

            self.stdout.write('Created ' + str(venue_count) + ' venues')

            # Institutions
            self.stdout.write('Attempting to create the institutions')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'institutions.csv')))
            except:
                self.stdout.write('institutions.csv file is missing or damaged')

            institutions_count = 0
            for code, name in reader:
                i = m.Institution(code=code, name=name, tournament=t)
                i.save()
                institutions_count = institutions_count + 1

            self.stdout.write('Created ' + str(institutions_count) + ' institutions')

            # Judges
            self.stdout.write('Attempting to create the judges')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'institutions.csv')))
            except:
                self.stdout.write('institutions.csv file is missing or damaged')

            adjs_count = 0
            reader = csv.reader(open(os.path.join(data_path, 'judges.csv')))
            for ins_name, name, score in reader:
                try:
                    score = int(score)
                except ValueError:
                    score = 0

                # People can either input instutions as name or short name
                try:
                    ins = m.Institution.objects.get(name=ins_name, tournament=t)
                except:
                    ins = m.Institution.objects.get(code=ins_name, tournament=t)

                m.Adjudicator(
                    name = name,
                    institution = ins,
                    score = score
                ).save()

                adjs_count = adjs_count + 1

            self.stdout.write('Created ' + str(adjs_count) + 'judges')

            # Speakers
            self.stdout.write('Attempting to create the teams/speakers')
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
                    team = m.Team.objects.get_or_create(institution = ins, 
                           reference = team_name, 
                           use_institution_prefix = False)
                    teams_count = teams_count + 1
                except Exception as inst:
                    self.stdout.write("error with " + str(team_name))
                    print type(inst)     # the exception instance
                    print inst           # __str__ allows args to printed directly


                # Resetting the variable incase create/get above fails
                speakers_team = m.Team.objects.get(reference=team_name)

                print team

                try:
                    m.Speaker(
                        name = name,
                        team = speakers_team
                    ).save()
                    speakers_count = speakers_count + 1
                except:
                    self.stdout.write('Couldnt make the speaker ' + name)


            self.stdout.write('Created ' + str(speakers_count) + 
                              ' speakers and ' + str(teams_count) + ' teams')

            self.stdout.write('Successfully import all data')

        except:
            self.stdout.write('Failed')