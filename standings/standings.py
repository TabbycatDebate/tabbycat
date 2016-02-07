from django.db.models import Sum
from results.models import TeamScore
import random
from operator import attrgetter
import logging
logger = logging.getLogger(__name__)

# More rules can be added here.
# Valid metrics include any orderable attributes of team, as well as
# 'points', 'speaker_score', 'margins', 'draw_strength' and 'wbw'.
# The 'wbw' (who-beat-whom) metric can be used more than once.
PRECEDENCE_BY_RULE = {
    "australs": ('points', 'speaker_score'),
    "nz"      : ('points', 'wbw', 'speaker_score', 'wbw', 'draw_strength', 'wbw'),
    "wadl"    : ('points', 'wbw', 'margins', 'speaker_score'),
    "test"    : ('points', 'wbw', 'draw_strength', 'wbw', 'speaker_score', 'wbw', 'margins', 'wbw'),
}

def _extract_key_and_wbw(precedence):
    """Given a precedence as in PRECEDENCE_BY_RULE, returns a 2-tuple:
        - A tuple with who-beat-whoms numbered
        - A tuple of attrgetters, each being a key for a who-beat-whom
    For example:
        ('points', 'wbw', 'speaks', 'wbw', 'margins')
    returns:
        (
            ('points', 'wbw1', 'speaks', 'wbw2', 'margins'),
            (attrgetter('points'), attrgetter('points', 'speaks'))
        )
    """
    numbered = list()
    wbw_keys = list()
    counter = 1
    for i, attr in enumerate(precedence):
        if attr == "wbw":
            numbered.append(attr + str(counter))
            wbw_attrs = tuple(attr for attr in precedence[0:i] if attr != "wbw")
            wbw_keys.append(attrgetter(*wbw_attrs))
            counter += 1
        else:
            numbered.append(attr)

    return tuple(numbered), tuple(wbw_keys)

def _add_database_annotations(teams, round):
    """Add those annotations which can be done in an SQL query."""
    from tournaments.models import Round

    # This is what might be more concisely expressed, if it were permissible
    # in Django, as:
    # teams = teams.annotate_if(
    #     dict(points = models.Count('debateteam__teamscore__points'),
    #     speaker_score = models.Count('debateteam__teamscore__score')),
    #     dict(debateteam__teamscore__ballot_submission__confirmed = True)
    # )
    # That is, it adds up all the wins and points of each team on CONFIRMED
    # ballots and adds them as columns to the table it returns.
    # The standings include only preliminary rounds.

    EXTRA_QUERY = """
        SELECT DISTINCT SUM({field:s})
        FROM "results_teamscore"
        JOIN "results_ballotsubmission" ON "results_teamscore"."ballot_submission_id" = "results_ballotsubmission"."id"
        JOIN "draw_debateteam" ON "results_teamscore"."debate_team_id" = "draw_debateteam"."id"
        JOIN "draw_debate" ON "draw_debateteam"."debate_id" = "draw_debate"."id"
        JOIN "tournaments_round" ON "draw_debate"."round_id" = "tournaments_round"."id"
        WHERE "results_ballotsubmission"."confirmed" = True
        AND "draw_debateteam"."team_id" = "participants_team"."id"
        AND "tournaments_round"."stage" = '""" + str(Round.STAGE_PRELIMINARY) + "\'"

    if round is not None:
        EXTRA_QUERY += """AND "tournaments_round"."seq" <= {round:d}""".format(round=round.seq)

    return teams.extra({
        "points": EXTRA_QUERY.format(field="points"),
        "speaker_score": EXTRA_QUERY.format(field="score"),
        "margins": EXTRA_QUERY.format(field="margin"),
    }).distinct()

def _add_draw_strength(teams, round):
    """Adds draw strength. Operates in-place."""
    tournament = teams[0].tournament
    all_teams = _add_database_annotations(tournament.team_set.all(), round)

    for team in teams:
        draw_strength = 0
        # Find all teams that they've faced.
        debateteam_set = team.debateteam_set.all()
        if round is not None:
            debateteam_set = debateteam_set.filter(debate__round__seq__lte=round.seq)
        for dt in debateteam_set:
            # Can't just use dt.opposition.team.points, as dt.opposition.team isn't annotated.
            draw_strength += all_teams.get(id=dt.opposition.team_id).points
        team.draw_strength = draw_strength

