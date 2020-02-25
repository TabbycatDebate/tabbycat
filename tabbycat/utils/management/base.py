import logging

from django.core.management.base import BaseCommand, CommandError

from settings import TABBYCAT_APPS
from tournaments.models import Round, Tournament


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
        tournaments_group = parser.add_argument_group("tournament selection")
        tournaments_group.add_argument(
            "-t",
            "--tournament",
            type=str,
            action="append",
            dest="tournament_selection",
            metavar="TOURNAMENT",
            help="Slug of tournament(s), required if there is more than one tournament. "
            "Can be specified multiple times to run the command on multiple tournaments.")
        tournaments_group.add_argument(
            "--all-tournaments",
            action="store_true",
            help="Run on all tournaments in the database. "
            "--tournament options are ignored if this is used.")

    def _set_log_level(self, **options):
        loglevel = [logging.WARNING, logging.INFO, logging.DEBUG, logging.DEBUG,
                    ][options["verbosity"]]
        _set_log_level(loglevel)

    def get_tournaments(self, options):
        """Returns a list of tournaments implied by command-line arguments.
        Implementation note: For caching purposes, this stores the result in
        the "__tournaments__" key of the options dict."""

        if "__tournaments__" in options:
            pass

        elif options["all_tournaments"]:
            if options["tournament_selection"]:
                raise CommandError(
                    "You can't use --tournament and --all-tournaments together.")
            options["__tournaments__"] = list(Tournament.objects.all())

        elif not options["tournament_selection"]:
            # If there is only one tournament, that'll do.
            if Tournament.objects.count() > 1:
                raise CommandError(
                    "You must specify a tournament, because there is more than one tournament in the database.")
            options["__tournaments__"] = [Tournament.objects.get()]

        else:
            tournaments = list()
            bad_slugs = list()
            for slug in options["tournament_selection"]:
                try:
                    tournament = Tournament.objects.get(slug=slug)
                except Tournament.DoesNotExist:
                    bad_slugs.append(slug)
                    continue
                tournaments.append(tournament)

            if bad_slugs:
                raise CommandError(
                    "There {verb} no tournament{s} with the following slug{s}: {slugs}".format(
                        verb="is" if len(bad_slugs) == 1 else "are",
                        s="" if len(bad_slugs) == 1 else "s",
                        slugs=", ".join(bad_slugs)))

            options["__tournaments__"] = tournaments

        return options["__tournaments__"]

    def handle(self, *args, **options):
        self._set_log_level(**options)
        for tournament in self.get_tournaments(options):
            self.handle_tournament(tournament, **options)

    def handle_tournament(self, tournament, **options):
        """Perform the command's actions on ``tournament``, a ``Tournament``
        instance corresponding to the slug on the command line."""
        raise NotImplementedError(
            "subclasses of TournamentCommand must provide a handle_tournament() method.")


class RoundCommand(TournamentCommand):
    """Implements common functionality for commands that relate to rounds.

    If multiple tournaments are specified in command-line options, the rounds
    specified in command-line options must all exist in every such tournament.
    If any one round does not exist, the command will not run.

    Subclasses should override ``handle_round()`` rather than ``handle()``
    or ``handle_tournament()``.
    Subclasses that override ``add_arguments()`` must call
        ``RoundCommand``'s ``add_arguments()``, using
        ``super(Command, self).add_arguments(parser)``.
    If a subclass uses subparsers, the above line should be called once for
        every subparser, passing it in as ``parser``.

    If a subclass sets confirm_round_destruction to a nonempty string, then the
    aggregate round selection options will not be permitted, and the command
    will prompt the user with a list of rounds unless the --confirm option is
    used.
    """

    confirm_round_destruction = None
    rounds_required = True

    def add_arguments(self, parser):
        super(RoundCommand, self).add_arguments(parser)

        group_description = "Options to select rounds on which to run command."
        if not self.confirm_round_destruction:
            group_description += (" Every option adds the associated round(s); "
            "duplicates are not filtered out. So, for example, "
            "'--all-rounds 2' will run on round 2 twice.")

        rounds_group = parser.add_argument_group("round selection", group_description)
        rounds_group.add_argument(
            "round_selection",
            type=str,
            nargs='+' if self.rounds_required else '*',
            metavar="round",
            help="Seq numbers (if integers) or abbreviations (if not integers) "
            "of rounds. Multiple rounds can be specified. If a round's "
            "abbreviation is an integer, only its seq number may be used. If "
            "multiple tournaments are specified, the rounds must exist in "
            "every tournament.")

        if self.confirm_round_destruction:
            rounds_group.add_argument(
                "--confirm",
                type=str,
                nargs='+',
                metavar="ROUND",
                help="If specified with the same arguments as the positional "
                "arguments and in the same order, the user confirmation prompt "
                "will be skipped.")
        else:
            rounds_group.add_argument(
                "--all-rounds",
                action="store_true",
                help="Run on all rounds in each specified tournament.")
            rounds_group.add_argument(
                "--prelim-rounds",
                action="store_true",
                help="Run on all prelim rounds in each specified tournament.")
            rounds_group.add_argument(
                "--break-rounds",
                action="store_true",
                help="Run on all break rounds in each specified tournament.")

    def _get_round(self, tournament, specifier):
        if specifier.isdigit():
            spectype = "seq"
            specifier = int(specifier)
        else:
            spectype = "abbreviation"
        try:
            return tournament.round_set.get(**{spectype: specifier})
        except Round.DoesNotExist:
            raise CommandError("The tournament {tournament!r} has no round with {type} {spec!r}".format(
                tournament=tournament.slug, type=spectype, spec=specifier))

    def get_rounds(self, options):
        """Returns a list of rounds implied by command-line arguments.
        Implementation note: For caching purposes, this stores the result in
        the "__rounds__" key of the options dict."""

        if "__rounds__" in options:
            return options["__rounds__"]

        rounds = list()
        for tournament in self.get_tournaments(options):
            rounds.extend(self._get_round(tournament, spec) for spec in options["round_selection"])
            if options.get("all_rounds", False):
                rounds.extend(tournament.round_set.all())
            if options.get("prelim_rounds", False):
                rounds.extend(tournament.prelim_rounds().all())
            if options.get("break_rounds", False):
                rounds.extend(tournament.break_rounds().all())
        if not rounds and self.rounds_required:
            raise CommandError("No rounds were given. (Use --help for more info.)")

        options["__rounds__"] = rounds
        return rounds

    def _confirm_rounds(self, rounds, **options):
        if not options["confirm"]:
            self.stdout.write(self.style.WARNING("WARNING! You are about to {} from the following rounds:".format(self.confirm_round_destruction)))
            for r in rounds:
                self.stdout.write(self.style.WARNING("  [{t}]: {r}".format(
                    t=r.tournament.name, r=r.name)))
            response = input("Are you sure? ")
            if response != "yes":
                raise CommandError("Cancelled by user.")

        elif options["confirm"] != options["round_selection"]:
            raise CommandError("The --confirm arguments did not match the positional arguments.")

    def handle(self, *args, **options):
        self._set_log_level(**options)
        rounds = self.get_rounds(options)
        if self.confirm_round_destruction:
            self._confirm_rounds(rounds, **options)
        for round in rounds:
            self.handle_round(round, **options)

    def handle_round(self, round, **options):
        """Perform the command's actions on ``round``, a ``Round``
        instance corresponding to the slug on the command line."""
        raise NotImplementedError(
            "subclasses of RoundCommand must provide a handle_round() method.")

    def handle_tournament(self, tournament, **options):
        raise NotImplementedError(
            "subclasses of RoundCommand do not use handle_tournament().")
