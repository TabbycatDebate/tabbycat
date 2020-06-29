"""Unit tests for the Anorak importer."""

import logging
import os.path

from django.test import TestCase

import adjallocation.models as am
import adjfeedback.models as fm
import breakqual.models as bm
import motions.models as mm
import participants.models as pm
import tournaments.models as tm
import venues.models as vm
from settings import BASE_DIR

from ..importers import TournamentDataImporterError
from ..importers.anorak import AnorakTournamentDataImporter


class TestImporterAnorak(TestCase):

    # BASE_DIR is /tabbycat this allows tests to run from there or project root
    TESTDIR = os.path.join(BASE_DIR, '../data/test/standard')
    TESTDIR_CHOICES = os.path.join(BASE_DIR, '../data/test/choices')
    TESTDIR_ERRORS = os.path.join(BASE_DIR, '../data/test/errors')

    def setUp(self):
        super(TestImporterAnorak, self).setUp()

        # create tournament
        self.maxDiff = None
        self.tournament = tm.Tournament(slug="import-test")
        self.tournament.save()
        self.logger = logging.getLogger(__name__)
        self.logger.propagate = False  # keep logs contained for tests
        self.logger.setLevel(logging.INFO)
        self.importer = AnorakTournamentDataImporter(self.tournament, logger=self.logger)

    def _open_csv_file(self, dir, filename):
        path = os.path.join(dir, filename + ".csv")
        return open(path, 'r')

    def assertCountsDictEqual(self, counts, expected): # noqa
        counts = dict(counts)
        self.assertEqual(counts, expected)

    def test_break_categories(self):
        f = self._open_csv_file(self.TESTDIR, "break_categories")
        self.importer.import_break_categories(f)
        self.assertCountsDictEqual(self.importer.counts, {bm.BreakCategory: 3})
        self.assertFalse(self.importer.errors)

    def test_rounds(self):
        self.test_break_categories()
        self.importer.reset_counts()
        f = self._open_csv_file(self.TESTDIR, "rounds")
        self.importer.import_rounds(f)
        self.assertCountsDictEqual(self.importer.counts, {tm.Round: 10})
        self.assertFalse(self.importer.errors)

    def test_venues(self):
        f = self._open_csv_file(self.TESTDIR, "venues")
        self.importer.import_venues(f)
        self.assertCountsDictEqual(self.importer.counts, {vm.VenueCategory: 7, vm.Venue: 25,
                vm.VenueCategory.venues.through: 25})
        self.assertFalse(self.importer.errors)

    def test_institutions(self):
        f = self._open_csv_file(self.TESTDIR, "institutions")
        self.importer.import_institutions(f)
        self.assertCountsDictEqual(self.importer.counts, {pm.Institution: 14, pm.Region: 3})
        self.assertFalse(self.importer.errors)

    def test_speakers(self):
        self.test_institutions()
        self.importer.reset_counts()
        f = self._open_csv_file(self.TESTDIR, "speakers")
        self.importer.import_speakers(f)
        self.assertCountsDictEqual(self.importer.counts, {
            pm.Team: 24,
            pm.Speaker: 72,
            am.TeamInstitutionConflict: 23,
        })
        self.assertFalse(self.importer.errors)

    def test_adjudicators(self):
        self.test_speakers()
        self.importer.reset_counts()
        f = self._open_csv_file(self.TESTDIR, "adjudicators")
        self.importer.import_adjudicators(f)
        self.assertCountsDictEqual(self.importer.counts, {
            pm.Adjudicator: 29,
            fm.AdjudicatorBaseScoreHistory: 29,
            am.AdjudicatorInstitutionConflict: 36,
            am.AdjudicatorAdjudicatorConflict: 6,
            am.AdjudicatorTeamConflict: 3,
        })
        self.assertFalse(self.importer.errors)

    def test_motions(self):
        self.test_rounds()
        self.importer.reset_counts()
        f = self._open_csv_file(self.TESTDIR, "motions")
        self.importer.import_motions(f)
        self.assertCountsDictEqual(self.importer.counts, {mm.Motion: 30})
        self.assertFalse(self.importer.errors)

    def test_adj_feedback_questions(self):
        f = self._open_csv_file(self.TESTDIR, "adj_feedback_questions")
        self.importer.import_adj_feedback_questions(f)
        self.assertCountsDictEqual(self.importer.counts, {fm.AdjudicatorFeedbackQuestion: 11})
        self.assertFalse(self.importer.errors)

    def test_venue_categories(self):
        f = self._open_csv_file(self.TESTDIR, "venue_categories")
        self.importer.import_venue_categories(f)
        self.assertCountsDictEqual(self.importer.counts, {vm.VenueCategory: 7})
        self.assertFalse(self.importer.errors)

    def test_adj_venue_constraints(self):
        self.test_venue_categories()
        self.importer.reset_counts()
        self.test_adjudicators()
        self.importer.reset_counts()
        f = self._open_csv_file(self.TESTDIR, "adj_venue_constraints")
        self.importer.import_adj_venue_constraints(f)
        self.assertCountsDictEqual(self.importer.counts, {vm.VenueConstraint: 2})
        self.assertFalse(self.importer.errors)

    def test_team_venue_constraints(self):
        self.test_venue_categories()
        self.importer.reset_counts()
        self.test_speakers()
        self.importer.reset_counts()
        f = self._open_csv_file(self.TESTDIR, "team_venue_constraints")
        self.importer.import_team_venue_constraints(f)
        self.assertCountsDictEqual(self.importer.counts, {vm.VenueConstraint: 2})
        self.assertFalse(self.importer.errors)

    def test_invalid_line(self):
        self.test_speakers()
        self.importer.reset_counts()
        f = self._open_csv_file(self.TESTDIR_ERRORS, "judges_invalid_line")
        with self.assertRaises(TournamentDataImporterError) as raisescm, self.assertLogs(self.logger, logging.ERROR) as logscm:
            self.importer.import_adjudicators(f)
        self.assertCountEqual([e.lineno for e in raisescm.exception.entries], (2, 9, 10, 15, 16, 23, 24, 25, 26, 28))
        self.assertEqual(len(raisescm.exception), 10)
        self.assertEqual(len(logscm.records), 10)

    def test_weird_choices_judges(self):
        self.test_speakers()
        self.importer.reset_counts()
        f = self._open_csv_file(self.TESTDIR_CHOICES, "judges")
        self.importer.import_adjudicators(f)
        self.assertCountsDictEqual(self.importer.counts, {
            pm.Adjudicator: 29,
            fm.AdjudicatorBaseScoreHistory: 29,
            am.AdjudicatorInstitutionConflict: 36,
            am.AdjudicatorAdjudicatorConflict: 6,
            am.AdjudicatorTeamConflict: 3,
        })
        self.assertFalse(self.importer.errors)

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
            self.importer.import_venues(f)
        self.assertCountsDictEqual(self.importer.counts, {vm.VenueCategory: 7, vm.Venue: 20,
                vm.VenueCategory.venues.through: 20})
        # There are three bad lines in the CSV file, but each one generates
        # two errors: one creating the venue itself, and one creating the
        # venuecategory-venue relationship (because the venue doesn't exist).
        self.assertEqual(len(self.importer.errors), 6)
        self.assertEqual(len(logscm.records), 6)
        self.importer.strict = True
