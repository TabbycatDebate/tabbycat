"""Unit tests for the importer module."""

from django.test import TestCase
from unittest import skip
import debate.models as m
import motions.models as mm
import options.models as cm
import venues.models as vm
import os.path
import logging

from debate.importer.anorak import AnorakTournamentDataImporter, TournamentDataImporterError

class TestImporterAnorak(TestCase):

    TESTDIR = "data/test/standard"
    TESTDIR_CHOICES = "data/test/choices"
    TESTDIR_ERRORS = "data/test/errors"

    def setUp(self):
        super(TestImporterAnorak, self).setUp()

        # create tournament
        self.t = m.Tournament(slug="import-test")
        self.t.save()
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        self.importer = AnorakTournamentDataImporter(self.t, logger=logger)

    def _open_csv_file(self, dir, filename):
        path = os.path.join(dir, filename + ".csv")
        return open(path, 'r')

    def test_rounds(self):
        f = self._open_csv_file(self.TESTDIR, "rounds")
        counts, errors = self.importer.import_rounds(f)
        self.assertEqual(counts, {m.Round: 6})
        self.assertFalse(errors)

    def test_venues(self):
        f = self._open_csv_file(self.TESTDIR, "venues")
        counts, errors = self.importer.import_venues(f)
        self.assertEqual(counts, {vm.VenueGroup: 7, vm.Venue: 23})
        self.assertFalse(errors)

    def test_institutions(self):
        f = self._open_csv_file(self.TESTDIR, "institutions")
        counts, errors = self.importer.import_institutions(f)
        self.assertEqual(counts, {m.Institution: 13, m.Region: 6})
        self.assertFalse(errors)

    @skip("test file does not yet exist")
    def test_teams(self):
        f = self._open_csv_file(self.TESTDIR, "teams")
        counts, errors = self.importer.import_teams(self)
        self.assertEqual(counts, {m.Team: 12})
        self.assertFalse(errors)

    def test_speakers(self):
        self.test_institutions()
        f = self._open_csv_file(self.TESTDIR, "speakers")
        counts, errors = self.importer.import_speakers(f)
        self.assertEqual(counts, {m.Team: 24, m.Speaker: 72})
        self.assertFalse(errors)

    def test_adjudicators(self):
        self.test_speakers()
        f = self._open_csv_file(self.TESTDIR, "judges")
        counts, errors = self.importer.import_adjudicators(f)
        self.assertEqual(counts, {
            m.Adjudicator: 27,
            m.AdjudicatorTestScoreHistory: 27,
            m.AdjudicatorInstitutionConflict: 36,
            m.AdjudicatorConflict: 7,
        })
        self.assertFalse(errors)

    def test_motions(self):
        self.test_rounds()
        f = self._open_csv_file(self.TESTDIR, "motions")
        counts, errors = self.importer.import_motions(f)
        self.assertEqual(counts, {mm.Motion: 18})
        self.assertFalse(errors)

    def test_config(self):
        f = self._open_csv_file(self.TESTDIR_CHOICES, "config")
        counts, errors = self.importer.import_config(f)
        self.assertEqual(counts, {cm.Config: 28})
        self.assertFalse(errors)

    def test_adj_feedback_questions(self):
        f = self._open_csv_file(self.TESTDIR, "questions")
        counts, errors = self.importer.import_adj_feedback_questions(f)
        self.assertEqual(counts, {m.AdjudicatorFeedbackQuestion: 7})
        self.assertFalse(errors)

    def test_invalid_line(self):
        self.test_speakers()
        f = self._open_csv_file(self.TESTDIR_ERRORS, "judges_invalid_line")
        with self.assertRaises(TournamentDataImporterError) as cm:
            counts, errors = self.importer.import_adjudicators(f)
        self.assertEqual(len(cm.exception), 10)
        self.assertItemsEqual([e.lineno for e in cm.exception.entries], (2, 5, 9, 10, 15, 16, 23, 24, 26, 28))

    def test_weird_choices_judges(self):
        self.test_speakers()
        f = self._open_csv_file(self.TESTDIR_CHOICES, "judges")
        counts, errors = self.importer.import_adjudicators(f)
        self.assertEqual(counts, {
            m.Adjudicator: 27,
            m.AdjudicatorTestScoreHistory: 27,
            m.AdjudicatorInstitutionConflict: 36,
            m.AdjudicatorConflict: 7,
        })
        self.assertFalse(errors)

    def test_blank_entry_strict(self):
        f = self._open_csv_file(self.TESTDIR_ERRORS, "venues")
        self.assertRaises(TournamentDataImporterError, self.importer.import_venues, f)

    def test_blank_entry_not_strict(self):
        f = self._open_csv_file(self.TESTDIR_ERRORS, "venues")
        self.importer.strict = False
        counts, errors = self.importer.import_venues(f)
        self.assertEqual(counts, {vm.Venue: 20, vm.VenueGroup: 7})
        self.assertEqual(len(errors), 3)
        self.importer.strict = True
