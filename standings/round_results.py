import itertools
import logging
logger = logging.getLogger(__name__)

from django.db.models.expressions import RawSQL

from results.models import TeamScore, SpeakerScore
from participants.models import Team
from tournaments.models import Round

def add_team_round_results(standings, rounds, lookup=None):

    if lookup is None:
        lookup = lambda standings, x: standings.get_standing(x)

    teamscores = TeamScore.objects.select_related(
            'debate_team__team', 'debate_team__debate__round').filter(
            ballot_submission__confirmed=True, debate_team__debate__round__in=rounds)
    teamscores = teamscores.annotate(opposition_id=RawSQL("""
        SELECT opposition.team_id
        FROM draw_debateteam AS opposition
        WHERE opposition.debate_id = draw_debateteam.debate_id
        AND opposition.id != draw_debateteam.id""", ()
    ))
    teamscores = list(teamscores)
    oppositions = Team.objects.in_bulk([ts.opposition_id for ts in teamscores])

    for info in standings:
        info.round_results = [None] * len(rounds)

    round_lookup = {r: i for i, r in enumerate(rounds)}
    for ts in teamscores:
        ts.opposition = oppositions[ts.opposition_id]
        info = lookup(standings, ts.debate_team.team)
        info.round_results[round_lookup[ts.debate_team.debate.round]] = ts

    for info in standings:
        info.results_in = info.round_results[-1] is not None

def add_team_round_results_public(teams, rounds):
    add_team_round_results(teams, rounds, (lambda teams, x: [t for t in teams if t == x][0]))
    for team in teams:
        team.wins = [ts.win for ts in team.round_results if ts].count(True)
        team.points = sum([ts.points for ts in team.round_results if ts])


def add_speaker_round_results(standings, rounds, tournament, replies=False):
    speaker_scores = SpeakerScore.objects.select_related(
            'speaker', 'ballot_submission', 'debate_team__debate__round').filter(
            ballot_submission__confirmed=True)

    if replies:
        speaker_scores = speaker_scores.filter(position=tournament.REPLY_POSITION)
    else:
        speaker_scores = speaker_scores.filter(position__lte=tournament.LAST_SUBSTANTIVE_POSITION)

    for info in standings:
        info.scores = [None] * len(rounds)

    round_lookup = {r: i for i, r in enumerate(rounds)}
    for ss in speaker_scores:
        info = standings.get_standing(ss.speaker)
        info.scores[round_lookup[ss.debate_team.debate.round]] = ss.score

    for info in standings:
        info.results_in = info.scores[-1] is not None
