"""Module to compute the teams breaking in a BreakCategory."""

from collections import Counter


def breaking_teams(category):
    """Returns a list of Teams with annotations.
    'category' must be a BreakCategory instance."""

    teams = category.team_set.all()
    teams = annotate_team_standings(teams)

    break_size = category.break_size
    institution_cap = category.institution_cap

    prev_rank_value = (None, None)
    current_rank = 0
    breaking_teams = list()

    # variables for institutional caps and non-breaking teams
    current_break_rank = 0
    current_break_seq = 0
    teams_from_institution = Counter()

    for i, team in enumerate(teams, start=1):

        # Overall rank
        rank_value = (team.points, team.speaker_score)
        is_new_rank = rank_value != prev_rank_value
        if is_new_rank:
            current_rank = i
            prev_rank_value = rank_value
        team.rank = current_rank

        if institution_cap > 0 and teams_from_institution[team.institution] >= institution_cap:
            if is_new_rank and current_break_rank == break_size:
                break
            team.break_rank = "(capped)"
        else:
            current_break_seq += 1
            if is_new_rank:
                if current_break_rank == break_size:
                    break
                current_break_rank = current_break_seq
                team.break_rank = current_break_rank

        if current_break_rank > break_size:
            break

        # Take note of the institution
        teams_from_institution[team.institution] += 1

        breaking_teams.append(team)

    return breaking_teams