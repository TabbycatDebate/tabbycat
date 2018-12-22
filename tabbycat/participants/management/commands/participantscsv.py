from argparse import ArgumentParser

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

        adjs = subparsers.add_parser("adjs")
        adjs.add_argument("--full-institution-name", action="store_true", default=False,
            help="Use full institution name (rather than code)")
        super(Command, self).add_arguments(adjs)

    def handle_tournament(self, tournament, **options):

        if options['subcommand'] == "teams":
            self.stdout.write("institution,short_name,code_name,speakers")
            for team in tournament.team_set.all():
                self.stdout.write(",".join([
                    (team.institution.name if options['full_institution_name'] else team.institution.code)
                    if team.institution else "",
                    team.short_name,
                    team.code_name,
                ] + [
                    x for speaker in team.speaker_set.all()
                    for x in (speaker.name, speaker.email)
                ]))

        elif options['subcommand'] == "adjs":
            self.stdout.write("institution,name")
            for adj in tournament.relevant_adjudicators.all():
                self.stdout.write(",".join([
                    (adj.institution.name if options['full_institution_name'] else adj.institution.code)
                    if adj.institution else "",
                    adj.name,
                    adj.email,
                ]))
