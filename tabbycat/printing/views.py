import json

from django.views.generic.base import TemplateView

from adjfeedback.models import AdjudicatorFeedbackQuestion
from adjfeedback.utils import expected_feedback_targets
from draw.models import Debate
from motions.models import Motion
from participants.models import Adjudicator
from tournaments.mixins import RoundMixin, TournamentMixin
from tournaments.models import Tournament
from utils.mixins import SuperuserRequiredMixin
from venues.models import Venue, VenueGroup


class MasterSheetsListView(SuperuserRequiredMixin, RoundMixin, TemplateView):
    template_name = 'division_sheets_list.html'

    def get_context_data(self, **kwargs):
        kwargs['standings'] = VenueGroup.objects.all()
        kwargs['venue_groups'] = VenueGroup.objects.all()
        return super().get_context_data(**kwargs)


class MasterSheetsView(SuperuserRequiredMixin, RoundMixin, TemplateView):
    template_name = 'master_sheets_view.html'

    def get_context_data(self, **kwargs):
        venue_group_id = self.kwargs['venue_group_id']
        base_venue_group = VenueGroup.objects.get(id=venue_group_id)
        active_tournaments = Tournament.objects.filter(active=True)
        for tournament in list(active_tournaments):
            tournament.debates = Debate.objects.select_related(
                'division', 'division__venue_group', 'round',
                'round__tournament').filter(
                    # All Debates, with a matching round, at the same venue group name
                    round__seq=round.seq,
                    round__tournament=tournament,
                    # Hack - remove when venue groups are unified
                    division__venue_group__short_name=base_venue_group.short_name
            ).order_by('round', 'division__venue_group__short_name', 'division')

        kwargs['base_venue_group'] = base_venue_group
        kwargs['active_tournaments'] = active_tournaments
        return super().get_context_data(**kwargs)


class RoomSheetsView(SuperuserRequiredMixin, RoundMixin, TemplateView):
    template_name = 'room_sheets_view.html'

    def get_context_data(self, **kwargs):
        venue_group_id = self.kwargs['venue_group_id']
        base_venue_group = VenueGroup.objects.get(id=venue_group_id)
        venues = Venue.objects.filter(group=base_venue_group)

        for venue in venues:
            venue.debates = Debate.objects.filter(
                # All Debates, with a matching round, at the same venue group name
                round__seq=round.seq,
                venue=venue
            ).select_related('round__tournament').order_by('round__tournament__seq')

        kwargs['base_venue_group'] = base_venue_group
        kwargs['venues'] = venues
        return super().get_context_data(**kwargs)


class PrintFeedbackFormsView(RoundMixin, SuperuserRequiredMixin, TemplateView):

    template_name = 'feedback_list.html'

    def from_team(self):
        return AdjudicatorFeedbackQuestion.objects.filter(
            tournament=self.get_round().tournament, from_team=True).exists()

    def from_adj(self):
        return AdjudicatorFeedbackQuestion.objects.filter(
            tournament=self.get_round().tournament, from_adj=True).exists()

    def questions_json_dict(self):
        questions = []
        for q in self.get_round().tournament.adj_feedback_questions:
            q_set = {
                'text': q.text, 'seq': q.seq, 'type': q.answer_type,
                'required': json.dumps(q.answer_type),
                'from_team': json.dumps(q.from_team),
                'from_adj': json.dumps(q.from_adj),
            }
            if q.choices:
                q_set['choice_options'] = q.choices.split(AdjudicatorFeedbackQuestion.CHOICE_SEPARATOR)
            elif q.min_value is not None and q.max_value is not None:
                q_set['choice_options'] = q.choices_for_number_scale

            questions.append(q_set)
        return questions

    def construct_info(self, venue, source, source_p, target, target_p):
        source_n = source.name if hasattr(source, 'name') else source.short_name
        return {
            'room': "%s %s" % (venue.name if venue else "", "(" + venue.group.short_name + ")" if venue and venue.group else '', ),
            'authorInstitution': source.institution.code,
            'author': source_n, 'authorPosition': source_p,
            'target': target.name, 'targetPosition': target_p
        }

    def get_context_data(self, **kwargs):
        kwargs['questions'] = self.questions_json_dict()
        kwargs['ballots'] = []

        feedback_paths_option = self.get_tournament().pref('feedback_paths')
        draw = self.get_round().debate_set_with_prefetches(ordering=(
            'venue__group__name', 'venue__name'))

        for debate in draw:
            chair = debate.adjudicators.chair
            if not chair:
                continue

            if self.from_team():
                for team in debate.teams:
                    kwargs['ballots'].append(self.construct_info(
                        debate.venue, team, "Team", chair, ""))

            if self.from_adj():
                debateadjs = debate.debateadjudicator_set.all()
                for debateadj in debateadjs:
                    sadj = debateadj.adjudicator
                    spos = debate.adjudicators.get_position(sadj)
                    targets = expected_feedback_targets(debateadj, feedback_paths=feedback_paths_option,
                            debate=debate)
                    for tadj, tpos in targets:
                        kwargs['ballots'].append(self.construct_info(
                            debate.venue, sadj, spos, tadj, tpos))

        return super().get_context_data(**kwargs)


class PrintScoreSheetsView(RoundMixin, SuperuserRequiredMixin, TemplateView):

    template_name = 'scoresheet_list.html'

    def get_context_data(self, **kwargs):
        kwargs['motions'] = Motion.objects.filter(round=self.get_round()).values('text').order_by('seq')
        kwargs['ballots'] = []

        draw = self.get_round().debate_set_with_prefetches(ordering=(
            'venue__group__name', 'venue__name',))

        for debate in draw:
            debate_info = {
                'room': "%s %s" % (debate.venue.name, "(" + debate.venue.group.short_name + ")" if debate.venue.group else '', ),
                'aff': debate.aff_team.short_name,
                'affEmoji': debate.aff_team.emoji,
                'affSpeakers': [s.name for s in debate.aff_team.speakers],
                'neg': debate.neg_team.short_name,
                'negEmoji': debate.neg_team.emoji,
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
