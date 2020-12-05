from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

import adjallocation.models as am
import adjfeedback.models as fm
import availability.models as avm
import breakqual.models as bm
import motions.models as mm
import participants.models as pm
import tournaments.models as tm
import venues.models as vm
from participants.emoji import set_emoji

from .base import BaseTournamentDataImporter, convert_bool, make_interpreter, make_lookup


class BootsTournamentDataImporter(BaseTournamentDataImporter):
    """Boots: Added for British Parliamentary convenience."""

    order = [
        'break_categories',
        'rounds',
        'institutions',
        'speaker_categories',
        'adjudicators',
        'scores',
        'teams',
        'venues',
        'team_conflicts',
        'institution_conflicts',
        'adjudicator_conflicts',
        'team_institution_conflicts',
        'adj_feedback_questions',
        'motions',
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

    def _adj_lookup(self, x):
        return pm.Adjudicator.objects.get(
                Q(tournament=self.tournament) | Q(tournament__isnull=True), name=x)

    def import_rounds(self, f):
        interpreter_part = make_interpreter(
            tournament=self.tournament,
            stage=self.lookup_round_stage,
            draw_type=self.lookup_draw_type,
            break_category=lambda x: bm.BreakCategory.objects.get(slug=x, tournament=self.tournament),
        )

        def interpreter(lineno, line):
            line = interpreter_part(lineno, line)
            if line.get('seq') is None:
                line['seq'] = lineno - 1
            return line

        self._import(f, tm.Round, interpreter)

    def import_institutions(self, f, auto_create_regions=True):
        if auto_create_regions:
            def region_interpreter(lineno, line):
                if line.get('region'):
                    return {'name': line['region']}  # otherwise return None
            self._import(f, pm.Region, region_interpreter, expect_unique=False)

        interpreter = make_interpreter(region=lambda x: pm.Region.objects.get(name=x))
        self._import(f, pm.Institution, interpreter)

    def import_break_categories(self, f):
        interpreter = make_interpreter(tournament=self.tournament)
        self._import(f, bm.BreakCategory, interpreter)

    def import_speaker_categories(self, f):
        interpreter = make_interpreter(tournament=self.tournament)
        self._import(f, pm.SpeakerCategory, interpreter)

    def import_adjudicators(self, f):
        interpreter = make_interpreter(
            institution=pm.Institution.objects.lookup,
            tournament=self.tournament,
            gender=self.lookup_gender,
            DELETE=['category', lambda x: x.startswith('available:')],
        )
        adjudicators = self._import(f, pm.Adjudicator, interpreter)

        def own_institution_conflict_interpreter(lineno, line):
            adjudicator = adjudicators[lineno]
            if adjudicator.institution is not None:
                return {
                    'adjudicator': adjudicator,
                    'institution': adjudicator.institution,
                }
        self._import(f, am.AdjudicatorInstitutionConflict, own_institution_conflict_interpreter)

        content_type = ContentType.objects.get_for_model(pm.Adjudicator)

        def adjudicator_availability_interpreter(lineno, line):
            availability_columns = [col for col in line if col.startswith('available:')]
            for col in availability_columns:
                round_name = col[10:]  # length of 'available:'
                round = tm.Round.objects.lookup(round_name)
                if convert_bool(line[col]):
                    yield {
                        'content_type': content_type,
                        'object_id': adjudicators[lineno].id,
                        'round': round,
                    }

        self._import(f, avm.RoundAvailability, adjudicator_availability_interpreter)

    def import_scores(self, f):
        # The base class can only create instances, it can't update existing ones.
        # To get around this, we create the histories first, and then set the scores
        # on adjudicators.
        interpreter = make_interpreter(
            round=None,
            adjudicator=self._adj_lookup,
        )
        histories = self._import(f, fm.AdjudicatorBaseScoreHistory, interpreter)

        for history in histories.values():
            history.adjudicator.base_score = history.score
            history.adjudicator.save()

    def import_teams(self, f):
        speaker_fields = ['name', 'email', 'category', 'gender']

        team_interpreter_part = make_interpreter(
            tournament=self.tournament,
            institution=pm.Institution.objects.lookup,
            DELETE=['speaker%d_%s' % (i, field) for i in [1, 2] for field in speaker_fields] + ['break_category'],
        )

        def team_interpreter(lineno, line):
            line = team_interpreter_part(lineno, line)
            if not line.get('short_reference'):
                line['short_reference'] = line['reference'][:34]
            return line
        teams = self._import(f, pm.Team, team_interpreter)
        set_emoji(teams.values(), self.tournament)

        def own_team_institution_conflict_interpreter(lineno, line):
            team = teams[lineno]
            if team.institution is not None:
                return {
                    'team': team,
                    'institution': team.institution,
                }
        self._import(f, am.TeamInstitutionConflict, own_team_institution_conflict_interpreter)

        def break_category_interpreter(lineno, line):
            if line.get('break_category'):
                for category in line['break_category'].split('/'):
                    yield {
                        'team': teams[lineno],
                        'breakcategory': self.tournament.breakcategory_set.get(slug=category),
                    }
        self._import(f, pm.Team.break_categories.through, break_category_interpreter)

        def speakers_interpreter(lineno, line):
            for i in [1, 2]:
                subline = {field: line.get('speaker%d_%s' % (i, field)) for field in ['name', 'email', 'gender']}
                subline['gender'] = self.lookup_gender(subline['gender'])
                subline['team'] = teams[lineno]
                yield subline
        speakers = self._import(f, pm.Speaker, speakers_interpreter)

        def speaker_category_interpreter(lineno, line):
            for i in [1, 2]:
                if line.get('speaker%d_category' % i):
                    for category in line['speaker%d_category' % i].split('/'):
                        yield {
                            'speakercategory': self.tournament.speakercategory_set.get(slug=category),
                            'speaker': speakers[(lineno, i)],
                        }
        self._import(f, pm.Speaker.categories.through, speaker_category_interpreter)

    def import_venues(self, f, auto_create_categories=True):
        interpreter = make_interpreter(tournament=self.tournament,
            DELETE=['category', lambda x: x.startswith('available:')])

        venues = self._import(f, vm.Venue, interpreter)

        if auto_create_categories:
            def venue_category_interpreter(lineno, line):
                if not line.get('category'):
                    return None
                return {'name': line['category']}
            self._import(f, vm.VenueCategory, venue_category_interpreter, expect_unique=False)

        def venue_category_venue_interpreter(lineno, line):
            if line.get('category'):
                return {
                    'venuecategory': vm.VenueCategory.objects.get(name=line['category']),
                    'venue': venues[lineno],
                }

        self._import(f, vm.VenueCategory.venues.through, venue_category_venue_interpreter)

        content_type = ContentType.objects.get_for_model(vm.Venue)

        def venue_availability_interpreter(lineno, line):
            availability_columns = [col for col in line if col.startswith('available:')]
            for col in availability_columns:
                round_name = col[10:]  # length of 'available:'
                round = tm.Round.objects.lookup(round_name)
                if convert_bool(line[col]):
                    yield {
                        'content_type': content_type,
                        'object_id': venues[lineno].id,
                        'round': round,
                    }

        self._import(f, avm.RoundAvailability, venue_availability_interpreter)

    def import_team_conflicts(self, f):
        interpreter = make_interpreter(
            team=lambda x: pm.Team.objects.lookup(name=x, tournament=self.tournament),
            adjudicator=self._adj_lookup,
        )
        self._import(f, am.AdjudicatorTeamConflict, interpreter)

    def import_institution_conflicts(self, f):
        interpreter = make_interpreter(
            institution=pm.Institution.objects.lookup,
            adjudicator=self._adj_lookup,
        )
        self._import(f, am.AdjudicatorInstitutionConflict, interpreter)

    def import_adjudicator_conflicts(self, f):
        interpreter = make_interpreter(
            adjudicator1=self._adj_lookup,
            adjudicator2=self._adj_lookup,
        )
        self._import(f, am.AdjudicatorAdjudicatorConflict, interpreter)

    def import_team_institution_conflicts(self, f):
        interpreter = make_interpreter(
            team=lambda x: pm.Team.objects.lookup(name=x, tournament=self.tournament),
            institution=pm.Institution.objects.lookup,
        )
        self._import(f, am.TeamInstitutionConflict, interpreter)

    def import_adj_feedback_questions(self, f):
        interpreter = make_interpreter(
            tournament=self.tournament,
            answer_type=self.lookup_feedback_answer_type,
            choices=lambda c: c.split('//'),
        )

        self._import(f, fm.AdjudicatorFeedbackQuestion, interpreter)

    def import_motions(self, f):
        motions_interpreter = make_interpreter(
            round=lambda x: tm.Round.objects.lookup(x, tournament=self.tournament),
        )
        self._import(f, mm.Motion, motions_interpreter)
