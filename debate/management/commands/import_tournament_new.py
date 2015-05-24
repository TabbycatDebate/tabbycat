import os
import csv
import logging
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify

import debate.models as m
from debate.importer import AnorakTournamentDataImporter

class Command(BaseCommand):
    help = 'Delete all data for a tournament and import from specified directory.'

    def add_arguments(self, parser):
        parser.add_argument('path', help="Directory to import tournament data from")

        parser.add_argument('-r', '--auto-rounds', type=int, metavar='N', default=None,
            help='Create N preliminary rounds automatically. Use either this or a rounds.csv file, but not both.')
        parser.add_argument('-S', '--share-data', action='store_true', default=False,
            help='If specified, all institutions and adjudicators will not be tournament-specific.')
        parser.add_argument("--force", action='store_true', default=False,
            help='Delete tournaments if they already exist.')

        # Tournament options
        parser.add_argument('-s', '--slug', type=str, action='store', default=None,
            help='Override tournament slug. (Default: use name of directory.)'),
        parser.add_argument('--name', type=str, action='store', default=None,
            help='Override tournament name. (Default: use name of directory.)'),
        parser.add_argument('--short-name', type=str, action='store', default=None,
            help='Override tournament short name. (Default: use name of directory.)'),

    def _print_stage(self, message):
        if self.verbosity > 1:
            self.stdout.write("\033[1;36m" + message + "\033[0m\n")

    def _print_result(self, counts, errors):
        if self.verbosity > 1:
            if errors:
                for message in errors.itermessages():
                    self.stdout.write("\033[1;32m" + message + "\032[0m\n")
            count_strs = ("{1:d} {0:s}".format(model._meta.verbose_name_plural.lower(), count) for model, count in counts.iteritems())
            message = "Imported " + ", ".join(count_strs) + ", hit {1:d} errors".format(counts, len(errors))
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
        self.dirpath = self.get_data_path(options['path'])

        self.make_tournament()
        loglevel = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG][self.verbosity]
        self.importer = AnorakTournamentDataImporter(self.t, loglevel=loglevel)
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
                counts, errors = self.importer.import_rounds(f)
                self._print_result(counts, errors)
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
