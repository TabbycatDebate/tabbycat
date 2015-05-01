"""Unit tests for the importer module."""

from django.test import TestCase
from unittest import skip
import debate.models as m
import debate.importer
import os.path
import logging

class TestImporter(TestCase):

    TESTDIR = "data/test/standard"
    TESTDIR_ERRORS = "data/test/errors"

    def setUp(self):
        super(TestImporter, self).setUp()

        # create tournament
        self.t = m.Tournament(slug="import-test")
        self.t.save()
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.ERROR)
        self.importer = debate.importer.TournamentDataImporter(self.t, logger=logger)

    def _open_csv_file(self, dir, filename):
        path = os.path.join(dir, filename + ".csv")
        return open(path, 'r')

    def test_rounds(self):
        f = self._open_csv_file(self.TESTDIR, "rounds")
        rounds, errors = self.importer.import_rounds(f)

    def test_venues(self):
        f = self._open_csv_file(self.TESTDIR, "venues")
        institutions, errors = self.importer.import_venues(f)

    def test_institutions(self):
        f = self._open_csv_file(self.TESTDIR, "institutions")
        institutions, errors = self.importer.import_institutions(f)

    # @skip
    # def test_invalid_line(self):
    #     pass

    def test_blank_entry(self):
        f = self._open_csv_file(self.TESTDIR_ERRORS, "venues")
        institutions, errors = self.importer.import_venues(f)
