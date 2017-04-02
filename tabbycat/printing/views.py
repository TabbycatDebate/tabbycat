import json

from django.contrib import messages
from django.views.generic.base import TemplateView

from adjfeedback.models import AdjudicatorFeedbackQuestion
from adjfeedback.utils import expected_feedback_targets
from draw.models import Debate
from participants.models import Adjudicator
from tournaments.mixins import RoundMixin, TournamentMixin
from tournaments.models import Tournament
from tournaments.utils import get_position_name
from utils.mixins import SuperuserRequiredMixin
from venues.models import Venue, VenueCategory


class MasterSheetsListView(SuperuserRequiredMixin, RoundMixin, TemplateView):
    template_name = 'division_sheets_list.html'

    def get_context_data(self, **kwargs):
        kwargs['standings'] = VenueCategory.objects.all()
        kwargs['venue_categories'] = VenueCategory.objects.all()
        return super().get_context_data(**kwargs)


class MasterSheetsView(SuperuserRequiredMixin, RoundMixin, TemplateView):
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
                    division__venue_category__short_name=base_venue_category.name
            ).order_by('round', 'division__venue_category__short_name', 'division')

        kwargs['base_venue_category'] = base_venue_category
        kwargs['active_tournaments'] = active_tournaments
        return super().get_context_data(**kwargs)


class RoomSheetsView(SuperuserRequiredMixin, RoundMixin, TemplateView):
    template_name = 'room_sheets_view.html'

    def get_context_data(self, **kwargs):
        venue_category_id = self.kwargs['venue_category_id']
        base_venue_category = VenueCategory.objects.get(id=venue_category_id)
        venues = Venue.objects.filter(category=base_venue_category)

        for venue in venues:
            venue.debates = Debate.objects.filter(
                # All Debates, with a matching round, at the same venue category name
                round__seq=round.seq,
            ).select_related('round__tournament').order_by('round__tournament__seq')

        kwargs['base_venue_category'] = base_venue_category
        kwargs['venues'] = venues
        return super().get_context_data(**kwargs)


