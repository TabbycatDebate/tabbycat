"""Unit tests for the importer module."""

from django.test import TestCase
import debate.models as m
import debate.importer

class TestImporter(TestCase):

    TESTDIR = "data/test/standard"
    TESTDIR_FAULTY = "data/test/error"

    def setUp(self):
        super(TestImporter, self).setUp()

        # create tournament
        self.t = Tournament(slug="import-test")
        self.t.save()
        self.importer = debate.importer.TournamentDataImporter(self.t)

    def _open_csv_file(self, filename):
        path = os.path.join(TESTDIR, filename + ".csv")
        return open(path, 'r')

    def test_rounds(self):
        f = self._open_csv_file("rounds")
        rounds, errors = self.importer.import_rounds(f)