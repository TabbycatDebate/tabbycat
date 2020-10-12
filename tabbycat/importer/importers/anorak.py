from django.contrib.contenttypes.models import ContentType

import adjallocation.models as am
import adjfeedback.models as fm
import breakqual.models as bm
import draw.models as dm
import motions.models as mm
import participants.models as pm
import tournaments.models as tm
import venues.models as vm
from participants.emoji import set_emoji

from .base import BaseTournamentDataImporter, make_interpreter, make_lookup


class AnorakTournamentDataImporter(BaseTournamentDataImporter):
    """Anorak: The original tournament data format."""

    order = [
        'venue_categories',
        'venues',
        'regions',
        'institutions',
        'break_categories',
        'teams',
        'speakers',
        'adjudicators',
        'rounds',
        'motions',
        'sides',
        'adj_feedback_questions',
        'adj_venue_constraints',
        'team_venue_constraints',
    ]

    lookup_round_stage = make_lookup("round stage", {
        ("preliminary", "p"): tm.Round.STAGE_PRELIMINARY,
        ("elimination", "break", "e", "b"): tm.Round.STAGE_ELIMINATION,
    })

    lookup_draw_type = make_lookup("draw type", {
        ("random", "r"): tm.Round.DRAW_RANDOM,
        ("manual", "m"): tm.Round.DRAW_MANUAL,
        ("round robin", "d"): tm.Round.DRAW_ROUNDROBIN,
        ("power paired", "p"): tm.Round.DRAW_POWERPAIRED,
        ("elimination", "break", "e", "b"): tm.Round.DRAW_ELIMINATION,
    })

    lookup_gender = make_lookup("gender", {
        ("male", "m"): pm.Person.GENDER_MALE,
        ("female", "f"): pm.Person.GENDER_FEMALE,
        ("other", "o"): pm.Person.GENDER_OTHER,
    })

    lookup_team_position = make_lookup("team position", {
        ("affirmative", "aff", "a"): dm.DebateTeam.SIDE_AFF,
        ("negative", "neg", "n"): dm.DebateTeam.SIDE_NEG,
    })

    lookup_feedback_answer_type = make_lookup("feedback answer type", {
        ("checkbox"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_BOOLEAN_CHECKBOX,
        ("yes no select", "yesno"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_BOOLEAN_SELECT,
        ("integer textbox", "int", "integer"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_INTEGER_TEXTBOX,
        ("integer scale", "scale"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_INTEGER_SCALE,
        ("float"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_FLOAT,
        ("text"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_TEXT,
        ("textbox", "long text", "longtext"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_LONGTEXT,
        ("select single", "single select"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_SINGLE_SELECT,
        ("select multiple", "multiple select"): fm.AdjudicatorFeedbackQuestion.ANSWER_TYPE_MULTIPLE_SELECT,
    })

    lookup_venue_category_display = make_lookup("venue category display", {
        (""): vm.VenueCategory.DISPLAY_SUFFIX,
        ("suffix"): vm.VenueCategory.DISPLAY_SUFFIX,
        ("prefix"): vm.VenueCategory.DISPLAY_PREFIX,
    })

    def import_rounds(self, f):
        round_interpreter_part = make_interpreter(
            tournament=self.tournament,
            stage=self.lookup_round_stage,
            draw_type=self.lookup_draw_type,
            break_category=lambda x: bm.BreakCategory.objects.get(slug=x, tournament=self.tournament),
        )

        def round_interpreter(lineno, line):
            line = round_interpreter_part(lineno, line)
            if line.get('seq') is None:
                line['seq'] = lineno - 1
            return line

        self._import(f, tm.Round, round_interpreter)

    def import_regions(self, f):
        region_interpreter = make_interpreter()
        self._import(f, pm.Region, region_interpreter)

    def import_institutions(self, f, auto_create_regions=True):
        """Imports institutions, also creating regions as needed unless
        'auto_create_regions' is False."""

        if auto_create_regions:
            def region_interpreter(lineno, line):
                if not line.get('region'):
                    return None
                return {
                    'name': line['region'],
                }
            self._import(f, pm.Region, region_interpreter, expect_unique=False)

        institution_interpreter = make_interpreter(
            region=lambda x: pm.Region.objects.get(name=x),
        )

        self._import(f, pm.Institution, institution_interpreter)

    def import_venues(self, f, auto_create_categories=True):
        """Imports venues, also creating venue categories as needed unless
        'auto_create_categories' is False. This function only adds one category
        per venue; use `import_venue_categories` to create further categories.
        """

        venue_interpreter = make_interpreter(
            tournament=self.tournament,
            DELETE=['category'],
            category=lambda x: vm.VenueCategory.objects.get(name=x),
        )
        self._import(f, vm.Venue, venue_interpreter)

        if auto_create_categories:
            def venue_category_interpreter(lineno, line):
                if not line.get('category'):
                    return None
                return {'tournament': self.tournament, 'name': line['category']}
            self._import(f, vm.VenueCategory, venue_category_interpreter, expect_unique=False)

        def venue_category_venue_interpreter(lineno, line):
            if not line.get('category'):
                return None
            return {
                'venuecategory': vm.VenueCategory.objects.get(name=line['category']),
                'venue': self.tournament.venue_set.get(name=line['name']),
            }

        self._import(f, vm.VenueCategory.venues.through, venue_category_venue_interpreter)

    def import_venue_categories(self, f):
        venue_category_interpreter = make_interpreter(
            tournament=self.tournament,
            display_in_venue_name=self.lookup_venue_category_display,
        )

        self._import(f, vm.VenueCategory, venue_category_interpreter, expect_unique=False)

    def import_break_categories(self, f):
        break_category_interpreter = make_interpreter(
            tournament=self.tournament,
        )
        self._import(f, bm.BreakCategory, break_category_interpreter)

    def import_teams(self, f, create_dummy_speakers=False):
        """Imports teams. If 'create_dummy_speakers' is True, it also creates
        dummy speakers."""

        team_interpreter_part = make_interpreter(
            tournament=self.tournament,
            institution=pm.Institution.objects.lookup,
        )

        def team_interpreter(lineno, line):
            line = team_interpreter_part(lineno, line)
            line['short_reference'] = line['reference'][:34]
            return line

        teams = self._import(f, pm.Team, team_interpreter)
        set_emoji(teams.values(), self.tournament)

        if create_dummy_speakers:
            def speakers_interpreter(lineno, line):
                team = teams[lineno]
                for name in ["1st Speaker", "2nd Speaker", "3rd Speaker", "Reply Speaker"]:
                    yield dict(name=name, team=team)
            self._import(f, pm.Speaker, speakers_interpreter)

        def own_team_institution_conflict_interpreter(lineno, line):
            team = teams[lineno]
            if team.institution is not None:
                return {
                    'team': team,
                    'institution': team.institution,
                }
        self._import(f, am.TeamInstitutionConflict, own_team_institution_conflict_interpreter)

    def import_speakers(self, f, auto_create_teams=True):
        """Imports speakers, also creating teams as needed (unless
        'auto_create_teams' is False). Institutions are not created as needed;
        if an institution doesn't exist, an error is raised.
        """

        if auto_create_teams:

            def team_interpreter(lineno, line):
                interpreted = {
                    'tournament': self.tournament,
                    'reference': line['team_name'],
                    'short_reference':  line['team_name'][:34],
                }
                if line.get('institution'):
                    interpreted['institution'] = pm.Institution.objects.lookup(line['institution'])
                if line.get('use_institution_prefix'):
                    interpreted['use_institution_prefix'] = line['use_institution_prefix']
                return interpreted

            teams = self._import(f, pm.Team, team_interpreter, expect_unique=False)
            set_emoji(teams.values(), self.tournament)

            def own_team_institution_conflict_interpreter(lineno, line):
                team = teams.get(lineno)
                if team is not None and team.institution is not None:
                    return {
                        'team': team,
                        'institution': team.institution,
                    }
            self._import(f, am.TeamInstitutionConflict, own_team_institution_conflict_interpreter)

        speaker_interpreter_part = make_interpreter(
            DELETE=['use_institution_prefix', 'institution', 'team_name'],
            gender=self.lookup_gender,
        )

        def speaker_interpreter(lineno, line):
            institution = pm.Institution.objects.lookup(line['institution']) if line.get('institution') else None
            line['team'] = pm.Team.objects.get(
                institution=institution, reference=line['team_name'], tournament=self.tournament)
            line = speaker_interpreter_part(lineno, line)
            return line
        self._import(f, pm.Speaker, speaker_interpreter)

    def import_adjudicators(self, f, auto_conflict=True):
        """Imports adjudicators. Institutions are not created as needed; if an
        institution doesn't exist, an error is raised. Conflicts are created
        from the same file, if present. If 'auto_conflict' is True (default),
        conflicts are created with adjudicators' own institutions.
        """

        adjudicator_interpreter = make_interpreter(
            institution=pm.Institution.objects.lookup,
            tournament=self.tournament,
            gender=self.lookup_gender,
            DELETE=['team_conflicts', 'institution_conflicts', 'adj_conflicts'],
        )
        adjudicators = self._import(f, pm.Adjudicator, adjudicator_interpreter)

        def base_score_interpreter(lineno, line):
            adjudicator = adjudicators[lineno]
            if line['base_score']:
                return {
                    'adjudicator' : adjudicator,
                    'score'       : line['base_score'],
                    'round'       : None,
                }
        self._import(f, fm.AdjudicatorBaseScoreHistory, base_score_interpreter)

        def own_institution_conflict_interpreter(lineno, line):
            adjudicator = adjudicators[lineno]
            if adjudicator.institution is not None:
                return {
                    'adjudicator': adjudicator,
                    'institution': adjudicator.institution,
                }
        self._import(f, am.AdjudicatorInstitutionConflict, own_institution_conflict_interpreter)

        def institution_conflict_interpreter(lineno, line):
            if not line.get('institution_conflicts'):
                return None
            adjudicator = adjudicators[lineno]
            for institution_name in line['institution_conflicts'].split(","):
                institution_name = institution_name.strip()
                institution = pm.Institution.objects.lookup(institution_name)
                yield {
                    'adjudicator' : adjudicator,
                    'institution' : institution,
                }
        self._import(f, am.AdjudicatorInstitutionConflict, institution_conflict_interpreter)

        def team_conflict_interpreter(lineno, line):
            if not line.get('team_conflicts'):
                return
            adjudicator = adjudicators[lineno]
            for team_name in line['team_conflicts'].split(","):
                team_name = team_name.strip()
                team = pm.Team.objects.lookup(team_name)
                yield {
                    'adjudicator' : adjudicator,
                    'team'        : team,
                }
        self._import(f, am.AdjudicatorTeamConflict, team_conflict_interpreter)

        def adj_conflict_interpreter(lineno, line):
            if not line.get('adj_conflicts'):
                return
            adjudicator = adjudicators[lineno]
            for adj_name in line['adj_conflicts'].split(","):
                adj_name = adj_name.strip()
                conflicted_adj = pm.Adjudicator.objects.get(name=adj_name)
                yield {
                    'adjudicator1' : adjudicator,
                    'adjudicator2' : conflicted_adj,
                }
        self._import(f, am.AdjudicatorAdjudicatorConflict, adj_conflict_interpreter)

    def import_motions(self, f):
        motions_interpreter = make_interpreter(
            round=lambda x: tm.Round.objects.lookup(x, tournament=self.tournament),
        )
        self._import(f, mm.Motion, motions_interpreter)

    def import_sides(self, f):
        def side_interpreter(lineno, line):
            team = pm.Team.objects.lookup(line['team_name'])
            del line['team_name']
            for round_name, side in line.items():
                yield {
                    'round'    : tm.Round.objects.lookup(round_name, tournament=self.tournament),
                    'team'     : team,
                    'position' : self.lookup_team_position(side),
                }
        self._import(f, dm.TeamSideAllocation, side_interpreter)

    def import_adj_feedback_questions(self, f):
        question_interpreter = make_interpreter(
            tournament=self.tournament,
            answer_type=self.lookup_feedback_answer_type,
            choices=lambda c: c.split('//'),
        )

        self._import(f, fm.AdjudicatorFeedbackQuestion, question_interpreter)

    def import_adj_venue_constraints(self, f):
        adj_venue_constraints_interpreter_part = make_interpreter(
            adjudicator=lambda x: pm.Adjudicator.objects.get(name=x),
            category=lambda x: vm.VenueCategory.objects.get(name=x),
        )

        def adj_venue_constraints_interpreter(lineno, line):
            line = adj_venue_constraints_interpreter_part(lineno, line)
            line['subject_id'] = line['adjudicator'].id
            line['subject_content_type'] = ContentType.objects.get_for_model(pm.Adjudicator)
            del line['adjudicator']
            return line

        self._import(f, vm.VenueConstraint, adj_venue_constraints_interpreter)

    def import_team_venue_constraints(self, f):
        team_venue_constraints_interpreter_part = make_interpreter(
            team=pm.Team.objects.lookup,
            category=lambda x: vm.VenueCategory.objects.get(name=x),
        )

        def team_venue_constraints_interpreter(lineno, line):
            line = team_venue_constraints_interpreter_part(lineno, line)
            line['subject_id'] = line['team'].id
            line['subject_content_type'] = ContentType.objects.get_for_model(pm.Team)
            del line['team']
            return line

        self._import(f, vm.VenueConstraint, team_venue_constraints_interpreter)
