"""Unit tests for the importer module."""

from django.test import TestCase
from unittest import skip
import debate.models as m
import os.path
import logging

from debate.importer import TournamentDataImporter, TournamentDataImporterError

class TestImporter(TestCase):

    TESTDIR = "data/test/standard"
    TESTDIR_ERRORS = "data/test/errors"

    def setUp(self):
        super(TestImporter, self).setUp()

        # create tournament
        self.t = m.Tournament(slug="import-test")
        self.t.save()
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        self.importer = TournamentDataImporter(self.t, logger=logger)

    def _open_csv_file(self, dir, filename):
        path = os.path.join(dir, filename + ".csv")
        return open(path, 'r')

    def test_rounds(self):
        f = self._open_csv_file(self.TESTDIR, "rounds")
        rounds, errors = self.importer.import_rounds(f)
        self.assertEqual(rounds, 6)
        self.assertEqual(errors, 0)

    def test_venues(self):
        f = self._open_csv_file(self.TESTDIR, "venues")
        venues, errors = self.importer.import_venues(f)
        self.assertEqual(venues, 23)
        self.assertEqual(errors, 0)

    def test_institutions(self):
        f = self._open_csv_file(self.TESTDIR, "institutions")
        institutions, errors = self.importer.import_institutions(f)
        self.assertEqual(institutions, 14)
        self.assertEqual(errors, 0)

    @skip
    def test_teams(self):
        f = self._open_csv_file(self, TESTDIR, "teams")
        teams, errors = self.importer.import_teams(self)
        self.assertEqual(teams, 12)
        self.assertEqual(errors, 0)

    # @skip
    # def test_invalid_line(self):
    #     pass

    def test_blank_entry_strict(self):
        f = self._open_csv_file(self.TESTDIR_ERRORS, "venues")
        self.assertRaises(TournamentDataImporterError, self.importer.import_venues, f)

    def test_blank_entry_not_strict(self):
        f = self._open_csv_file(self.TESTDIR_ERRORS, "venues")
        self.importer.strict = False
        venues, errors = self.importer.import_venues(f)
        self.assertEqual(venues, 20)
        self.assertEqual(errors, 3)
        self.importer.strict = True
