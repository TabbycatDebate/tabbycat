import json

from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView

from adjfeedback.models import AdjudicatorFeedbackQuestion
from adjfeedback.utils import expected_feedback_targets
from draw.models import Debate, DebateTeam
from options.utils import use_team_code_names
from participants.models import Adjudicator
from tournaments.mixins import (CurrentRoundMixin, OptionalAssistantTournamentPageMixin,
                                RoundMixin, TournamentMixin)
from tournaments.models import Tournament
from tournaments.utils import get_side_name
from utils.mixins import AdministratorMixin
from venues.models import VenueCategory


class MasterSheetsListView(AdministratorMixin, RoundMixin, TemplateView):
    template_name = 'division_sheets_list.html'

    def get_context_data(self, **kwargs):
        kwargs['standings'] = VenueCategory.objects.all()
        kwargs['venue_categories'] = VenueCategory.objects.all()
        return super().get_context_data(**kwargs)


class MasterSheetsView(AdministratorMixin, RoundMixin, TemplateView):
    template_name = 'master_sheets_view.html'

    def get_context_data(self, **kwargs):
        venue_category_id = self.kwargs['venue_category_id']
        base_venue_category = VenueCategory.objects.get(id=venue_category_id)
        active_tournaments = Tournament.objects.filter(active=True)
        for tournament in list(active_tournaments):
            tournament.debates = Debate.objects.select_related(
                'division', 'division__venue_category', 'round',
                'round__tournament').filter(
                    # All Debates, with a matching round, at the same venue category name
                    round__seq=self.round.seq,
                    round__tournament=tournament,
                    # Hack - remove when venue category are unified
                    division__venue_category__name=base_venue_category.name
            ).order_by('round', 'division__venue_category__name', 'division')

        kwargs['base_venue_category'] = base_venue_category
        kwargs['active_tournaments'] = active_tournaments
        return super().get_context_data(**kwargs)


class RoomSheetsView(AdministratorMixin, RoundMixin, TemplateView):
    template_name = 'room_sheets_view.html'

    def get_context_data(self, **kwargs):
        venue_category_id = self.kwargs['venue_category_id']
        base_venue_category = VenueCategory.objects.get(id=venue_category_id)
        venues_list = []

        # Get a unique list of venue names (avoid getting duplicates across tournaments)
        for venue in set(base_venue_category.venues.order_by('name').values_list('name', flat=True)):
            venues_list.append({'name': venue, 'debates': []})
            # All Debates, with a matching round, at the same venue category
            venues_list[-1]['debates'] = Debate.objects.filter(
                round__seq=self.round.seq, venue__name=venue).order_by('round__tournament__seq').all()
            print(venues_list[-1])

        kwargs['base_venue_category'] = base_venue_category
        kwargs['venues'] = venues_list
        return super().get_context_data(**kwargs)


class BasePrintFeedbackFormsView(RoundMixin, TemplateView):

    template_name = 'feedback_list.html'

    def add_defaults(self):
        default_questions = []

        if self.tournament.pref('feedback_introduction'):
            default_scale_info = AdjudicatorFeedbackQuestion(
                text=self.tournament.pref('feedback_introduction'), seq=0,
                answer_type='comment', # Custom type just for print display
                required=True, from_team=True, from_adj=True
            )
            default_questions.append(default_scale_info.serialize())

        default_scale_question = AdjudicatorFeedbackQuestion(
            text=_("Overall Score"), seq=0,
            answer_type=AdjudicatorFeedbackQuestion.ANSWER_TYPE_INTEGER_SCALE,
            required=True, from_team=True, from_adj=True,
            min_value=self.tournament.pref('adj_min_score'),
            max_value=self.tournament.pref('adj_max_score')
        )
        default_questions.append(default_scale_question.serialize())

        return default_questions

    def questions_dict(self):
        questions = self.add_defaults()
        for question in self.tournament.adj_feedback_questions:
            questions.append(question.serialize())

        return questions

    def construct_info(self, venue, source, source_p, target, target_p):
        if hasattr(source, 'name'):
            source_n = source.name
        elif use_team_code_names(self.tournament, False):
            source_n = source.code_name
        else:
            source_n = source.short_name

        return {
            'venue': venue.serialize() if venue else '',
            'authorInstitution': source.institution.code if source.institution else _("Unaffiliated"),
            'author': source_n, 'authorPosition': source_p,
            'target': target.name, 'targetPosition': target_p,
        }

    def get_team_feedbacks(self, debate, team):
        if len(debate.adjudicators) is 0:
            return []

        team_paths = self.tournament.pref('feedback_from_teams')
        ballots = []

        if team_paths == 'orallist' and debate.adjudicators.chair:
            ballots.append(self.construct_info(debate.venue, team, _("Team"),
                                               debate.adjudicators.chair, ""))
        elif team_paths == 'all-adjs':
            for target in debate.adjudicators.all():
                ballots.append(self.construct_info(debate.venue, team, _("Team"), target, ""))

        return ballots

    def get_adj_feedbacks(self, debate):
        adj_paths = self.tournament.pref('feedback_paths')
        ballots = []

        debateadjs = debate.debateadjudicator_set.all()
        for debateadj in debateadjs:
            sadj = debateadj.adjudicator
            spos = debate.adjudicators.get_position(sadj)
            targets = expected_feedback_targets(debateadj, feedback_paths=adj_paths, debate=debate)
            for tadj, tpos in targets:
                ballots.append(self.construct_info(debate.venue, sadj, spos, tadj, tpos))

        return ballots

    def get_context_data(self, **kwargs):
        draw = self.round.debate_set_with_prefetches(institutions=True)
        draw = sorted(draw, key=lambda d: d.venue.display_name if d.venue else "")

        ballots = []
        for debate in draw:
            for team in debate.teams:
                ballots.extend(self.get_team_feedbacks(debate, team))
            ballots.extend(self.get_adj_feedbacks(debate))

        kwargs['ballots'] = json.dumps(ballots)
        kwargs['questions'] = json.dumps(self.questions_dict())

        kwargs['team_questions_exist'] = self.tournament.adjudicatorfeedbackquestion_set.filter(from_team=True).exists()
        kwargs['adj_questions_exist'] = self.tournament.adjudicatorfeedbackquestion_set.filter(from_adj=True).exists()

        return super().get_context_data(**kwargs)


