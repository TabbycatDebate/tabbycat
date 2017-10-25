from django.db.models import Q

import adjallocation.models as am
import adjfeedback.models as fm
import breakqual.models as bm
import tournaments.models as tm
import participants.models as pm
import venues.models as vm
from participants.emoji import set_emoji

from .base import BaseTournamentDataImporter, make_interpreter, make_lookup


class BootsTournamentDataImporter(BaseTournamentDataImporter):
    """Boots: Added for British Parliamentary convenience."""

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
    ]

    def import_rounds(self, f):
        round_interpreter = make_interpreter(
            tournament=self.tournament,
            stage=self.lookup_round_stage,
            draw_type=self.lookup_draw_type,
            break_category=lambda x: bm.BreakCategory.objects.get(slug=x, tournament=self.tournament)
        )
        self._import(f, tm.Round, round_interpreter)

        # Set the round with the lowest known seqno to be the current round.
        self.tournament.current_round = self.tournament.round_set.order_by('seq').first()
        self.tournament.save()

    def import_institutions(self, f):
        self._import(f, pm.Institution)

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

    def import_scores(self, f):
        # The base class can only create instances, it can't update existing ones.
        # To get around this, we create the histories first, and then set the scores
        # on adjudicators.
        interpreter = make_interpreter(
            round=None,
            adjudicator=lambda x: pm.Adjudicator.objects.get(
                Q(tournament=self.tournament) | Q(tournament__isnull=True), name=x),
        )
        histories = self._import(f, fm.AdjudicatorTestScoreHistory, interpreter)

        for history in histories.values():
            history.adjudicator.test_score = history.score
            history.adjudicator.save()

    def import_teams(self, f):
        speaker_fields = ['name', 'email', 'category', 'gender']

        team_interpreter_part = make_interpreter(
            tournament=self.tournament,
            institution=pm.Institution.objects.lookup,
            DELETE=['speaker%d_%s' % (i, field) for i in [1, 2] for field in speaker_fields] + ['break_category']
        )

        def team_interpreter(lineno, line):
            line = team_interpreter_part(lineno, line)
            if not line.get('short_reference'):
                line['short_reference'] = line['reference'][:34]
            return line
        teams = self._import(f, pm.Team, team_interpreter)
        set_emoji(teams.values(), self.tournament)

        def break_category_interpreter(lineno, line):
            if line.get('break_category'):
                for category in line['break_category'].split('/'):
                    yield {
                        'team': teams[lineno],
                        'breakcategory': self.tournament.breakcategory_set.get(slug=category)
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

    def import_venues(self, f):
        interpreter = make_interpreter(tournament=self.tournament)
        self._import(f, vm.Venue, interpreter)

    def import_team_conflicts(self, f):
        interpreter = make_interpreter(
            team=lambda x: pm.Team.objects.lookup(name=x, tournament=self.tournament),
            adjudicator=lambda x: pm.Adjudicator.objects.get(
                Q(tournament=self.tournament) | Q(tournament__isnull=True), name=x),
        )
        self._import(f, am.AdjudicatorConflict, interpreter)

    def import_institution_conflicts(self, f):
        interpreter = make_interpreter(
            institution=pm.Institution.objects.lookup,
            adjudicator=lambda x: pm.Adjudicator.objects.get(
                Q(tournament=self.tournament) | Q(tournament__isnull=True), name=x),
        )
        self._import(f, am.AdjudicatorInstitutionConflict, interpreter)
