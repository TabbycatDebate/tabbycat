from utils.management.base import TournamentCommand, CommandError
from ...models import Debate
from tournaments.models import Round

class Command(TournamentCommand):

    help = "Deletes all debates in a round (or rounds)."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument("round", type=str, nargs='+', help="Seq numbers (if integers) or abbreviations "
                "(if not integers) of rounds to reset, multiple rounds can be specified. If a round's "
                "abbreviation is an integer, only its seq number may be used.")
        parser.add_argument("--confirm", type=str, action="append" metavar="ROUND", help="If specified with "
                "the same arguments as the positional arguments and in the same order, the user confirmation "
                "prompt will be skipped. --confirm must be used with each round, e.g., 2 3 --confirm 2 "
                "--confirm 3.")

    def _get_round(self, specifier):
        if specifier.isdigit():
            kwargs = {"seq": int(specifier)}
            type = "seq number"
        else:
            kwargs = {"abbreviation": specifier}
            type = "abbreviation"
        try:
            return Round.objects.get(tournament=tournament, **kwargs)
        except Round.DoesNotExist:
            raise CommandError("The tournament {tournament:r} has no round with {type} {spec}".format(
                    tournament=tournament.slug, type=type, spec=specifier))

    def handle_tournament(self, tournament, **options):

        rounds = [_get_round(spec) for spec in options["round"]]

        if not options["confirm"]:
            self.stdout.write("WARNING! You are about to delete ALL DEBATES from the following rounds:")
            self.stdout.write("   " + ", ".join(r.name for r in rounds))
            response = input("Are you sure? ")
            if response != "yes":
                raise CommandError("Cancelled by user.")

        elif options["confirm"] != options["round"]:
            raise CommandError("The --confirm arguments did not match the positional arguments.")

        for round in rounds:
            self.stdout.write("Deleting all debates in round {} ...".format(round.name))
            Debate.objects.filter(round=round).delete()
            round.draw_status = Round.STATUS_NONE
            round.save()

        self.stdout.write("Done.")