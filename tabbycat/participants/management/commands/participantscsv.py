import csv
from argparse import ArgumentParser

from participants.models import Speaker
from utils.management.base import TournamentCommand


class Command(TournamentCommand):

    help = "Prints a CSV-style list of participants"

    def add_arguments(self, parser):
        subparsers = parser.add_subparsers(dest="subcommand", parser_class=ArgumentParser,
              metavar="{teams,adjs}")
        subparsers.required = True

        teams = subparsers.add_parser("teams")
        teams.add_argument("--full-institution-name", action="store_true", default=False,
            help="Use full institution name (rather than code)")
        super(Command, self).add_arguments(teams)

        speakers = subparsers.add_parser("speakers")
        speakers.add_argument("--full-institution-name", action="store_true", default=False,
            help="Use full institution name (rather than code)")
        super(Command, self).add_arguments(speakers)

        adjs = subparsers.add_parser("adjs")
        adjs.add_argument("--full-institution-name", action="store_true", default=False,
            help="Use full institution name (rather than code)")
        super(Command, self).add_arguments(adjs)

    def handle_tournament(self, tournament, **options):

        def institution_name(inst):
            if not inst:
                return ""
            elif options['full_institution_name']:
                return inst.name
            else:
                return inst.code

        writer = csv.writer(self.stdout)

        if options['subcommand'] == "teams":
            writer.writerow(["institution", "short_name", "code_name", "speakers"])
            for team in tournament.team_set.all():
                row = [institution_name(team.institution), team.short_name, team.code_name]
                for speaker in team.speaker_set.all():
                    row.extend([speaker.name, speaker.email])
                writer.writerow(row)

        elif options['subcommand'] == "speakers":
            writer.writerow(["name", "email", "short_name", "code_name", "institution"])
            for speaker in Speaker.objects.filter(team__tournament=tournament):
                row = [speaker.name, speaker.email, speaker.team.short_name,
                        speaker.team.code_name, institution_name(speaker.team.institution)]
                writer.writerow(row)

        elif options['subcommand'] == "adjs":
            writer.writerow(["name", "email", "institution"])
            for adj in tournament.relevant_adjudicators.all():
                row = [adj.name, adj.email, institution_name(adj.institution)]
                writer.writerow(row)
