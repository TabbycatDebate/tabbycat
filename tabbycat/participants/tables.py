from django.db.models import Prefetch
from django.utils.translation import gettext as _

from adjallocation.models import DebateAdjudicator
from draw.prefetch import populate_opponents
from results.models import SpeakerScore, TeamScore
from results.prefetch import populate_confirmed_ballots, populate_wins
from standings.templatetags.standingsformat import metricformat
from tournaments.models import Round
from utils.tables import TabbycatTableBuilder


class TeamResultTableBuilder(TabbycatTableBuilder):

    def add_cumulative_team_points_column(self, teamscores):
        """It is assumed that `teamscores` is ordered by round number; the
        caller must ensure that this is the case."""
        cumul = 0
        data = []
        for teamscore in teamscores:
            if teamscore.debate_team.debate.round.is_break_round:
                data.append("—")
            else:
                cumul += teamscore.points * teamscore.debate_team.debate.round.weight
                data.append(cumul)

        if self.tournament.pref('teams_in_debate') == 'bp':
            tooltip = _("Points after this debate")
        else:
            tooltip = _("Wins after this debate")
        header = {'key': 'cumulative', 'tooltip': tooltip, 'icon': 'trending-up'}
        self.add_column(header, data)

    def add_speaker_scores_column(self, teamscores):
        data = [{
            'text': ", ".join([metricformat(ss.score) for ss in ts.debate_team.speaker_scores]) or "—",
            'tooltip': "<br>".join(["%s for %s" % (metricformat(ss.score), ss.speaker) for ss in ts.debate_team.speaker_scores]),
        } for ts in teamscores]
        header = {'key': 'speaks', 'tooltip': _("Speaker scores<br>(in speaking order)"), 'text': _("Speaks")}
        self.add_column(header, data)


class AdjudicatorDebateTable:

    @classmethod
    def get_table(cls, view, participant):
        """On adjudicator record pages, the table is the previous debates table."""
        table = TabbycatTableBuilder(view=view, title=view.table_title, sort_key="round")

        debateadjs = DebateAdjudicator.objects.filter(
            adjudicator=participant,
        ).select_related(
            'debate__round', 'debate__round__tournament',
        ).prefetch_related(
            Prefetch('debate__debateadjudicator_set',
                queryset=DebateAdjudicator.objects.select_related('adjudicator__institution')),
            'debate__debateteam_set__team__speaker_set',
            'debate__round__motion_set',
        )
        if not table.admin and not view.tournament.pref('all_results_released') and not table.private_url:
            debateadjs = debateadjs.filter(
                debate__round__draw_status=Round.STATUS_RELEASED,
                debate__round__silent=False,
                debate__round__completed=True,
            )
        elif table.private_url:
            debateadjs = debateadjs.filter(debate__round__draw_status=Round.STATUS_RELEASED)

        debates = [da.debate for da in debateadjs]
        populate_wins(debates)
        populate_confirmed_ballots(debates, motions=True, results=True)

        table.add_round_column([debate.round for debate in debates])
        table.add_debate_results_columns(debates)
        table.add_debate_adjudicators_column(debates, show_splits=True, highlight_adj=participant)

        if table.admin or view.tournament.pref('public_motions'):
            table.add_debate_motion_column(debates)

        table.add_debate_ballot_link_column(debates)
        return table


class TeamDebateTable:

    @classmethod
    def get_table(cls, view, participant):
        """On team record pages, the table is the results table."""

        table = TeamResultTableBuilder(view=view, title=view.table_title, sort_key="round")

        tournament = view.tournament
        teamscores = TeamScore.objects.filter(
            debate_team__team=participant,
            ballot_submission__confirmed=True,
        ).select_related(
            'debate_team__debate__round__tournament',
        ).prefetch_related(
            Prefetch('debate_team__debate__debateadjudicator_set',
                queryset=DebateAdjudicator.objects.select_related('adjudicator__institution')),
            'debate_team__debate__debateteam_set__team',
            'debate_team__debate__round__motion_set',
            Prefetch('debate_team__speakerscore_set',
                queryset=SpeakerScore.objects.filter(ballot_submission__confirmed=True).select_related('speaker').order_by('position'),
                to_attr='speaker_scores'),
        ).order_by('debate_team__debate__round__seq')

        if not table.admin and not tournament.pref('all_results_released'):
            teamscores = teamscores.filter(
                debate_team__debate__round__draw_status=Round.STATUS_RELEASED,
                debate_team__debate__round__silent=False,
                debate_team__debate__round__completed=True,
            )

        debates = [ts.debate_team.debate for ts in teamscores]
        populate_opponents([ts.debate_team for ts in teamscores])
        populate_confirmed_ballots(debates, motions=True, results=True)

        table.add_round_column([debate.round for debate in debates])
        table.add_debate_result_by_team_column(teamscores)
        table.add_cumulative_team_points_column(teamscores)
        if table.admin or tournament.pref('all_results_released') and tournament.pref('speaker_tab_released') and tournament.pref('speaker_tab_limit') == 0:
            table.add_speaker_scores_column(teamscores)
        table.add_debate_side_by_team_column(teamscores)
        table.add_debate_adjudicators_column(debates, show_splits=True)

        if table.admin or tournament.pref('public_motions'):
            table.add_debate_motion_column(debates)

        if not table.private_url:
            table.add_debate_ballot_link_column(debates)

        return table
