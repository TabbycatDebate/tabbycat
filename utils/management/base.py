from django.core.management.base import BaseCommand
from tournaments.models import Tournament

class TournamentCommand(BaseCommand):
    """Implements common functionality for commands specific to a tournament.

    Subclasses should override ``handle_tournament()`` rather than ``handle()``.
    Subclasses that override ``add_arguments()`` must call
        ``TournamentCommand``'s ``add_arguments()``, using
        ``super(Command, self).add_arguments(parser)``.
    """

    def add_arguments(self, parser):
        parser.add_argument("-t", "--tournament", type=str, action="append", help="Slug of tournament(s), required if there is more than one tournament. "
                "Can be specified multiple times to run the command on multiple tournaments.")

    def handle(self, *args, **options):
        tournaments = list()

        if not self.options["tournament"]:
            # if there is only one tournament, that'll do.
            if Tournament.objects.count() == 1:
                tournaments.append(Tournament.objects.get())
        else:
            bad_slugs = list()
            for slug in self.options["tournament"]:
                try:
                    tournament = Tournament.objects.get(slug=slug)
                except Tournament.DoesNotExist:
                    bad_slugs.append(slug)
                    continue
                tournaments.append(tournament)

            if bad_slugs:
                raise CommandError("There {verb} no tournament with the following slug{s}: {slugs}".format(
                        verb="is" if len(bad_slugs) == 1 else "are",
                        s="" if len(bad_slugs) == 1 else "s",
                        slugs=", ".join(bad_slugs)))

        for tournament in tournaments:
            self.handle_tournament(tournament, **options)

    def handle_tournament(self, tournament, **options):
        """Perform the command's actions on ``tournament``, a ``Tournament``
        instance corresponding to the slug on the command line."""
        raise NotImplementedError("subclasses of TournamentCommand must provide a handle_tournament() method.")