def _add_who_beat_whom(teams, round, keys):
    """Adds who beat whom annotations, using each key in keys. For example, if
    there are three tuples in keys, it will add to each team the attributes
    team.wbw1, team.wbw2 and team.wbw3, each being who-beat-whoms based on those
    keys. Operates in-place.
    """

    def who_beat_whom(team, key):
        equal_teams = [x for x in teams if key(x) == key(team)]
        if len(equal_teams) != 2:
            return "n/a" # fail fast if attempt to compare with an int
        equal_teams.remove(team)
        other = equal_teams[0]
        ts = TeamScore.objects.filter(
            ballot_submission__confirmed=True,
            debate_team__team=team,
            debate_team__debate__debateteam__team=other)
        if round is not None:
            ts = ts.filter(debate_team__debate__round__seq__lte=round.seq)
        ts = ts.aggregate(Sum('points'))
        logger.info("who beat whom, {0}{3} vs {1}{4}: {2}".format(team.short_name, other.short_name, ts["points__sum"], key(team), key(other)))
        return ts["points__sum"] or 0

    for team in teams:
        wbws = []
        for i, key in enumerate(keys, start=1):
            wbw = who_beat_whom(team, key)
            setattr(team, "wbw" + str(i), wbw)
            wbws.append(wbw)
        team.who_beat_whom_display = ", ".join(str(wbw) for wbw in wbws)

def _add_ranks(standings, key):
    """Adds the 'rank' attribute to each team in 'standings'. Teams in
    'standings' are assumed to be correctly ordered. 'key' must be a function
    taking a team and returning some metric. Teams are on the same rank if their
    keys are the same."""
    prev_key = None
    current_rank = 0
    for i, team in enumerate(standings, start=1):
        this_key = key(team)
        if this_key != prev_key:
            current_rank = i
            prev_key = this_key
        team.rank = current_rank

def _add_subranks(standings, key, subkey):
    """Adds the 'subrank' attribute to each team in 'standings'. Works as for
    _add_ranks, but ranks reset within each bracket matching 'key', and are
    increased for each change in 'subkey'."""
    prev_key = None
    prev_subkey = None
    current_subrank = 0
    counter = 0

    for team in standings:

        this_key = key(team)
        if this_key != prev_key: # reset subrank
            counter = 1
            prev_key = this_key
            prev_subkey = None

        this_subkey = subkey(team)
        if this_subkey != prev_subkey: # advance subrank
            current_subrank = counter
            prev_subkey = this_subkey

        team.subrank = current_subrank
        counter += 1

    return standings

def _add_division_ranks(standings, divisions):
    """Adds subranks for each division."""
    for division in divisions:
        division_teams = [team for team in standings if team.division == division]
        prev_key = None
        current_rank = 0
        for i, team in enumerate(division_teams, start=1):
            this_key = key(team)
            if this_key != prev_key:
                current_rank = i
                prev_key = this_key
            team.division_rank = current_rank


ANNOTATORS = {
    'draw_strength': _add_draw_strength
}

def annotate_team_standings(teams, round=None, tournament=None, shuffle=False, ranks=False, subranks=False, division_ranks=False):
    """Accepts a QuerySet, returns a list.
    If 'shuffle' is True, it shuffles the list before sorting so that teams that
    are equal are in random order. This should be turned on for draw generation,
    and turned off for display."""

    # Identify tournament
    if round is not None and tournament is None:
        tournament = round.tournament
    if tournament is None:
        raise TypeError("A tournament or a round must be specified.")

    # Identify standings rule
    rule = tournament.pref('team_standings_rule')
    if rule not in PRECEDENCE_BY_RULE:
        raise ValueError("Invalid team_standings_rule option: {0}".format(rule))

    # Add database annotations
    teams = _add_database_annotations(teams, round)

    # HACK for WADL
    # Because this turns teams into a list, you can't use draw_strength and
    # wadl simultaneously.
    if rule == "wadl": # TODO: not sure why this is here
        orig_len = len(teams)
        teams = [t for t in teams if (t.margins != 0 and t.points > 0)]
        print("{} total teams, {} culled teams".format(orig_len, len(teams)))

    precedence, wbw_keys = _extract_key_and_wbw(PRECEDENCE_BY_RULE[rule])

    # Add other annotations and who-beat-whom
    for annotation, annotator in ANNOTATORS.items():
        if annotation in precedence:
            annotator(teams, round)

    if wbw_keys:
        _add_who_beat_whom(teams, round, wbw_keys)

    # Shuffle, so that if teams are truly equal, they'll be in random order
    standings = list(teams)
    if shuffle:
        random.shuffle(standings)

    # Sort!
    try:
        standings.sort(key=attrgetter(*precedence), reverse=True)
    except TypeError:
        print("Unsorted:")
        for team in standings:
            print("{0:20s} {1}".format(team.short_name, attrgetter(*precedence)(team)))
        raise

    print("Sorted:")
    for team in standings:
        print("{0:20s} {1}".format(team.short_name, attrgetter(*precedence)(team)))

    # Add other rank annotations if desired
    if ranks:
        _add_ranks(standings, attrgetter(*precedence))
    if subranks:
        _add_subranks(standings, attrgetter(precedence[0]), attrgetter(*precedence[1:]))
    if division_ranks:
        _add_division_ranks(standings, tournament.division_set.all())

    return standings
