import csv

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import CommandError

from participants.prefetch import populate_win_counts
from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Prints the teams eligible for a break category, their code names, " \
           "and how many points they're on."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("slug", type=str, nargs='+',
            help="Slug of break category to dump")

    def handle_tournament(self, tournament, **options):
        for slug in options["slug"]:
            try:
                break_category = tournament.breakcategory_set.get(slug=slug)
            except ObjectDoesNotExist:
                raise CommandError("There's no break category with slug '%s'" % slug)

            self.stdout.write("\n==== %s Teams ====" % (break_category.name,))

            teams = break_category.team_set.all()
            populate_win_counts(teams)

            writer = csv.writer(self.stdout)

            for team in sorted(teams, key=lambda x: -x.points_count):
                row = [team.short_name, team.code_name, team.points_count]
                writer.writerow(row)
