import os
from xml.etree import ElementTree

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from importer.archive import Importer


class Command(BaseCommand):
    help = 'Import a non-existant tournament from an XML archive file.'

    def add_arguments(self, parser):
        parser.add_argument('file', help="File to import tournament data from")

    def handle(self, *args, **options):
        self.options = options
        self.filepath = self.get_data_path(options['file'])

        self.create_tournament()

    def get_data_path(self, arg):
        """Returns the file for the given command-line argument. If the
        argument is an absolute path and is an XML file, then looks there.
        Failing that, looks in the debate/data directory. Raises an exception
        if the file doesn't appear to exist, or is not an XML file."""

        def _check_return(path):
            if not os.path.isfile(path) or os.path.splitext[1] != '.xml':
                raise CommandError("The path '%s' is not a valid XML file" % path)
            self.stdout.write('Importing from file: ' + path)
            return path

        if os.path.isabs(arg):  # Absolute path
            return _check_return(arg)

        # relative path, look in debate/data
        base_path = os.path.join(settings.BASE_DIR, '..', 'data')
        data_path = os.path.join(base_path, arg)
        return _check_return(data_path)

    def create_tournament(self):
        """Given the path, does everything necessary to create the tournament."""
        contents = open(self.filepath, 'r')
        importer = Importer(ElementTree.fromstring(contents))
        importer.import_tournament()
