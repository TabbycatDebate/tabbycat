from django.core.management.base import BaseCommand, CommandError
from tournaments.models import Tournament
from settings import TABBYCAT_APPS
import logging

def _set_log_level(level):
    for app in TABBYCAT_APPS:
        logging.getLogger(app).setLevel(level)

class TournamentCommand(BaseCommand):
    """Implements common functionality for commands specific to a tournament.

    Subclasses should override ``handle_tournament()`` rather than ``handle()``.
    Subclasses that override ``add_arguments()`` must call
        ``TournamentCommand``'s ``add_arguments()``, using
        ``super(Command, self).add_arguments(parser)``.
    If a subclass uses subparsers, the above line should be called once for
        every subparser, passing it in as ``parser``.
    """

    def add_arguments(self, parser):
        parser.add_argument("-t", "--tournament", type=str, action="append", help="Slug of tournament(s), required if there is more than one tournament. "
                "Can be specified multiple times to run the command on multiple tournaments.")

    def handle(self, *args, **options):
        loglevel = [logging.WARNING, logging.INFO, logging.DEBUG, logging.DEBUG][options["verbosity"]]
        _set_log_level(loglevel)

        tournament_option = options.pop("tournament")
        tournaments = list()

        if not tournament_option:
            # if there is only one tournament, that'll do.
            if Tournament.objects.count() == 1:
                tournaments.append(Tournament.objects.get())
        else:
            bad_slugs = list()
            for slug in tournament_option:
                try:
                    tournament = Tournament.objects.get(slug=slug)
                except Tournament.DoesNotExist:
                    bad_slugs.append(slug)
                    continue
                tournaments.append(tournament)

            if bad_slugs:
                raise CommandError("There {verb} no tournament{s} with the following slug{s}: {slugs}".format(
                        verb="is" if len(bad_slugs) == 1 else "are",
                        s="" if len(bad_slugs) == 1 else "s",
                        slugs=", ".join(bad_slugs)))

        for tournament in tournaments:
            self.handle_tournament(tournament, **options)

    def handle_tournament(self, tournament, **options):
        """Perform the command's actions on ``tournament``, a ``Tournament``
        instance corresponding to the slug on the command line."""
        raise NotImplementedError("subclasses of TournamentCommand must provide a handle_tournament() method.")
