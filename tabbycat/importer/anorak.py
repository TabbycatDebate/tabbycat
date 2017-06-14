from django.contrib.contenttypes.models import ContentType

import adjallocation.models as am
import adjfeedback.models as fm
import breakqual.models as bm
import draw.models as dm
import motions.models as mm
import participants.models as pm
import tournaments.models as tm
import tournaments.utils
import venues.models as vm
from participants.emoji import pick_unused_emoji

from .base import BaseTournamentDataImporter, make_interpreter, make_lookup


class AnorakTournamentDataImporter(BaseTournamentDataImporter):
    """Anorak: The original tournament data format."""

    lookup_round_stage = make_lookup("round stage", {
        ("preliminary", "p"): tm.Round.STAGE_PRELIMINARY,
        ("elimination", "break", "e", "b"): tm.Round.STAGE_ELIMINATION,
    })

    lookup_draw_type = make_lookup("draw type", {
        ("random", "r"): tm.Round.DRAW_RANDOM,
        ("manual", "m"): tm.Round.DRAW_MANUAL,
        ("round robin", "d"): tm.Round.DRAW_ROUNDROBIN,
        ("power paired", "p"): tm.Round.DRAW_POWERPAIRED,
        ("first elimination", "1st elimination", "1e", "f"): tm.Round.DRAW_FIRSTBREAK,
        ("subsequent elimination", "2nd elimination", "2e", "b"): tm.Round.DRAW_BREAK,
    })

    lookup_gender = make_lookup("gender", {
        ("male", "m"): pm.Person.GENDER_MALE,
        ("female", "f"): pm.Person.GENDER_FEMALE,
        ("other", "o"): pm.Person.GENDER_OTHER,
    })

    lookup_team_position = make_lookup("team position", {
        ("affirmative", "aff", "a"): dm.TeamPositionAllocation.POSITION_AFFIRMATIVE,
        ("negative", "neg", "n"): dm.TeamPositionAllocation.POSITION_NEGATIVE,
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
        ("prefix"): vm.VenueCategory.DISPLAY_PREFIX
    })

    def import_rounds(self, f):
        """Imports rounds from a file.
        Each line has:
            seq, name, abbreviation, stage, draw_type, silent, feedback_weight, break_category
        """
        round_interpreter = make_interpreter(
            tournament=self.tournament,
            stage=self.lookup_round_stage,
            draw_type=self.lookup_draw_type,
            break_category=lambda x: bm.BreakCategory.objects.get(
                slug=x, tournament=self.tournament)
        )
        counts, errors = self._import(f, tm.Round, round_interpreter)

        # Set the round with the lowest known seqno to be the current round.
        self.tournament.current_round = self.tournament.round_set.order_by('seq').first()
        self.tournament.save()

        return counts, errors

    def import_regions(self, f):
        """Imports regions from a file.
        Each line has:
            name
        """
        region_interpreter = make_interpreter()
        return self._import(f, pm.Region, region_interpreter)

    def import_institutions(self, f, auto_create_regions=True):
        """Imports institutions from a file, also creating regions as needed
        (unless 'auto_create_regions' is False)
        Each line has:
            name, code, abbreviation, region
        """
        if auto_create_regions:
            def region_interpreter(line):
                if not line.get('region'):
                    return None
                return {
                    'name': line['region']
                }
            counts, errors = self._import(f, pm.Region, region_interpreter,
                                          expect_unique=False)
        else:
            counts = None
            errors = None

        institution_interpreter = make_interpreter(
            region=lambda x: pm.Region.objects.get(name=x)
        )

        counts, errors = self._import(f, pm.Institution, institution_interpreter,
                                      counts=counts, errors=errors)

        return counts, errors

    def import_venues(self, f, auto_create_categories=True):
        """Imports venues from a file, also creating venue categories as needed
        (unless 'auto_create_categories' is False). This function only adds one
        category per venue; use `import_venue_categories` to create further
        categories.

        Each line has:
            name, priority, category
        """

        venue_interpreter = make_interpreter(
            tournament=self.tournament,
            DELETE=['category'],
            category=lambda x: vm.VenueCategory.objects.get(name=x),
        )
        counts, errors = self._import(f, vm.Venue, venue_interpreter)

        if auto_create_categories:
            def venue_category_interpreter(line):
                if not line.get('category'):
                    return None
                return {'name': line['category']}
            counts, errors = self._import(
                    f, vm.VenueCategory, venue_category_interpreter,
                    expect_unique=False, counts=counts, errors=errors)

        def venue_category_venue_interpreter(line):
            if not line.get('category'):
                return None
            return {
                'venuecategory': vm.VenueCategory.objects.get(name=line['category']),
                'venue': vm.Venue.objects.get(name=line['name'])
            }

        counts, errors = self._import(f, vm.VenueCategory.venues.through,
                venue_category_venue_interpreter, counts=counts, errors=errors)

        return counts, errors

    def import_venue_categories(self, f):
        """Imports venue categories from a file.
        Each line has:
            name,display_in_venue_name
        """

        venue_category_interpreter = make_interpreter(
            display_in_venue_name=self.lookup_venue_category_display,
        )

        counts, errors = self._import(f, vm.VenueCategory,
                venue_category_interpreter, expect_unique=False)

        return counts, errors

    def import_break_categories(self, f):
        """Imports break categories from a file.

        Each line has:
            name, slug, seq, break_size, is_general, priority, institution_cap
        """

        break_category_interpreter = make_interpreter(
            tournament=self.tournament,
        )
        return self._import(f, bm.BreakCategory, break_category_interpreter)

    def import_teams(self, f, create_dummy_speakers=False):
        """Imports teams from a file. If 'create_dummy_speakers' is True,
        it also creates dummy speakers."""

        team_interpreter_part = make_interpreter(
            tournament=self.tournament,
            institution=pm.Institution.objects.lookup
        )

        def team_interpreter(line):
            line = team_interpreter_part(line)
            line['short_reference'] = line['reference'][:34]
            return line

        used_emoji = []
        counts, errors = self._import(f, pm.Team, team_interpreter,
                generated_fields={'emoji': (lambda: pick_unused_emoji(used=used_emoji))})

        if create_dummy_speakers:
            def speakers_interpreter(line):
                team = pm.Teams.objects.get(name=line['reference'],
                    institution=pm.Institution.objects.lookup(line['institution']))
                for name in ["1st Speaker", "2nd Speaker", "3rd Speaker", "Reply Speaker"]:
                    yield dict(name=name, team=team)
            counts, errors = self._import(f, pm.Speaker, speakers_interpreter,
                                          counts=counts, errors=errors)

    def import_speakers(self, f, auto_create_teams=True):
        """Imports speakers from a file, also creating teams as needed (unless
        'auto_create_teams' is False). Institutions are not created as needed;
        if an institution doesn't exist, an error is raised.

        Each line has:
            name, institution, team_name, use_team_name_as_prefix, gender,
            pronoun, email, novice_status.
        """

        if auto_create_teams:

            def team_interpreter(line):
                interpreted = {
                    'tournament':  self.tournament,
                    'institution':  pm.Institution.objects.lookup(line['institution']),
                    'reference':  line['team_name'],
                    'short_reference':  line['team_name'][:34],
                }
                if line.get('use_institution_prefix'):
                    interpreted['use_institution_prefix'] = line['use_institution_prefix']
                return interpreted

            used_emoji = []
            counts, errors = self._import(f, pm.Team, team_interpreter, expect_unique=False,
                    generated_fields={'emoji': (lambda: pick_unused_emoji(used=used_emoji))})

        else:
            counts = None
            errors = None

        speaker_interpreter_part = make_interpreter(
            DELETE=['use_institution_prefix', 'institution', 'team_name'],
            gender=self.lookup_gender,
        )

        def speaker_interpreter(line):
            institution = pm.Institution.objects.lookup(line['institution'])
            line['team'] = pm.Team.objects.get(
                institution=institution, reference=line['team_name'], tournament=self.tournament)
            line = speaker_interpreter_part(line)
            return line
        counts, errors = self._import(f, pm.Speaker, speaker_interpreter,
                                      counts=counts, errors=errors)

        return counts, errors

    def import_adjudicators(self, f, auto_conflict=True):
        """Imports adjudicators from a file. Institutions are not created as
        needed; if an institution doesn't exist, an error is raised. Conflicts
        are created from the same file, if present. If 'auto_conflict' is True
        (default), conflicts are created with adjudicators' own institutions.

        Each line has:
            name, institution, rating, gender, independent, novice, cellphone,
            adj_core, email, notes, institution_conflicts, team_conflicts,
            adj_conflicts
        """

        adjudicator_interpreter = make_interpreter(
            institution=pm.Institution.objects.lookup,
            tournament=self.tournament,
            gender=self.lookup_gender,
            DELETE=['team_conflicts', 'institution_conflicts', 'adj_conflicts']
        )
        counts, errors = self._import(f, pm.Adjudicator, adjudicator_interpreter)

        def test_score_interpreter(line):
            institution = pm.Institution.objects.lookup(line['institution'])
            if line['test_score']:
                return {
                    'adjudicator' : pm.Adjudicator.objects.get(name=line['name'], institution=institution, tournament=self.tournament),
                    'score'       : line['test_score'],
                    'round'       : None,
                }
        counts, errors = self._import(f, fm.AdjudicatorTestScoreHistory,
                                      test_score_interpreter, counts=counts,
                                      errors=errors)

        def own_institution_conflict_interpreter(line):
            institution = pm.Institution.objects.lookup(line['institution'])
            return {
                'adjudicator' : pm.Adjudicator.objects.get(name=line['name'], institution=institution, tournament=self.tournament),
                'institution' : institution,
            }
        counts, errors = self._import(f, am.AdjudicatorInstitutionConflict,
                                      own_institution_conflict_interpreter,
                                      counts=counts, errors=errors)

        def institution_conflict_interpreter(line):
            if not line.get('institution_conflicts'):
                return None
            adj_inst = pm.Institution.objects.lookup(line['institution'])
            adjudicator = pm.Adjudicator.objects.get(name=line['name'], institution=adj_inst, tournament=self.tournament)
            for institution_name in line['institution_conflicts'].split(","):
                institution_name = institution_name.strip()
                institution = pm.Institution.objects.lookup(institution_name)
                yield {
                    'adjudicator' : adjudicator,
                    'institution' : institution,
                }
        counts, errors = self._import(f, am.AdjudicatorInstitutionConflict,
                                      institution_conflict_interpreter,
                                      counts=counts, errors=errors)

        def team_conflict_interpreter(line):
            if not line.get('team_conflicts'):
                return
            adj_inst = pm.Institution.objects.lookup(line['institution'])
            adjudicator = pm.Adjudicator.objects.get(name=line['name'],
                institution=adj_inst, tournament=self.tournament)
            for team_name in line['team_conflicts'].split(","):
                team_name = team_name.strip()
                team = pm.Team.objects.lookup(team_name)
                yield {
                    'adjudicator' : adjudicator,
                    'team'        : team,
                }
        counts, errors = self._import(f, am.AdjudicatorConflict,
                                      team_conflict_interpreter,
                                      counts=counts, errors=errors)

        def adj_conflict_interpreter(line):
            if not line.get('adj_conflicts'):
                return
            adj_inst = pm.Institution.objects.lookup(line['institution'])
            adjudicator = pm.Adjudicator.objects.get(name=line['name'],
                institution=adj_inst, tournament=self.tournament)
            for adj_name in line['adj_conflicts'].split(","):
                adj_name = adj_name.strip()
                conflicted_adj = pm.Adjudicator.objects.get(name=adj_name)
                yield {
                    'adjudicator'               : adjudicator,
                    'conflict_adjudicator'      : conflicted_adj,
                }
        counts, errors = self._import(f, am.AdjudicatorAdjudicatorConflict,
                                      adj_conflict_interpreter,
                                      counts=counts, errors=errors)

        return counts, errors

    def import_motions(self, f):
        """Imports motions from a file.
        Each line has:
            round, motion_seq, reference, text
        """
        motions_interpreter = make_interpreter(
            round=lambda x: tm.Round.objects.lookup(x, tournament=self.tournament),
        )
        return self._import(f, mm.Motion, motions_interpreter)

    def import_sides(self, f):
        """Imports sides from a file.
        Each line has:
            team_name, side_for_round1, side_for_round2, ...
        """
        def side_interpreter(line):
            team = pm.Team.objects.lookup(line['team_name'])
            del line['team_name']
            for round_name, side in line.items():
                yield {
                    'round'    : tm.Round.objects.lookup(round_name, tournament=self.tournament),
                    'team'     : team,
                    'position' : self.lookup_team_position(side),
                }
        return self._import(f, dm.TeamPositionAllocation, side_interpreter)

    def import_adj_feedback_questions(self, f):
        """Imports adjudicator feedback questions from a file.
        Each line has:
            seq, reference, name, text, answer_type, required, from_adj, from_team,
                min_value, max_value
        """
        question_interpreter = make_interpreter(
            tournament=self.tournament,
            answer_type=self.lookup_feedback_answer_type,
        )

        return self._import(f, fm.AdjudicatorFeedbackQuestion, question_interpreter)

    def import_adj_venue_constraints(self, f):
        """Imports venue constraints from a file.
        Each line has:
            adjudicator, category, priority
        """
        adj_venue_constraints_interpreter_part = make_interpreter(
            adjudicator=lambda x: pm.Adjudicator.objects.get(name=x),
            category=lambda x: vm.VenueCategory.objects.get(name=x),
        )

        def adj_venue_constraints_interpreter(line):
            line = adj_venue_constraints_interpreter_part(line)
            line['subject_id'] = line['adjudicator'].id
            line['subject_content_type'] = ContentType.objects.get_for_model(pm.Adjudicator)
            del line['adjudicator']
            return line

        return self._import(f, vm.VenueConstraint, adj_venue_constraints_interpreter)

    def import_team_venue_constraints(self, f):
        """Imports venue constraints from a file.
        Each line has:
            team, category, priority
        """
        team_venue_constraints_interpreter_part = make_interpreter(
            team=pm.Team.objects.lookup,
            category=lambda x: vm.VenueCategory.objects.get(name=x),
        )

        def team_venue_constraints_interpreter(line):
            line = team_venue_constraints_interpreter_part(line)
            line['subject_id'] = line['team'].id
            line['subject_content_type'] = ContentType.objects.get_for_model(pm.Team)
            del line['team']
            return line

        return self._import(f, vm.VenueConstraint, team_venue_constraints_interpreter)

    def auto_make_rounds(self, num_rounds):
        """Makes the number of rounds specified. The first one is random and the
        rest are all power-paired. The last one is silent. This is intended as a
        convenience function. For anything more complicated, the user should use
        import_rounds() instead."""
        tournaments.utils.auto_make_rounds(self.tournament, num_rounds)
        self.logger.info("Auto-made %d rounds", num_rounds)
