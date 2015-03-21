"""Unit tests for the importer module."""

from django.test import TestCase
import debate.models as m
import debate.importer
import os.path

class TestImporter(TestCase):

    TESTDIR = "data/test/standard"
    TESTDIR_FAULTY = "data/test/error"

    def setUp(self):
        super(TestImporter, self).setUp()

        # create tournament
        self.t = m.Tournament(slug="import-test")
        self.t.save()
        self.importer = debate.importer.TournamentDataImporter(self.t)

    def _open_csv_file(self, filename):
        path = os.path.join(self.TESTDIR, filename + ".csv")
        return open(path, 'r')

    def test_rounds(self):
        f = self._open_csv_file("rounds")
        rounds, errors = self.importer.import_rounds(f)

    def test_venues(self):
        f = self._open_csv_file("venues")
        institutions, errors = self.importer.import_venues(f)

    def test_institutions(self):
        f = self._open_csv_file("institutions")
        institutions, errors = self.importer.import_institutions(f)