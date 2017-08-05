import json

from django.contrib import messages
from django.views.generic.base import TemplateView

from adjfeedback.models import AdjudicatorFeedbackQuestion
from adjfeedback.utils import expected_feedback_targets
from draw.models import Debate
from participants.models import Adjudicator
from tournaments.mixins import OptionalAssistantTournamentPageMixin, RoundMixin, TournamentMixin
from tournaments.models import Tournament
from utils.mixins import LoginRequiredMixin, SuperuserRequiredMixin
from venues.models import VenueCategory


class MasterSheetsListView(LoginRequiredMixin, RoundMixin, TemplateView):
    template_name = 'division_sheets_list.html'

    def get_context_data(self, **kwargs):
        kwargs['standings'] = VenueCategory.objects.all()
        kwargs['venue_categories'] = VenueCategory.objects.all()
        return super().get_context_data(**kwargs)


class MasterSheetsView(LoginRequiredMixin, RoundMixin, TemplateView):
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
                    round__seq=self.get_round().seq,
                    round__tournament=tournament,
                    # Hack - remove when venue category are unified
                    division__venue_category__name=base_venue_category.name
            ).order_by('round', 'division__venue_category__name', 'division')

        kwargs['base_venue_category'] = base_venue_category
        kwargs['active_tournaments'] = active_tournaments
        return super().get_context_data(**kwargs)


class RoomSheetsView(LoginRequiredMixin, RoundMixin, TemplateView):
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
                round__seq=self.get_round().seq, venue__name=venue).order_by('round__tournament__seq').all()
            print(venues_list[-1])

        kwargs['base_venue_category'] = base_venue_category
        kwargs['venues'] = venues_list
        return super().get_context_data(**kwargs)


class PrintFeedbackFormsView(RoundMixin, OptionalAssistantTournamentPageMixin, TemplateView):

    assistant_page_permissions = ['all_areas', 'results_draw']
    template_name = 'feedback_list.html'

    def has_team_questions(self):
        return AdjudicatorFeedbackQuestion.objects.filter(
            tournament=self.get_round().tournament, from_team=True).exists()

    def has_adj_questions(self):
        return AdjudicatorFeedbackQuestion.objects.filter(
            tournament=self.get_round().tournament, from_adj=True).exists()

    def add_defaults(self):
        t = self.get_tournament()
        default_questions = []

        if t.pref('feedback_introduction'):
            default_scale_info = AdjudicatorFeedbackQuestion(
                text=t.pref('feedback_introduction'), seq=0,
                answer_type='comment', # Custom type just for print display
                required=True, from_team=True, from_adj=True
            )
            default_questions.append(default_scale_info.serialize())

        default_scale_question = AdjudicatorFeedbackQuestion(
            text='Overall Score', seq=0,
            answer_type=AdjudicatorFeedbackQuestion.ANSWER_TYPE_INTEGER_SCALE,
            required=True, from_team=True, from_adj=True,
            min_value=t.pref('adj_min_score'),
            max_value=t.pref('adj_max_score')
        )
        default_questions.append(default_scale_question.serialize())

        return default_questions

    def questions_dict(self):
        questions = self.add_defaults()
        for question in self.get_round().tournament.adj_feedback_questions:
            questions.append(question.serialize())

        return questions

    def construct_info(self, venue, source, source_p, target, target_p):
        source_n = source.name if hasattr(source, 'name') else source.short_name
        return {
            'venue': venue.serialize() if venue else '',
            'authorInstitution': source.institution.code,
            'author': source_n, 'authorPosition': source_p.upper(),
            'target': target.name, 'targetPosition': target_p.upper()
        }

    def get_team_feedbacks(self, debate, team):
        if len(debate.adjudicators) is 0:
            return []

        team_paths = self.get_tournament().pref('feedback_from_teams')
        ballots = []

        if team_paths == 'orallist' and debate.adjudicators.chair:
            ballots.append(self.construct_info(debate.venue, team, "Team",
                                               debate.adjudicators.chair, ""))
        elif team_paths == 'all-adjs':
            for target in debate.debateadjudicator_set.all():
                ballots.append(self.construct_info(debate.venue, team, "Team",
                                                   target.adjudicator, ""))

        return ballots

    def get_adj_feedbacks(self, debate):
        adj_paths = self.get_tournament().pref('feedback_paths')
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
        draw = self.get_round().debate_set_with_prefetches(ordering=('venue__name',))
        # Sort by venue categories to ensure it matches the draw
        draw = sorted(draw, key=lambda d: d.venue.display_name if d.venue else "")
        message = ""
        ballots = []
        if not self.has_team_questions():
            message += "No feedback questions have been added " + \
                       "for teams on adjudicators."
        if not self.has_adj_questions():
            message += "No feedback questions have been added " + \
                       "for adjudicators on adjudicators. "
        if message is not "":
            messages.warning(self.request, message + "Check the " +
                "documentation for information on how to add these" +
                " (otherwise these forms will be quite bare).")

        for debate in draw:
            for team in debate.teams:
                ballots.extend(self.get_team_feedbacks(debate, team))
            ballots.extend(self.get_adj_feedbacks(debate))

        kwargs['ballots'] = json.dumps(ballots)
        kwargs['questions'] = json.dumps(self.questions_dict())
        return super().get_context_data(**kwargs)


