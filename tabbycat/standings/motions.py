from motions.models import DebateTeamMotionPreference
from results.models import TeamScore


# Critical Values / Determination
BALANCES = [
    {'critical': 0.455,  'label': '50% (balanced)',             'freedom': .5},
    {'critical': 2.706,  'label': '90% likely TEAM favoured ',  'freedom': .1},
    {'critical': 3.841,  'label': '95% likely TEAM favoured',   'freedom': .05},
    {'critical': 5.412,  'label': '98% likely TEAM favoured',   'freedom': .02},
    {'critical': 6.635,  'label': '99% likely TEAM favoured',   'freedom': .01},
    # The last value is large enough to be a catch-all; ie over 99.9% confidence
    {'critical': 1000.0, 'label': '99.9% likely TEAM favoured', 'freedom': .001},
]


# Calculate points per position and debate
def gather_motion_stats(motions, rounds, tournament):

    results = TeamScore.objects.filter(
        ballot_submission__confirmed=True,
        ballot_submission__debate__round__in=rounds).select_related('debate_team',
            'ballot_submission__debate__round', 'ballot_submission__motion')

    # Create a dictionary organising results by motion, side, and points won
    placings = dict.fromkeys(motions, {})
    chosen = dict.fromkeys(motions, {})

    for motion, places in placings.items():
        chosen[motion] = 0
        placings[motion] = {}
        for side in tournament.sides:
            placings[motion][side] = {3: 0, 2: 0, 1: 0, 0: 0}

    # Populate dictionary
    for result in results:
        motion = None # Default
        if tournament.pref('enable_motions'):
            motion = result.ballot_submission.motion # Motion Selection
        else:
            result_round = result.ballot_submission.debate.round # BP
            motion = next((m for m in motions if m.round == result_round), None)

        if motion:
            chosen[motion] += 1
            placings[motion][result.debate_team.side][result.points] += 1

    if tournament.pref('motion_vetoes_enabled'):
        # Create dictionary to track vetoes per-side
        vetoes = dict.fromkeys(motions, {})
        for motion_key in vetoes.keys():
            vetoes[motion_key] = dict.fromkeys(tournament.sides, 0)

        veto_objs = DebateTeamMotionPreference.objects.filter(
            preference=3,
            ballot_submission__confirmed=True,
            ballot_submission__debate__round__in=rounds).select_related(
            'debate_team', 'ballot_submission__motion')
        for veto in veto_objs:
            vetoes[veto.motion][veto.debate_team.side] += 1
    else:
        vetoes = False

    for motion in motions:
        setattr(motion, 'placings', placings[motion])
        setattr(motion, 'chosen', chosen[motion])
        round_totals = [c for m, c in chosen.items() if m.round == motion.round]
        if tournament.pref('teams_in_debate') is 'two':
            setattr(motion, 'round_total', sum(round_totals) / 2)
        else:
            setattr(motion, 'round_total', sum(round_totals) / 4)
        if vetoes:
            setattr(motion, 'vetoes', vetoes[motion])

    return motions


def get_motion_balance(results_for_motion, chosen_count, for_vetoes=False):
    inconclusive = 'Too few vetoes to determine meaningful balance'

    if chosen_count < 10: # Too few wins/vetoes to calculate
        return 'inconclusive', inconclusive

    if len(results_for_motion) == 2:
        return two_team_balance(results_for_motion, chosen_count, for_vetoes)
    else:
        return four_team_balance(results_for_motion, chosen_count)


def two_team_balance(results_for_motion, chosen_count, for_vetoes):
    # Test and confidence levels contributed by Viran Weerasekera
    if for_vetoes:
        print(results_for_motion)
    if for_vetoes:
        affs = results_for_motion['aff']
        negs = results_for_motion['neg']
        n_2 = int((affs + negs) / 2)
    else:
        affs = results_for_motion['aff'][1]
        negs = results_for_motion['neg'][1]
        n_2 = int(chosen_count / 2)

    aff_c_stat = pow(affs - n_2, 2) / n_2
    neg_c_stat = pow(negs - n_2, 2) / n_2
    c_stat = round(aff_c_stat + neg_c_stat, 2)

    print('\tc_stat', c_stat)
    threshold = next((ir for ir in BALANCES if c_stat <= ir['critical']), None)

    info = "%s critical value; %s level of signficance" % (c_stat, threshold['freedom'])

    if affs > negs:
        return threshold['label'].replace('TEAM', 'aff'), info
    elif affs < negs:
        return threshold['label'].replace('TEAM', 'neg'), info
    else:
        return threshold['label'], info


def four_team_balance(results_for_motion, chosen_count):
    return None, None