class PrintFeedbackFormsView(RoundMixin, SuperuserRequiredMixin, TemplateView):

    template_name = 'feedback_list.html'

    def has_team_questions(self):
        return AdjudicatorFeedbackQuestion.objects.filter(
            tournament=self.get_round().tournament, from_team=True).exists()

    def has_adj_questions(self):
        return AdjudicatorFeedbackQuestion.objects.filter(
            tournament=self.get_round().tournament, from_adj=True).exists()

    def question_to_json(self, question):
        qdict = {
            'text': question.text,
            'seq': question.seq,
            'type': question.answer_type,
            'required': json.dumps(question.answer_type),
            'from_team': json.dumps(question.from_team),
            'from_adj': json.dumps(question.from_adj),
        }
        if question.choices:
            qdict['choice_options'] = question.choices.split(AdjudicatorFeedbackQuestion.CHOICE_SEPARATOR)
        elif question.min_value is not None and question.max_value is not None:
            qdict['choice_options'] = question.choices_for_number_scale
        return qdict

    def add_defaults(self):
        t = self.get_tournament()
        default_questions = []

        if t.pref('feedback_introduction'):
            default_scale_info = AdjudicatorFeedbackQuestion(
                text=t.pref('feedback_introduction'), seq=0,
                answer_type='comment', # Custom type just for print display
                required=True, from_team=True, from_adj=True
            )
            default_questions.append(self.question_to_json(default_scale_info))

        default_scale_question = AdjudicatorFeedbackQuestion(
            text='Overall Score', seq=0,
            answer_type=AdjudicatorFeedbackQuestion.ANSWER_TYPE_INTEGER_SCALE,
            required=True, from_team=True, from_adj=True,
            min_value=t.pref('adj_min_score'),
            max_value=t.pref('adj_max_score')
        )
        default_questions.append(self.question_to_json(default_scale_question))

        return default_questions

    def questions_json_dict(self):
        questions = self.add_defaults()
        for question in self.get_round().tournament.adj_feedback_questions:
            questions.append(self.question_to_json(question))

        return questions

    def construct_info(self, venue, source, source_p, target, target_p):
        source_n = source.name if hasattr(source, 'name') else source.short_name
        return {
            'room': venue.display_name if venue else '',
            'authorInstitution': source.institution.code,
            'author': source_n, 'authorPosition': source_p,
            'target': target.name, 'targetPosition': target_p
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
        kwargs['questions'] = self.questions_json_dict()
        kwargs['ballots'] = []

        draw = self.get_round().debate_set_with_prefetches(ordering=('venue__name',))

        message = ""
        if not self.has_team_questions():
            message += "No feedback questions have been added " + \
                       "for teams on adjudicators."
        if not self.has_adj_questions():
            message += "No feedback questions have been added " + \
                       "for adjudicators on adjudicators. "
        if message is not "":
            messages.warning(self.request, message + "Check the " +
                "documentation for information on how to add these.")

        for debate in draw:
            for team in debate.teams:
                kwargs['ballots'].extend(self.get_team_feedbacks(debate, team))

            kwargs['ballots'].extend(self.get_adj_feedbacks(debate))
            pass

        return super().get_context_data(**kwargs)


class PrintScoreSheetsView(RoundMixin, SuperuserRequiredMixin, TemplateView):

    template_name = 'scoresheet_list.html'

    def get_context_data(self, **kwargs):
        motions = self.get_round().motion_set.order_by('seq')
        tournament = self.get_tournament()

        kwargs['motions'] = [{'seq': m.seq, 'text': m.text} for m in motions]
        kwargs['positions'] = [get_position_name(tournament, "aff", "full").title(),
                               get_position_name(tournament, "neg", "full").title()]
        kwargs['ballots'] = []

        draw = self.get_round().debate_set_with_prefetches(ordering=('venue__name',))
        show_emoji = tournament.pref('show_emoji')

        for debate in draw:
            debate_info = {
                'room': debate.venue.display_name if debate.venue else '',
                'aff': debate.aff_team.short_name,
                'affEmoji': debate.aff_team.emoji if debate.aff_team.emoji and show_emoji else '',
                'affSpeakers': [s.name for s in debate.aff_team.speakers],
                'neg': debate.neg_team.short_name,
                'negEmoji': debate.neg_team.emoji if debate.neg_team.emoji and show_emoji else '',
                'negSpeakers': [s.name for s in debate.neg_team.speakers],
                'panel': []
            }
            for adj, position in debate.adjudicators.with_positions():
                debate_info['panel'].append({
                    'name': adj.name,
                    'institution': adj.institution.code,
                    'position': position
                })

            if len(debate_info['panel']) is 0:
                ballot_data = {
                    'author': "_______________________________________________",
                    'authorInstitution': "",
                    'authorPosition': "",
                }
                ballot_data.update(debate_info)  # Extend with debateInfo keys
                kwargs['ballots'].append(ballot_data)
            else:
                for adj in (a for a in debate_info['panel'] if a['position'] != "t"):
                    ballot_data = {
                        'author': adj['name'],
                        'authorInstitution': adj['institution'],
                        'authorPosition': adj['position'],
                    }
                    ballot_data.update(debate_info)  # Extend with debateInfo keys
                    kwargs['ballots'].append(ballot_data)

        return super().get_context_data(**kwargs)


class FeedbackURLsView(TournamentMixin, SuperuserRequiredMixin, TemplateView):

    template_name = 'feedback_url_sheets.html'

    def get_context_data(self, **kwargs):
        tournament = self.get_tournament()
        kwargs['teams'] = tournament.team_set.all().order_by('institution', 'reference')
        if not tournament.pref('share_adjs'):
            kwargs['adjs'] = tournament.adjudicator_set.all().order_by('name')
        else:
            kwargs['adjs'] = Adjudicator.objects.all().order_by('name')
        kwargs['exists'] = tournament.adjudicator_set.filter(url_key__isnull=False).exists() or \
            tournament.team_set.filter(url_key__isnull=False).exists()
        kwargs['tournament_slug'] = tournament.slug
        return super().get_context_data(**kwargs)
