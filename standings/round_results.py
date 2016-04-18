import itertools
import logging
logger = logging.getLogger(__name__)

from django.db.models.expressions import RawSQL

from results.models import TeamScore
from participants.models import Team
from tournaments.models import Round


def add_team_round_results_0(standings, rounds):

    rankings_str = ", ".join(["({0:d}, {1:d})".format(i, info.instance_id) for i, info in enumerate(standings)])
    rounds_str = ", ".join(["({0:d}, {1:d})".format(i, r.id) for i, r in enumerate(rounds)])

    TEAM_SCORE_QUERY = """
        SELECT results_teamscore.*, opposition.team_id AS opposition_id
        FROM results_teamscore

        JOIN results_ballotsubmission ON results_teamscore.ballot_submission_id = results_ballotsubmission.id
        JOIN draw_debateteam ON draw_debateteam.id = results_teamscore.debate_team_id
        JOIN draw_debate ON draw_debate.id = draw_debateteam.debate_id

        JOIN draw_debateteam AS opposition
            ON  opposition.debate_id = draw_debate.id
            AND opposition.id != draw_debateteam.id

        RIGHT JOIN (VALUES {rankings}) AS team_standings (rank, team_id) ON team_standings.team_id = draw_debateteam.team_id
        RIGHT JOIN (VALUES {rounds}) AS rounds (seq, round_id) ON rounds.round_id = draw_debate.round_id

        WHERE results_ballotsubmission.confirmed = TRUE
        ORDER BY team_standings.rank, rounds.seq
        """.format(rankings=rankings_str, rounds=rounds_str)

    # logger.info(TEAM_SCORE_QUERY)

    teamscores = list(TeamScore.objects.raw(TEAM_SCORE_QUERY))
    oppositions = Team.objects.in_bulk([ts.opposition_id for ts in teamscores])

    for ts in teamscores:
        ts.opposition = oppositions[ts.opposition_id]
        # print("{} in {} against {} {}: {}".format(
        #         ts.debate_team.team.short_name,
        #         ts.debate_team.debate.round.name,
        #         opp.short_name, opp.emoji,
        #         ts.score))

    teamscores_iter = iter(teamscores)
    ts = next(teamscores_iter)
    for info in standings:
        results = []
        for round in rounds:
            if ts.debate_team.team_id == info.instance_id and ts.debate_team.debate.round.seq == round.seq:
                results.append(ts)
                try:
                    ts = next(teamscores_iter)
                except StopIteration:
                    pass
            else:
                results.append(None)
        info.round_results = results
        info.results_in = results[-1] is not None


def add_team_round_results_1(standings, rounds):

    teamscores = TeamScore.objects.select_related('debate_team__team', 'debate_team__debate__round').filter(ballot_submission__confirmed=True)
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
        info = standings.get_standing(ts.debate_team.team)
        info.round_results[round_lookup[ts.debate_team.debate.round]] = ts

    for info in standings:
        info.results_in = info.round_results[-1] is not None


def get_round_result(team, team_scores, r):
    ts = next(
        (x
         for x in team_scores
         if x.debate_team.team == team and x.debate_team.debate.round == r),
        None)
    try:
        ts.opposition = ts.debate_team.opposition.team  # TODO: this slows down the page generation considerably
    except AttributeError:
        pass
    except Exception as e:
        print("Unexpected exception in view.teams.get_round_result")
        print(e)
    return ts

def add_team_round_results_2(standings, rounds):
    team_scores = list(TeamScore.objects.select_related('debate_team__team', 'debate_team__debate__round').filter(ballot_submission__confirmed=True))
    for tsi in standings:
        tsi.round_results = [get_round_result(tsi.team, team_scores, r) for r in rounds]
        tsi.results_in = tsi.round_results[-1] is not None