class PrintScoreSheetsView(RoundMixin, OptionalAssistantTournamentPageMixin, TemplateView):

    assistant_page_permissions = ['all_areas']
    template_name = 'scoresheet_list.html'

    def get_context_data(self, **kwargs):
        motions = self.get_round().motion_set.order_by('seq')
        draw = self.get_round().debate_set_with_prefetches(ordering=('venue__name',))

        # Sort by venue categories to ensure it matches the draw
        draw = sorted(draw, key=lambda d: d.venue.display_name if d.venue else "")

        ballots = []
        for debate in draw:
            debate_info = debate.serialize()

            if len(debate_info['panel']) is 0:
                ballot_data = {
                    'author': "_______________________________________________",
                    'authorInstitution': "",
                    'authorPosition': "",
                }
                ballot_data.update(debate_info)  # Extend with debateInfo keys
                ballots.append(ballot_data)
            else:
                for adj in (a for a in debate_info['panel'] if a['position'] != "T"):
                    ballot_data = {
                        'author': adj['adjudicator']['name'],
                        'authorInstitution': adj['adjudicator']['institution']['code'],
                        'authorPosition': adj['position'],
                    }
                    ballot_data.update(debate_info)  # Extend with debateInfo keys
                    ballots.append(ballot_data)

        kwargs['ballots'] = json.dumps(ballots)
        kwargs['motions'] = json.dumps([
            {'seq': m.seq, 'text': m.text} for m in motions])
        return super().get_context_data(**kwargs)


class PrintableRandomisedURLs(TournamentMixin, SuperuserRequiredMixin, TemplateView):

    template_name = 'randomised_url_sheets.html'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        kwargs['sheet_type'] = self.sheet_type
        kwargs['tournament_slug'] = tournament.slug

        if not tournament.pref('share_adjs'):
            kwargs['adjs'] = tournament.adjudicator_set.all().order_by('name')
        else:
            kwargs['adjs'] = Adjudicator.objects.all().order_by('name')

        kwargs['exists'] = tournament.adjudicator_set.filter(url_key__isnull=False).exists() or \
            tournament.team_set.filter(url_key__isnull=False).exists()

        return super().get_context_data(**kwargs)


class PrintFeedbackURLsView(PrintableRandomisedURLs):

    sheet_type = 'feedback'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        kwargs['teams'] = tournament.team_set.all().order_by('institution', 'reference')
        return super().get_context_data(**kwargs)


class PrintBallotURLsView(PrintableRandomisedURLs):

    sheet_type = 'ballot'
