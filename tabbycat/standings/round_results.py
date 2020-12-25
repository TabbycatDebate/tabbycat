import logging

from django.db.models import Prefetch

from draw.models import DebateTeam
from draw.prefetch import populate_opponents
from results.models import SpeakerScore, TeamScore

logger = logging.getLogger(__name__)


def add_team_round_results(standings, rounds, opponents=False, lookup=None, id_attr='instance_id'):
    """Sets, on each item `info` in `standings`, an attribute
    `info.round_results` to be a list of `TeamScore` objects, one for each round
    in `rounds` (in the same order), relating to the team associated with that
    item.

    If, for some team and round, there is no relevant `TeamScore`, then the
    corresponding element of `info.round_results` will be `None`.

    If `lookup` is given, it should be a function that takes two arguments
    `(standings, x)` and returns the element in `standings` relating to the
    `Team` object `x`.  By default, it just uses `standings.get_standings(x)`.
    """

    if lookup is None:
        def lookup(standings, x):
            return standings.get_standing(x)

    team_ids = [getattr(info, id_attr) for info in standings]
    teamscores = TeamScore.objects.select_related(
        'debate_team__team', 'debate_team__debate__round').filter(
        ballot_submission__confirmed=True,
        debate_team__debate__round__in=rounds,
        debate_team__team_id__in=team_ids,
    )

    if opponents:
        populate_opponents([ts.debate_team for ts in teamscores])
    else:
        teamscores = teamscores.prefetch_related(
            Prefetch('debate_team__debate__debateteam_set', queryset=DebateTeam.objects.select_related('team')))

    for info in standings:
        info.round_results = [None] * len(rounds)

    round_lookup = {r: i for i, r in enumerate(rounds)}
    for ts in teamscores:
        info = lookup(standings, ts.debate_team.team)
        info.round_results[round_lookup[ts.debate_team.debate.round]] = ts


def add_team_round_results_public(teams, rounds, opponents=False):
    """Sets, on each item `t` in `teams`, the following attributes:
      - `t.round_results`, a list of `TeamScore` objects, one for each round in
        `rounds` (in the same order), relating to the team `t`.
      - `t.points`, the number of points that team has from the rounds in
        `rounds`.
    """
    add_team_round_results(teams, rounds, opponents=opponents,
        lookup=(lambda teams, x: [t for t in teams if t == x][0]), id_attr='id')
    for team in teams:
        team.points = sum([ts.points for ts in team.round_results if ts and ts.points is not None])


def add_speaker_round_results(standings, rounds, tournament, replies=False):
    """Sets, on each item `info` in `standings`, an attribute `info.scores` to
    be a list of ints, one for each round in `rounds`, each being the score
    received by the speaker associated with `info` in the corresponding round.
    If there is no score available for a speaker and round, the corresponding
    element will be `None`.
    """

    speaker_ids = [info.instance_id for info in standings]
    speaker_scores = SpeakerScore.objects.select_related('speaker',
        'ballot_submission', 'debate_team__debate__round').filter(
        ballot_submission__confirmed=True, debate_team__debate__round__in=rounds,
        speaker_id__in=speaker_ids, ghost=False)

    if replies:
        speaker_scores = speaker_scores.filter(position=tournament.reply_position)
    else:
        speaker_scores = speaker_scores.filter(position__lte=tournament.last_substantive_position)

    for info in standings:
        info.scores = [None] * len(rounds)

    round_lookup = {r: i for i, r in enumerate(rounds)}
    for ss in speaker_scores:
        info = standings.get_standing(ss.speaker)
        info.scores[round_lookup[ss.debate_team.debate.round]] = ss.score
