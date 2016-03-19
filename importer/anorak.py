from .base import BaseTournamentDataImporter, TournamentDataImporterError
import adjallocation.models as am
import breakqual.models as bm
import draw.models as dm
import adjfeedback.models as fm
import motions.models as mm
import options.models as cm
import participants.models as pm
import tournaments.models as tm
import tournaments.utils
import venues.models as vm
import csv

class AnorakTournamentDataImporter(BaseTournamentDataImporter):
    """Anorak: The original tournament data format."""

    ROUND_STAGES = {
        ("preliminary", "p"): tm.Round.STAGE_PRELIMINARY,
        ("elimination", "break", "e", "b"): tm.Round.STAGE_ELIMINATION,
    }

    ROUND_DRAW_TYPES = {
        ("random", "r"): tm.Round.DRAW_RANDOM,
        ("manual", "m"): tm.Round.DRAW_MANUAL,
        ("round robin", "d"): tm.Round.DRAW_ROUNDROBIN,
        ("power paired", "p"): tm.Round.DRAW_POWERPAIRED,
        ("first elimination", "1st elimination", "1e", "f"): tm.Round.DRAW_FIRSTBREAK,
        ("subsequent elimination", "2nd elimination", "2e", "b"): tm.Round.DRAW_BREAK,
    }

    GENDERS = {
        ("male", "m"): pm.Person.GENDER_MALE,
        ("female", "f"): pm.Person.GENDER_FEMALE,
        ("other", "o"): pm.Person.GENDER_OTHER,
    }

    TEAM_POSITIONS = {
        ("affirmative", "aff", "a"): dm.TeamPositionAllocation.POSITION_AFFIRMATIVE,
        ("negative", "neg", "n"): dm.TeamPositionAllocation.POSITION_NEGATIVE,
    }

    FEEDBACK_ANSWER_TYPES = {
        ("checkbox"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_BOOLEAN_CHECKBOX,
        ("yes no select", "yesno"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_BOOLEAN_SELECT,
        ("integer textbox", "int", "integer"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_INTEGER_TEXTBOX,
        ("integer scale", "scale"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_INTEGER_SCALE,
        ("float"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_FLOAT,
        ("text"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_TEXT,
        ("textbox", "long text", "longtext"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_LONGTEXT,
        ("select single", "single select"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_SINGLE_SELECT,
        ("select multiple", "multiple select"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_MULTIPLE_SELECT,
    }

    def import_rounds(self, f):
        """Imports rounds from a file.
        Each line has:
            seq, name, abbreviation, stage, draw_type, silent, feedback_weight, break_category
        """
        interpreter = self.construct_interpreter(
            tournament=self.tournament,
            seq=int,
            stage=lambda x: self._lookup(self.ROUND_STAGES, x or "p", "draw stage"),
            draw_type=lambda x: self._lookup(self.ROUND_DRAW_TYPES, x or "r", "draw type"),
            silent=lambda x: bool(int(x)),
            feedback_weight=lambda x: float(x) if x is not None else 0.7,
            break_category=lambda x: bm.BreakCategory.objects.get(slug=x, tournament=self.tournament)
        )
        counts, errors = self._import(f, tm.Round, interpreter)

        # Set the round with the lowest known seqno to be the current round.
        # TODO (as above)
        self.tournament.current_round = tm.Round.objects.get(
                tournament=self.tournament, seq=1)
        self.tournament.save()

        return counts, errors

    def import_regions(self, f):
        """Imports regions from a file.
        Each line has:
            name
        """
        interpreter = self.construct_interpreter(
            tournament=self.tournament
        )
        return self._import(f, pm.Region, interpreter)

    def import_institutions(self, f, auto_create_regions=True):
        """Imports institutions from a file, also creating regions as needed
        (unless 'auto_create_regions' is False)
        Each line has:
            name, code, abbreviation, region
        """
        if auto_create_regions:
            def _region_interpreter(row):
                if not row.get('region'):
                    return None
                return {
                    'name': row['region'],
                    'tournament' : self.tournament,
                }
            counts, errors = self._import(f, pm.Region, _region_interpreter, expect_unique=False)
        else:
            counts = None
            errors = None

        interpreter = self.construct_interpreter(
            region=lambda x: pm.Region.objects.get(name=x)
        )

        counts, errors = self._import(f, pm.Institution, interpreter, counts=counts, errors=errors)

        return counts, errors

    def import_venue_groups(self, f):
        """Imports venue groups from a file.
        Each line has:
            name, short_name[, team_capacity]
        """
        return self._import(f, vm.VenueGroup)

    def import_venues(self, f, auto_create_groups=True):
        """Imports venues from a file, also creating venue groups as needed
        (unless 'auto_create_groups' is False).

        Each line has:
            name, priority, venue_group.name
        """

        if auto_create_groups:
            def _venue_group_line_parser(row):
                if not row.get('group'):
                    return None
                return {
                    'name'       : row['group'],
                    'short_name' : row['group'][:25],
                }
            counts, errors = self._import(f, vm.VenueGroup,
                    _venue_group_line_parser, expect_unique=False)
        else:
            counts = None
            errors = None

        interpreter = self.construct_interpreter(
            tournament=self.tournament,
            priority=int,
            group=lambda x: vm.VenueGroup.objects.get(name=x),
        )
        counts, errors = self._import(f, vm.Venue, interpreter, counts=counts, errors=errors)

        return counts, errors

    def import_break_categories(self, f):
        """Imports break categories from a file.

        Each line has:
            name, slug, seq, break_size, is_general, priority, institution_cap
        """

        interpreter = self.construct_interpreter(
            tournament=self.tournament,
            seq=int,
            break_size=int,
            is_general=lambda x: bool(int(x)),
            priority=int,
            institution_cap=int,
        )
        return self._import(f, bm.BreakCategory, interpreter)

    def import_teams(self, f, create_dummy_speakers=False):
        """Imports teams from a file, assigning emoji as needed.
        If 'create_dummy_speakers' is True, also creates dummy speakers."""

        self.initialise_emoji_options()
        def _team_interpreter(row):
            row['tournament'] = self.tournament
            row['institution'] = pm.Institution.objects.lookup(row['institution'])
            row['short_reference'] = row['reference'][:34]
            try:
                row['use_institution_prefix'] = bool(int(row['use_institution_prefix']))
            except ValueError:
                row['use_institution_prefix'] = None
            return row

        counts, errors = self._import(f, pm.Team, _team_interpreter, generated_fields={'emoji': self.get_emoji})

        if create_dummy_speakers:
            def _speakers_interpreter(line):
                team = pm.Teams.objects.get(name=row['reference'], institution=pm.Institution.objects.lookup(row['institution']))
                for name in ["1st Speaker", "2nd Speaker", "3rd Speaker", "Reply Speaker"]:
                    yield dict(name=name, team=team)
            counts, errors = self._import(f, pm.Speaker, _speakers_interpreter, counts=counts, errors=errors)

    def import_speakers(self, f, auto_create_teams=True):
        """Imports speakers from a file, also creating teams as needed (unless
        'auto_create_teams' is False). Institutions are not created as needed;
        if an institution doesn't exist, an error is raised.

        Each line has:
            name, institution_name, team_name, use_team_name_as_prefix, gender,
                    novice_status.
        """

        if auto_create_teams:
            self.initialise_emoji_options()
            def _team_interpreter(row):
                row['tournament'] = self.tournament
                row['institution'] = pm.Institution.objects.lookup(row['institution'])
                row['reference'] = row['team_name']
                row['short_reference'] = row['team_name'][:34]
                try:
                    row['use_institution_prefix'] = bool(int(row['use_institution_prefix']))
                except ValueError:
                    row['use_institution_prefix'] = None
                return row
            def _team_line_parser(line):
                return {
                    'tournament'             : self.tournament,
                    'institution'            : pm.Institution.objects.lookup(line[1]),
                    'reference'              : line[2],
                    'short_reference'        : line[2][:35],
                    'use_institution_prefix' : int(line[3]) if len(line) > 3 and line[3] else 0,
                }
            counts, errors = self._import(f, _team_line_parser, pm.Team, expect_unique=False, generated_fields={'emoji': self.get_emoji})
        else:
            counts = None
            errors = None

        def _speaker_line_parser(line):
            institution = pm.Institution.objects.lookup(line[1])
            return {
                'name'   : line[0],
                'team'   : pm.Team.objects.get(institution=institution,
                                      reference=line[2], tournament=self.tournament),
                'gender' : self._lookup(self.GENDERS, line[4], "gender") if len(line) > 4 and line[4] else None,
                'pronoun': str(line[5]) if len(line) > 5 and line[5] else None,
                'novice' : int(line[6]) if len(line) > 6 and line[6] else False,
            }
        counts, errors = self._import(f, _speaker_line_parser, pm.Speaker, counts=counts, errors=errors)

        return counts, errors

    def import_adjudicators(self, f, auto_conflict=True):
        """Imports adjudicators from a file. Institutions are not created as
        needed; if an institution doesn't exist, an error is raised. Conflicts
        are created from the same file, if present. If 'auto_conflict' is True
        (default), conflicts are created with adjudicators' own institutions.

        Each line has:
            name, institution, rating, gender, independent, novice, cellphone,
                    email, notes, institution_conflicts, team_conflicts
        """
        def _adjudicator_line_parser(line):
            return {
                'name'        : line[0],
                'institution' : pm.Institution.objects.lookup(line[1]),
                'tournament'  : self.tournament,
                'test_score'  : float(line[2]),
                'gender'      : self._lookup(self.GENDERS, line[5], "gender") if len(line) > 5 and line[5] else None,
                'pronoun'     : line[6] if len(line) > 6 else None,
                'independent' : bool(int(line[7])) if len(line) > 7 and line[7] else False,
                'novice'      : int(line[8]) if len(line) > 8 and line[8] else False,
                'phone'       : line[9] if len(line) > 9 else None,
                'email'       : line[10] if len(line) > 10 else None,
                'notes'       : line[11] if len(line) > 11 else None,
            }
        counts, errors = self._import(f, _adjudicator_line_parser, pm.Adjudicator)

        def _test_score_line_parser(line):
            institution = pm.Institution.objects.lookup(line[1])
            return {
                'adjudicator' : pm.Adjudicator.objects.get(name=line[0], institution=institution, tournament=self.tournament),
                'score'       : float(line[2]),
                'round'       : None,
            }
        counts, errors = self._import(f, _test_score_line_parser, fm.AdjudicatorTestScoreHistory,
                counts=counts, errors=errors)

        def _own_institution_conflict_parser(line):
            institution = pm.Institution.objects.lookup(line[1])
            return {
                'adjudicator' : pm.Adjudicator.objects.get(name=line[0], institution=institution, tournament=self.tournament),
                'institution' : institution,
            }
        counts, errors = self._import(f, _own_institution_conflict_parser, am.AdjudicatorInstitutionConflict,
                counts=counts, errors=errors)

        def _institution_conflict_parser(line):
            if len(line) <= 3 or not line[3]:
                return
            adj_inst = pm.Institution.objects.lookup(line[1])
            adjudicator = pm.Adjudicator.objects.get(name=line[0], institution=adj_inst, tournament=self.tournament)
            for institution_name in line[3].split(","):
                institution_name = institution_name.strip()
                institution = pm.Institution.objects.lookup(institution_name)
                yield {
                    'adjudicator' : adjudicator,
                    'institution' : institution,
                }
        counts, errors = self._import(f, _institution_conflict_parser, am.AdjudicatorInstitutionConflict,
                counts=counts, errors=errors)

        def _team_conflict_parser(line):
            if len(line) <= 4 or not line[4]:
                return
            adj_inst = pm.Institution.objects.lookup(line[1])
            adjudicator = pm.Adjudicator.objects.get(name=line[0], institution=adj_inst, tournament=self.tournament)
            for team_name in line[4].split(","):
                team = pm.Team.objects.lookup(team_name)
                yield {
                    'adjudicator' : adjudicator,
                    'team'        : team,
                }
        counts, errors = self._import(f, _team_conflict_parser, am.AdjudicatorConflict,
                counts=counts, errors=errors)

        return counts, errors

    def import_motions(self, f):
        """Imports motions from a file.
        Each line has:
            round, motion_seq, reference, text
        """
        def _motion_line_parser(line):
            return {
                'round'     : tm.Round.objects.lookup(line[0], tournament=self.tournament),
                'seq'       : int(line[1]),
                'reference' : line[2],
                'text'      : line[3],
            }
        return self._import(f, _motion_line_parser, mm.Motion)

    def import_sides(self, f):
        """Imports sides from a file.
        Each line has:
            team_name, side_for_round1, side_for_round2, ...
        """
        def _side_line_parser(line):
            team = pm.Team.objects.lookup(line[0])
            for seq, side in enumerate(line[1:], start=1):
                yield {
                    'round'    : tm.Round.objects.get(seq=seq),
                    'team'     : team,
                    'position' : self._lookup(self.TEAM_POSITIONS, side, "side"),
                }
        return self._import(f, _side_line_parser, dm.TeamPositionAllocation)

    def import_adj_feedback_questions(self, f):
        """Imports adjudicator feedback questions from a file.
        Each line has:
            seq, reference, name, text, answer_type, required, team_on_orallist,
                chair_on_panel, panel_on_chair, panel_on_panel, min_value, max_value
        """
        def _question_line_parser(line):
            return {
                'tournament'             : self.tournament,
                'seq'                    : int(line[0]),
                'reference'              : line[1],
                'name'                   : line[2],
                'text'                   : line[3],
                'answer_type'            : self._lookup(self.FEEDBACK_ANSWER_TYPES, line[4], "answer type"),
                'required'               : bool(int(line[5])),
                'team_on_orallist'       : bool(int(line[6])),
                'chair_on_panellist'     : bool(int(line[7])),
                'panellist_on_chair'     : bool(int(line[8])),
                'panellist_on_panellist' : bool(int(line[9])),
                'min_value'              : int(line[10]) if len(line) > 10 and line[10] else None,
                'max_value'              : int(line[11]) if len(line) > 11 and line[11] else None,
                'choices'                : line[12] if len(line) > 12 else "",
            }
        return self._import(f, _question_line_parser, fm.AdjudicatorFeedbackQuestion)

    def auto_make_rounds(self, num_rounds):
        """Makes the number of rounds specified. The first one is random and the
        rest are all power-paired. The last one is silent. This is intended as a
        convenience function. For anything more complicated, the user should use
        import_rounds() instead."""
        tournaments.utils.auto_make_rounds(self.tournament, num_rounds)
        self.logger.info("Auto-made %d rounds", num_rounds)
