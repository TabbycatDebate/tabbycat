import os
import csv
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify

import debate.models as m
import debate.importer

class Command(BaseCommand):
    args = 'path [--auto-rounds n] [--share-data] [--slug SLUG] [--name NAME] [--short-name NAME]'
    help = 'Delete all data for a tournament and import from specified directory.'

    option_list = BaseCommand.option_list + (
        make_option('-r', '--auto-rounds', type=int, metavar='N', default=None,
            help='Create N preliminary rounds automatically. Use either this or a rounds.csv file, but not both.'),
        make_option('-S', '--share-data', action='store_true', default=False,
            help='If specified, all institutions and adjudicators will not be tournament-specific.'),
        make_option("--force", action='store_true', default=False,
            help='Delete tournaments if they already exist.'),

        # Tournament options
        make_option('-s', '--slug', type=str, action='store', default=None,
            help='Override tournament slug. (Default: use name of directory.)'),
        make_option('--name', type=str, action='store', default=None,
            help='Override tournament name. (Default: use name of directory.)'),
        make_option('--short-name', type=str, action='store', default=None,
            help='Override tournament short name. (Default: use name of directory.)'),
    )

    def _print_stage(self, message):
        if self.verbosity > 1:
            self.stdout.write("\033[1;36m" + message + "\033[0m\n")

    def _print_result(self, message):
        if self.verbosity > 1:
            self.stdout.write("\033[0;36m" + message + "\033[0m\n")

    def _warning(self, message):
        if self.verbosity > 0:
            self.stdout.write("\033[1;33mWarning: " + message + "\033[0m\n")

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
        except IOError as e:
            self._warning("Problem opening '{0:s}': {1:s}".format(filename, e))
            return None

    def handle(self, *args, **options):
        self.options = options
        self.verbosity = options['verbosity']

        if len(args) != 1:
            raise CommandError('There must be exactly one positional argument, the directory where the data is stored.')
        arg = args[0]

        self.dirpath = self.get_data_path(arg)

        self.make_tournament()
        self.importer = debate.importer.TournamentDataImporter(self.t)
        self.make_rounds()

    def get_data_path(self, arg):
        """Returns the directory for the given command-line argument. If the
        argument is an absolute path and is a directory, then looks there.
        Failing that, looks in the debate/data directory. Raises an exception
        if the directory doesn't appear to exist, or is not a directory."""
        if os.path.isabs(arg) and os.path.isdir(arg): # absolute path
            return arg

        # relative path, look in debate/data
        base_path = os.path.join(settings.PROJECT_PATH, 'data')
        data_path = os.path.join(base_path, arg)
        return data_path

    def make_tournament(self):
        """Given the path, does everything necessary to create the tournament,
        and sets self.t to be the newly-created tournament.
        """
        slug, name, short_name = self.resolve_tournament_fields()
        self.clean_existing_tournament(slug)
        self.t = self.create_tournament(slug, name, short_name)

    def make_rounds(self):
        if self.options['auto_rounds'] is None:
            f = self._open_csv_file('rounds')
            if f is not None:
                rounds, errors = self.importer.import_rounds(f)
                self._print_result("Imported {0:d} rounds, hit {1:d} errors".format(rounds, errors))
        else:
            if os.path.exists(self._csv_file_path('rounds')):
                self._warning("Ignoring file 'rounds.csv' because --auto-rounds used")
            self.importer.auto_make_rounds(self.options['auto_rounds'])

    def resolve_tournament_fields(self):
        """Figures out what the tournament slug, name and short name should be,
        and returns the three as a 3-tuple.
        """
        basename = unicode(os.path.basename(self.dirpath.rstrip('/')))
        name = self.options['name'] or basename
        short_name = self.options['short_name'] or (basename[:24] + '..' if len(basename) > 24 else basename)
        slug = self.options['slug'] or slugify(basename)
        return slug, name, short_name

    def clean_existing_tournament(self, slug):
        """Checks if a tournament exists and deletes it if it does."""
        if self.options['force']:
            return
        if m.Tournament.objects.filter(slug=slug).exists():
            self.stdout.write("WARNING! A tournament with slug '" + slug + "' already exists.")
            self.stdout.write("You are about to delete EVERYTHING for this tournament.")
            response = raw_input("Are you sure? ")
            if response != "yes":
                raise CommandError("Cancelled by user.")
            m.Tournament.objects.filter(slug=slug).delete()

    def create_tournament(self, slug, name, short_name):
        """Creates, saves and returns a tournament with the given slug.
        Raises exception on error."""
        self._print_stage("Creating tournament '" + slug + "'")
        t = m.Tournament(name=name, short_name=short_name, slug=slug)
        t.save()
        return t
