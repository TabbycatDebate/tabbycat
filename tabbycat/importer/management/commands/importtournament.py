import logging
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify

import participants.models as pm
import venues.models as vm
from draw.models import DebateTeam
from importer.importers import DUPLICATE_INFO, importer_registry, TournamentDataImporterFatal
from tournaments.models import Tournament
from tournaments.utils import auto_make_rounds


class Command(BaseCommand):
    help = 'Delete all data for a tournament and import from specified directory.'

    def add_arguments(self, parser):
        parser.add_argument('path', help="Directory to import tournament data from")
        parser.add_argument('items', help="Items to import (default: import all)", nargs="*", default=[])

        parser.add_argument('-e', '--encoding', type=str, default='utf-8',
                            help="Encoding used in the CSV files (default: utf-8)")
        parser.add_argument('-i', '--importer', type=str, default=None, choices=importer_registry,
                            help="Which importer to use (default: read from .importer file)")

        parser.add_argument('-r', '--auto-rounds', type=int, metavar='N', default=None,
                            help="Create N preliminary rounds automatically. Use either this or a rounds.csv file, but not both.")
        parser.add_argument('--force', action='store_true', default=False,
                            help="Do not prompt before deleting tournament that already exists.")
        parser.add_argument('--keep-existing', action='store_true', default=False,
                            help="Keep existing tournament and data, skipping lines if they are duplicates.")
        parser.add_argument('--relaxed', action='store_false', dest='strict', default=True,
                            help="Don't crash if there is an error, just skip and keep going.")

        # Cleaning shared objects
        parser.add_argument('--clean-shared', action='store_true', default=False,
                            help="Delete all shared objects from the database. Overrides --keep-existing.")
        parser.add_argument('--delete-institutions', action='store_true', default=False,
                            help="Delete all institutions from the database. Overrides --keep-existing.")
        parser.add_argument('--delete-venue-categories', action='store_true', default=False,
                            help="Delete all venue categories from the database. Overrides --keep-existing.")
        parser.add_argument('--delete-regions', action='store_true', default=False,
                            help="Delete all regions categories from the database. Overrides --keep-existing.")

        # Tournament options
        parser.add_argument('-s', '--slug', type=str, action='store', default=None,
                            help="Override tournament slug. (Default: use name of directory.)")
        parser.add_argument('--name', type=str, action='store', default=None,
                            help="Override tournament name. (Default: use name of directory.)")
        parser.add_argument('--short-name', type=str, action='store', default=None,
                            help="Override tournament short name. (Default: use name of directory.)")

    def handle(self, *args, **options):
        self.options = options
        self.verbosity = options['verbosity']
        self.color = not options['no_color']
        self.dirpath = self.get_data_path(options['path'])

        self.clean_shared_instances()
        self.make_tournament()
        loglevel = [logging.ERROR, logging.WARNING, DUPLICATE_INFO, logging.DEBUG][self.verbosity]

        importer_class = self.get_importer_class()
        self.importer = importer_class(
            self.tournament, loglevel=loglevel, strict=options['strict'], expect_unique=not options['keep_existing'])

        # Importer classes specify what they import, and in what order
        for item in self.importer.order:
            if item == 'rounds':
                self.make_rounds()
            else:
                self.make(item)

    def get_importer_class(self):
        importer_spec_filepath = os.path.join(self.dirpath, ".importer")
        importer_spec_arg = self.options['importer']

        if not os.path.exists(importer_spec_filepath) and importer_spec_arg is None:
            raise CommandError("The --importer option wasn't specified and the file "
                "%s does not exist." % importer_spec_filepath)

        if os.path.exists(importer_spec_filepath):
            try:
                f = open(importer_spec_filepath, 'r', encoding=self.options['encoding'])
            except OSError as e:
                raise CommandError("Error opening file %s: %s" % (importer_spec_filepath, e))
            importer_spec = f.read().strip()
        else:
            importer_spec = None

        if importer_spec_arg is not None:
            if importer_spec is not None and importer_spec_arg != importer_spec:
                self._warning("Using importer %s, but data directory suggests "
                        "%s" % (importer_spec_arg, importer_spec))
            importer_spec = importer_spec_arg

        if importer_spec not in importer_registry:
            raise CommandError("There is no importer %r." % importer_spec)

        return importer_registry[importer_spec]

    def _print_stage(self, message):
        if self.verbosity > 0:
            if self.color:
                message = "\033[0;36m" + message + "\033[0m\n"
            self.stdout.write(message)

    def _print_result(self):
        if self.verbosity > 0:
            counts = self.importer.counts
            errors = self.importer.errors
            if errors:
                for message in errors.itermessages():
                    if self.color:
                        message = "\033[1;32m" + message + "\033[0m\n"
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

    def _print_loud(self, message):
        if self.color:
            message = "\033[1;33m" + message + "\033[0m\n"
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
            return open(path, 'r', encoding=self.options['encoding'])
        except OSError as e:
            self._warning("Skipping '{0:s}': {1:s}".format(filename, e.strerror))
            return None

    def make(self, model):
        """Imports objects of the specified model, by calling the import_<model>
        method to import from the file <model>.csv."""
        if self.options['items'] and model not in self.options['items']:
            return
        f = self._open_csv_file(model)
        import_method = getattr(self.importer, 'import_' + model)
        if f is not None:
            self._print_stage("Importing %s.csv" % model)
            self.importer.reset_counts()
            try:
                import_method(f)
            except TournamentDataImporterFatal as e:
                raise CommandError(e)
            self._print_result()

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

    def clean_shared_instances(self):
        """Removes shared instances from the database, depending on what options
        the user selected."""
        if self.options['clean_shared'] or self.options['delete_institutions']:
            self._warning("Deleting all institutions from the database")
            pm.Institution.objects.all().delete()

        if self.options['clean_shared'] or self.options['delete_venue_categories']:
            self._warning("Deleting all room categories from the database")
            vm.VenueCategory.objects.all().delete()

        if self.options['clean_shared'] or self.options['delete_regions']:
            self._warning("Deleting all regions from the database")
            pm.Region.objects.all().delete()

    def make_tournament(self):
        """Given the path, does everything necessary to create the tournament,
        and sets self.tournament to be the newly-created tournament.
        """
        slug, name, short_name = self.resolve_tournament_fields()
        self.check_existing_tournament(slug)
        self.tournament = self.create_tournament(slug, name, short_name)

    def make_rounds(self):
        """Makes rounds using an automatic rounds maker if --auto-rounds is
        enabled, or using the CSV file if not."""
        if self.options['auto_rounds'] is None:
            self.make('rounds')
        else:
            if os.path.exists(self._csv_file_path('rounds')):
                self._warning("Ignoring file 'rounds.csv' because --auto-rounds used")
            num_rounds = self.options['auto_rounds']
            auto_make_rounds(self.tournament, num_rounds)
            self._print_stage("Auto-made %d rounds" % num_rounds)

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
                self._print_loud("WARNING! A tournament with slug '" + slug + "' already exists.")
                self._print_loud("You are about to delete EVERYTHING for this tournament.")
                response = input("Are you sure? (yes/no) ")
                if response != "yes":
                    raise CommandError("Cancelled by user.")
            DebateTeam.objects.filter(team__tournament__slug=slug).delete()  # protected from cascade deletion
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
