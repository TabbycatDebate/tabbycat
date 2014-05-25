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
            self.stdout.write('Creating a new tournament called ' + folder)
            m.Tournament.objects.filter(slug=folder).delete()
            t = m.Tournament(slug=folder)
            t.save()
            self.stdout.write('Can create tournament')

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
            self.stdout.write('Can create rounds')

            reader = csv.reader(open(os.path.join(data_path, 'venues.csv')))
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

            self.stdout.write('Can create venues')

            reader = csv.reader(open(os.path.join(data_path, 'institutions.csv')))
            for code, name in reader:
                i = m.Institution(code=code, name=name, tournament=t)
                i.save()
            self.stdout.write('Can create institutions')

            reader = csv.reader(open(os.path.join(data_path, 'judges.csv')))
            for ins_name, name, score in reader:
                ins = m.Institution.objects.get(name=ins_name, tournament=t)
                m.Adjudicator(
                    name = name,
                    institution = ins,
                    score = score
                ).save()
            self.stdout.write('Can create judges')

            reader = csv.reader(open(os.path.join(data_path, 'speakers.csv')))
            for _, ins_name, team_name, name, in reader:
                print ins_name
                ins = m.Institution.objects.get(name=ins_name, tournament=t)
                team, _ = m.Team.objects.get_or_create(
                    institution = ins,
                    name = team_name
                )
                m.Speaker(
                    name = name,
                    team = team
                ).save()

            self.stdout.write('Can create speakers')

            self.stdout.write('Successfully import all data')

        except:
            self.stdout.write('Failed')