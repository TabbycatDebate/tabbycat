import os
import logging

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify

import participants.models as pm
import venues.models as vm
from tournaments.models import Tournament
from importer.anorak import AnorakTournamentDataImporter
from importer.base import DUPLICATE_INFO, TournamentDataImporterFatal


class Command(BaseCommand):
    help = 'Delete all data for a tournament and import from specified directory.'

    def add_arguments(self, parser):
        parser.add_argument('path', help="Directory to import tournament data from")
        parser.add_argument('items', help="Items to import (default: import all)", nargs="*", default=[])

        parser.add_argument('-r', '--auto-rounds', type=int, metavar='N', default=None,
                            help='Create N preliminary rounds automatically. Use either this or a rounds.csv file, but not both.')
        parser.add_argument('--force', action='store_true', default=False,
                            help='Do not prompt before deleting tournament that already exists.')
        parser.add_argument('--keep-existing', action='store_true', default=False,
                            help='Keep existing tournament and data, skipping lines if they are duplicates.')
        parser.add_argument('--delete-institutions', action='store_true', default=False,
                            help='Delete all institutions from the database. Overrides --keep-existing.')
        parser.add_argument('--delete-venue-categories', action='store_true', default=False,
                            help='Delete all venue categories from the database. Overrides --keep-existing.')
        parser.add_argument('--relaxed', action='store_false', dest='strict', default=True,
                            help='Don\'t crash if there is an error, just skip and keep going.')

        # Tournament options
        parser.add_argument('-s', '--slug', type=str, action='store', default=None,
                            help='Override tournament slug. (Default: use name of directory.)'),
        parser.add_argument('--name', type=str, action='store', default=None,
                            help='Override tournament name. (Default: use name of directory.)'),
        parser.add_argument('--short-name', type=str, action='store', default=None,
                            help='Override tournament short name. (Default: use name of directory.)'),

    def handle(self, *args, **options):
        self.options = options
        self.verbosity = options['verbosity']
        self.color = not options['no_color']
        self.dirpath = self.get_data_path(options['path'])

        if options['delete_institutions']:
            self.delete_institutions()
        if options['delete_venue_categories']:
            self.delete_venue_categories()
        self.make_tournament()
        loglevel = [logging.ERROR, logging.WARNING, DUPLICATE_INFO, logging.DEBUG][self.verbosity]
        self.importer = AnorakTournamentDataImporter(
            self.t, loglevel=loglevel, strict=options['strict'], expect_unique=not options['keep_existing'])

        self._make('venue_categories')
        self._make('venues')
        self._make('regions')
        self._make('institutions')
        self._make('break_categories')
        self._make('teams')
        self._make('speakers')
        self._make('judges', self.importer.import_adjudicators)
        self.make_rounds()
        self._make('motions')
        self._make('sides')
        self._make('questions', self.importer.import_adj_feedback_questions)
        self._make('venue_constraint_categories')
        self._make('adj_venue_constraints')
        self._make('team_venue_constraints')

    def _print_stage(self, message):
        if self.verbosity > 0:
            if self.color:
                message = "\033[0;36m" + message + "\033[0m\n"
            self.stdout.write(message)

    def _print_result(self, counts, errors):
        if self.verbosity > 0:
            if errors:
                for message in errors.itermessages():
                    if self.color:
                        message = "\033[1;32m" + message + "\032[0m\n"
                    self.stdout.write(message)
            count_strs = ("{1:d} {0}".format(model._meta.verbose_name_plural, count) for model, count in counts.items())
            message = "Imported " + ", ".join(count_strs) + ", hit {1:d} errors".format(counts, len(errors))
            if self.color:
                "\033[0;36m" + message + "\033[0m\n"
            self.stdout.write(message)

    def _warning(self, message):
        if self.verbosity > 0:
            if self.color:
                message = "\033[0;33mWarning: " + message + "\033[0m\n"
            self.stdout.write(message)

    def _csv_file_path(self, filename):
        """Requires self.dirpath to be defined."""
        if not filename.endswith('.csv'):
            filename += '.csv'
        return os.path.join(self.dirpath, filename)

    def _open_csv_file(self, filename):
        """Requires self.dirpath to be defined."""
        path = self._csv_file_path(filename)
        try:
            return open(path, 'r')
        except OSError as e:
            self._warning("Skipping '{0:s}': {1:s}".format(filename, e.strerror))
            return None

    def _make(self, filename, import_method=None):
        """Imports objects from the given file using the given import method.
        If the import method isn't given, it is inferred from the file name."""
        if self.options['items'] and filename not in self.options['items']:
            return
        f = self._open_csv_file(filename)
        if import_method is None:
            import_method = getattr(self.importer, 'import_' + filename)
        if f is not None:
            self._print_stage("Importing %s.csv" % filename)
            try:
                counts, errors = import_method(f)
            except TournamentDataImporterFatal as e:
                raise CommandError(e)
            self._print_result(counts, errors)

    def get_data_path(self, arg):
        """Returns the directory for the given command-line argument. If the
        argument is an absolute path and is a directory, then looks there.
        Failing that, looks in the debate/data directory. Raises an exception
        if the directory doesn't appear to exist, or is not a directory."""
        def _check_return(path):
            if not os.path.isdir(path):
                raise CommandError("The path '%s' is not a directory" % path)
            self.stdout.write('Importing from directory: ' + path)
            return path

        if os.path.isabs(arg):  # Absolute path
            return _check_return(arg)

        # relative path, look in debate/data
        base_path = os.path.join(settings.BASE_DIR, '..', 'data')
        data_path = os.path.join(base_path, arg)
        return _check_return(data_path)

    def delete_institutions(self):
        """Deletes all institutions from the database."""
        self._warning("Deleting all institutions from the database")
        pm.Institution.objects.all().delete()

    def delete_venue_categories(self):
        """Deletes all venue categories from the database."""
        self._warning("Deleting all venue categories from the database")
        vm.VenueCategory.objects.all().delete()

    def make_tournament(self):
        """Given the path, does everything necessary to create the tournament,
        and sets self.t to be the newly-created tournament.
        """
        slug, name, short_name = self.resolve_tournament_fields()
        self.check_existing_tournament(slug)
        self.t = self.create_tournament(slug, name, short_name)

    def make_rounds(self):
        """Makes rounds using an automatic rounds maker if --auto-rounds is
        enabled, or using the CSV file if not."""
        if self.options['auto_rounds'] is None:
            self._make('rounds')
        else:
            if os.path.exists(self._csv_file_path('rounds')):
                self._warning("Ignoring file 'rounds.csv' because --auto-rounds used")
            self.importer.auto_make_rounds(self.options['auto_rounds'])

    def resolve_tournament_fields(self):
        """Figures out what the tournament slug, name and short name should be,
        and returns the three as a 3-tuple.
        """
        basename = str(os.path.basename(self.dirpath.rstrip('/')))
        name = self.options['name'] or basename
        short_name = self.options['short_name'] or (basename[:24] + '..' if len(basename) > 24 else basename)
        slug = self.options['slug'] or slugify(basename)
        return slug, name, short_name

    def check_existing_tournament(self, slug):
        """Checks if a tournament exists. If --keep-existing was not used,
        deletes it. If it was used, and the tournament does not exist, raises
        and error."""
        exists = Tournament.objects.filter(slug=slug).exists()
        if exists and not self.options['keep_existing'] and not self.options['items']:
            if not self.options['force']:
                self.stdout.write("WARNING! A tournament with slug '" + slug + "' already exists.")
                self.stdout.write("You are about to delete EVERYTHING for this tournament.")
                response = input("Are you sure? ")
                if response != "yes":
                    raise CommandError("Cancelled by user.")
            Tournament.objects.filter(slug=slug).delete()

        elif not exists and self.options['keep_existing']:
            raise CommandError("Used --keep-existing, but tournament %r does not exist" % slug)

    def create_tournament(self, slug, name, short_name):
        """Creates, saves and returns a tournament with the given slug.
        Raises exception on error."""
        try:
            existing = Tournament.objects.get(slug=slug)
        except Tournament.DoesNotExist:
            self._print_stage("Creating tournament %r" % slug)
            t = Tournament(name=name, short_name=short_name, slug=slug)
            t.save()
            return t
        else:
            self._warning("Tournament %r already exists, not creating" % slug)
            return existing