class AdminPrintFeedbackFormsView(AdministratorMixin, BasePrintFeedbackFormsView):
    pass


class AssistantPrintFeedbackFormsView(CurrentRoundMixin, OptionalAssistantTournamentPageMixin, BasePrintFeedbackFormsView):
    assistant_page_permissions = ['all_areas', 'results_draw']


class BasePrintScoresheetsView(RoundMixin, TemplateView):

    template_name = 'scoresheet_list.html'

    def get_ballots_dicts(self):
        draw = self.round.debate_set_with_prefetches()
        draw = sorted(draw, key=lambda d: d.venue.display_name if d.venue else "")
        ballots_dicts = []

        for debate in draw:
            debate_dict = {}

            if debate.venue:
                debate_dict['venue'] = {'display_name': debate.venue.display_name}
            else:
                debate_dict['venue'] = None

            debate_dict['debateTeams'] = []
            for side in self.tournament.sides:
                dt_dict = {
                    'side': side,
                    'position': get_side_name(self.tournament, side, 'full'),
                    'abbr': get_side_name(self.tournament, side, 'abbr'),
                }
                try:
                    team = debate.get_team(side)
                    dt_dict['team'] = {
                        'short_name': team.short_name,
                        'code_name': team.code_name,
                        'speakers': [{'name': s.name} for s in team.speakers],
                    }
                except DebateTeam.DoesNotExist:
                    dt_dict['team'] = None
                debate_dict['debateTeams'].append(dt_dict)

            debate_dict['debateAdjudicators'] = []
            for adj, pos in debate.adjudicators.with_positions():
                da_dict = {'position': pos}
                da_dict['adjudicator'] = {
                    'name': adj.name,
                    'institution': {'code': adj.institution.code},
                }
                debate_dict['debateAdjudicators'].append(da_dict)

            if self.round.ballots_per_debate == 'per-adj':
                authors = list(debate.adjudicators.voting_with_positions())
            else:
                authors = [(debate.adjudicators.chair, debate.adjudicators.POSITION_CHAIR)]

            # Add a ballot for each author
            for author, pos in authors:
                ballot_dict = {
                    'author': author.name,
                    'authorInstitution': author.institution.code if author.institution else _("Unaffiliated"),
                    'authorPosition': pos,
                }
                ballot_dict.update(debate_dict)
                ballots_dicts.append(ballot_dict)

            if len(authors) == 0:
                ballot_dict = {
                    'author': "_______________________________________________",
                    'authorInstitution': "",
                    'authorPosition': "",
                }
                ballot_dict.update(debate_dict)
                ballots_dicts.append(ballot_dict)

        return ballots_dicts

    def get_context_data(self, **kwargs):
        kwargs['ballots'] = json.dumps(self.get_ballots_dicts())
        motions = self.round.motion_set.order_by('seq')
        kwargs['motions'] = json.dumps([{'seq': m.seq, 'text': m.text} for m in motions])
        kwargs['use_team_code_names'] = use_team_code_names(self.tournament, False)
        return super().get_context_data(**kwargs)


class AdminPrintScoresheetsView(AdministratorMixin, BasePrintScoresheetsView):
    pass


class AssistantPrintScoresheetsView(CurrentRoundMixin, OptionalAssistantTournamentPageMixin, BasePrintScoresheetsView):
    assistant_page_permissions = ['all_areas']


class PrintableRandomisedURLs(TournamentMixin, AdministratorMixin, TemplateView):

    template_name = 'randomised_url_sheets.html'

    def get_context_data(self, **kwargs):
        kwargs['sheet_type'] = self.sheet_type
        kwargs['tournament_slug'] = self.tournament.slug

        if not self.tournament.pref('share_adjs'):
            kwargs['adjs'] = self.tournament.adjudicator_set.filter(url_key__isnull=False).order_by('institution__name', 'name')
        else:
            kwargs['adjs'] = Adjudicator.objects.filter(url_key__isnull=False).order_by('institution__name', 'name')

        kwargs['exists'] = self.tournament.adjudicator_set.filter(url_key__isnull=False).exists() or \
            self.tournament.team_set.filter(url_key__isnull=False).exists()

        return super().get_context_data(**kwargs)


class PrintFeedbackURLsView(PrintableRandomisedURLs):

    sheet_type = 'feedback'

    def get_context_data(self, **kwargs):
        kwargs['teams'] = self.tournament.team_set.filter(url_key__isnull=False).order_by('institution', 'reference')
        return super().get_context_data(**kwargs)


class PrintBallotURLsView(PrintableRandomisedURLs):

    sheet_type = 'ballot'
