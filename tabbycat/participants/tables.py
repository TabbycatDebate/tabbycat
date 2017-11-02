from django.utils.translation import ugettext as _

from standings.templatetags.standingsformat import metricformat
from utils.tables import TabbycatTableBuilder


class TeamResultTableBuilder(TabbycatTableBuilder):

    def add_cumulative_team_points_column(self, teamscores):
        cumul = 0
        data = []
        for teamscore in teamscores:
            if teamscore.debate_team.debate.round.is_break_round:
                data.append("—")
            else:
                cumul += teamscore.points
                data.append(cumul)

        header = _("Points after") if self.tournament.pref('teams_in_debate') == 'bp' else _("Wins after")
        self.add_column(header, data)

    def add_speaker_scores_column(self, teamscores):
        """The TeamScores query must have an attribute 'speaker_scores', probably
        populated using:
            Prefetch('debate_team__speakerscore_set',
                queryset=SpeakerScore.objects.filter(ballot_submission__confirmed=True).order_by('position'),
                to_attr='speaker_scores')
        """
        data = [", ".join([metricformat(ss.score) for ss in ts.debate_team.speaker_scores]) or "—"
                for ts in teamscores]
        self.add_column(_("Speaker scores"), data)
