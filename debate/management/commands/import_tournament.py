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
            m.Tournament.objects.filter(slug=folder).delete()
            t = m.Tournament(slug=folder)
            t.save()
            self.stdout.write('Created the tournament')

            self.stdout.write('Attempting to create rounds ')
            for i in range(1, 4):
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
            self.stdout.write('Created the rounds')

            # Venues
            self.stdout.write('Attempting to create the venues')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'venues.csv')))
            except:
                self.stdout.write('venues.csv file is missing or damaged')

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

            self.stdout.write('Created the venues')

            # Institutions
            self.stdout.write('Attempting to create the institutions')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'institutions.csv')))
            except:
                self.stdout.write('institutions.csv file is missing or damaged')

            for code, name in reader:
                i = m.Institution(code=code, name=name, tournament=t)
                i.save()
            self.stdout.write('Created the institutions')

            # Judges
            self.stdout.write('Attempting to create the judges')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'institutions.csv')))
            except:
                self.stdout.write('institutions.csv file is missing or damaged')

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

            self.stdout.write('Created the judges')

            # Speakers
            self.stdout.write('Attempting to create the teams/speakers')
            try:
                reader = csv.reader(open(os.path.join(data_path, 'speakers.csv'), 'rU'))
            except:
                self.stdout.write('speakers.csv file is missing or damaged')

            for name, ins_name, team_name in reader:
                try:
                    ins = m.Institution.objects.get(code=ins_name)
                    print ins
                except Exception as inst:
                    self.stdout.write("error with " + ins_name)
                    print type(inst)     # the exception instance
                    print inst           # __str__ allows args to printed directly

                try:
                    team = m.Team.objects.get_or_create(institution = ins, reference = team_name, use_institution_prefix = False)
                except Exception as inst:
                    self.stdout.write("error with " + team_name)
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
                except:
                    self.stdout.write('Couldnt make the speaker ' + name)


            self.stdout.write('Created the speakers')

            self.stdout.write('Successfully import all data')

        except:
            self.stdout.write('Failed')