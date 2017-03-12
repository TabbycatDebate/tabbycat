"""Unit tests for the Anorak importer."""

import logging
import os.path

from unittest import skip

from settings import BASE_DIR

from django.test import TestCase

import adjallocation.models as am
import adjfeedback.models as fm
import breakqual.models as bm
import motions.models as mm
import participants.models as pm
import tournaments.models as tm
import venues.models as vm

from ..anorak import AnorakTournamentDataImporter
from ..base import TournamentDataImporterError


class TestImporterAnorak(TestCase):

    # BASE_DIR is /tabbycat this allows tests to run from there or project root
    TESTDIR = os.path.join(BASE_DIR, '../data/test/standard')
    TESTDIR_CHOICES = os.path.join(BASE_DIR, '../data/test/choices')
    TESTDIR_ERRORS = os.path.join(BASE_DIR, '../data/test/errors')

    def setUp(self):
        super(TestImporterAnorak, self).setUp()

        # create tournament
        self.maxDiff = None
        self.t = tm.Tournament(slug="import-test")
        self.t.save()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.importer = AnorakTournamentDataImporter(self.t, logger=self.logger)

    def _open_csv_file(self, dir, filename):
        path = os.path.join(dir, filename + ".csv")
        return open(path, 'r')

    def assertCountsDictEqual(self, counts, expected): # noqa
        counts = dict(counts)
        self.assertEqual(counts, expected)

    def test_break_categories(self):
        f = self._open_csv_file(self.TESTDIR, "break_categories")
        counts, errors = self.importer.import_break_categories(f)
        self.assertCountsDictEqual(counts, {bm.BreakCategory: 3})
        self.assertFalse(errors)

    def test_rounds(self):
        self.test_break_categories()
        f = self._open_csv_file(self.TESTDIR, "rounds")
        counts, errors = self.importer.import_rounds(f)
        self.assertCountsDictEqual(counts, {tm.Round: 10})
        self.assertFalse(errors)

    def test_auto_make_rounds(self):
        self.importer.auto_make_rounds(7)
        self.assertEqual(self.t.round_set.count(), 7)

    def test_venues(self):
        f = self._open_csv_file(self.TESTDIR, "venues")
        counts, errors = self.importer.import_venues(f)
        self.assertCountsDictEqual(counts, {vm.VenueCategory: 8, vm.Venue: 23,
                vm.VenueCategory.venues.through: 22})
        self.assertFalse(errors)

    def test_institutions(self):
        f = self._open_csv_file(self.TESTDIR, "institutions")
        counts, errors = self.importer.import_institutions(f)
        self.assertCountsDictEqual(counts, {pm.Institution: 13, pm.Region: 6})
        self.assertFalse(errors)

    @skip("test file does not yet exist")
    def test_teams(self):
        f = self._open_csv_file(self.TESTDIR, "teams")  # noqa
        counts, errors = self.importer.import_teams(self)
        self.assertCountsDictEqual(counts, {pm.Team: 12})
        self.assertFalse(errors)

    def test_speakers(self):
        self.test_institutions()
        f = self._open_csv_file(self.TESTDIR, "speakers")
        counts, errors = self.importer.import_speakers(f)
        self.assertCountsDictEqual(counts, {pm.Team: 24, pm.Speaker: 72})
        self.assertFalse(errors)

    def test_adjudicators(self):
        self.test_speakers()
        f = self._open_csv_file(self.TESTDIR, "judges")
        counts, errors = self.importer.import_adjudicators(f)
        self.assertCountsDictEqual(counts, {
            pm.Adjudicator: 27,
            fm.AdjudicatorTestScoreHistory: 24,
            am.AdjudicatorInstitutionConflict: 36,
            am.AdjudicatorAdjudicatorConflict: 5,
            am.AdjudicatorConflict: 8,
        })
        self.assertFalse(errors)

    def test_motions(self):
        self.test_rounds()
        f = self._open_csv_file(self.TESTDIR, "motions")
        counts, errors = self.importer.import_motions(f)
        self.assertCountsDictEqual(counts, {mm.Motion: 18})
        self.assertFalse(errors)

    def test_adj_feedback_questions(self):
        f = self._open_csv_file(self.TESTDIR, "questions")
        counts, errors = self.importer.import_adj_feedback_questions(f)
        self.assertCountsDictEqual(counts, {fm.AdjudicatorFeedbackQuestion: 11})
        self.assertFalse(errors)

    def test_venue_categories(self):
        self.test_venues()
        f = self._open_csv_file(self.TESTDIR, "venue_categories")
        counts, errors = self.importer.import_venue_categories(f)
        self.assertCountsDictEqual(counts, {vm.VenueCategory: 7})
        self.assertFalse(errors)

    def test_adj_venue_constraints(self):
        self.test_adjudicators()
        self.test_venue_categories()
        f = self._open_csv_file(self.TESTDIR, "adj_venue_constraints")
        counts, errors = self.importer.import_adj_venue_constraints(f)
        self.assertCountsDictEqual(counts, {vm.VenueConstraint: 3})
        self.assertFalse(errors)

    def test_team_venue_constraints(self):
        self.test_speakers()
        self.test_venue_categories()
        f = self._open_csv_file(self.TESTDIR, "team_venue_constraints")
        counts, errors = self.importer.import_team_venue_constraints(f)
        self.assertCountsDictEqual(counts, {vm.VenueConstraint: 2})
        self.assertFalse(errors)

    def test_invalid_line(self):
        self.test_speakers()
        f = self._open_csv_file(self.TESTDIR_ERRORS, "judges_invalid_line")
        with self.assertRaises(TournamentDataImporterError) as raisescm, self.assertLogs(self.logger, logging.ERROR) as logscm:
            counts, errors = self.importer.import_adjudicators(f)
        self.assertCountEqual([e.lineno for e in raisescm.exception.entries], (2, 5, 9, 10, 15, 16, 23, 24, 26, 28))
        self.assertEqual(len(raisescm.exception), 10)
        self.assertEqual(len(logscm.records), 10)

    def test_weird_choices_judges(self):
        self.test_speakers()
        f = self._open_csv_file(self.TESTDIR_CHOICES, "judges")
        counts, errors = self.importer.import_adjudicators(f)
        self.assertCountsDictEqual(counts, {
            pm.Adjudicator: 27,
            am.AdjudicatorAdjudicatorConflict: 0,
            fm.AdjudicatorTestScoreHistory: 27,
            am.AdjudicatorInstitutionConflict: 36,
            am.AdjudicatorConflict: 7,
        })
        self.assertFalse(errors)

    def test_blank_entry_strict(self):
        f = self._open_csv_file(self.TESTDIR_ERRORS, "venues")
        with self.assertRaises(TournamentDataImporterError) as raisescm, self.assertLogs(self.logger, logging.ERROR) as logscm:
            self.importer.import_venues(f)
        # There are three bad lines in the CSV file, and because this raises
        # the exception straight after the Venue creation loop, it bad line
        # generates one error (not two, as in the non-strict version below).
        self.assertEqual(len(raisescm.exception), 3)
        self.assertCountEqual([e.lineno for e in raisescm.exception.entries], (9, 17, 21))
        self.assertEqual(len(logscm.records), 3)

    def test_blank_entry_not_strict(self):
        f = self._open_csv_file(self.TESTDIR_ERRORS, "venues")
        self.importer.strict = False
        with self.assertLogs(self.logger, logging.WARNING) as logscm:
            counts, errors = self.importer.import_venues(f)
        self.assertCountsDictEqual(counts, {vm.VenueCategory: 7, vm.Venue: 20,
                vm.VenueCategory.venues.through: 20})
        # There are three bad lines in the CSV file, but each one generates
        # two errors: one creating the venue itself, and one creating the
        # venuecategory-venue relationship (because the venue doesn't exist).
        self.assertEqual(len(errors), 6)
        self.assertEqual(len(logscm.records), 6)
        self.importer.strict = True
