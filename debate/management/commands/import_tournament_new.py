from django.core.management.base import LabelCommand, CommandError
from django.conf import settings
from django.template.defaultfilters import slugify
import os
import csv
import debate.models as m
from optparse import make_option

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
        make_option('-s', '--slug', type=str, action='store', default=None,
            help='Override tournament slug.'),
        make_option('--name', type=str, action='store', default=None,
            help='Override tournament name.'),
        make_option('--short-name', type=str, action='store', default=None,
            help='Override tournament short name.'),
    )

    def _print_stage(self, message):
        if self.verbosity > 0:
            print("\e[1;36m" + message + "\e[0m")

    def handle(self, *args, **options):
        self.verbosity = options['verbosity']
        self.check_if_tournament_exists(label, options['force'])
        dirname = self.get_dir(self, label)
        tslug = slugify(unicode(os.path.basename(dirname.rstrip('/'))))


    def get_dir(self, label):
        """Returns the directory for the given label. If the label is an
        absolute path and is a directory, then looks there first. Failing that,
        looks in the debate/data directory."""
        if os.path.isabs(label) and os.path.isdir(label): # absolute path
            return label

        # relative path, look in debate/data
        base_path = os.path.join(settings.PROJECT_PATH, 'data')
        data_path = os.path.join(base_path, label)
        return data_path

    def resolve_tournament_fields(self):
        pass

    def check_if_tournament_exists(self, label, force=False):
        """Checks if a tournament exists."""
        if force:
            return
        slug = slugify(unicode(label))
        if m.Tournament.objects.filter(slug=slug).exists():
            self.stdout.write("WARNING! A tournament called '" + label + "' already exists.")
            self.stdout.write("You are about to delete EVERYTHING for this tournament.")
            response = raw_input("Are you sure? ")
            if response != "yes":
                self.stdout.write("Cancelled.")
                raise CommandError("Cancelled by user.")
            m.Tournament.objects.filter(slug=slug).delete()

    def create_tournament(self, slug):
        """Creates, saves and returns a tournament with the given label.
        Raises exception on error."""
        self._print_stage("Creating tournament '" + label + "'")
        short_name = (label[:24] + '..') if len(label) > 75 else label
        t = m.Tournament(name=label, short_name=short_name, slug=slug)
        t.save()
        return t

    def create_rounds_from_file(self, dirname):
        pass
