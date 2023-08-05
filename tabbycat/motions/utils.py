from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils.translation import gettext as _

from .models import DebateTeamMotionPreference, RoundMotion


def merge_motions(new_bs, bses):
    n_motions = bses.aggregate(n_motions=Count('motion', distinct=True))['n_motions']
    if n_motions > 1:
        raise ValidationError(_("Not all latest ballots have the same motion. The correct motion must be set manually."))
    elif n_motions == 1:
        new_bs.motion = bses[0].motion


def merge_motion_vetos(new_bs, bses):
    vetos = {}
    pref_lists = [tuple(bs.debateteammotionpreference_set.all().values_list(
        'debate_team', 'debate_team__side', 'motion', 'preference')) for bs in bses]
    preferences = {p for bs in pref_lists for p in bs}

    rms = {}
    for rm in RoundMotion.objects.filter(round_id=new_bs.debate.round_id):
        rms[rm.motion_id] = rm

    if len({p[0] for p in preferences}) != len(preferences):
        # If a team is repeated, means different values were given and the length of both sets would
        # be different. First term could just be "2" (expected to be {'aff', 'neg'}).
        raise ValidationError(_("Motion vetos are inconsistent; they must be set manually."))

    for dt, side, motion, preference in preferences:
        vetos[side] = DebateTeamMotionPreference(
            debate_team_id=dt, motion_id=motion, preference=preference, ballot_submission=new_bs)
        vetos[side]._roundmotion = rms[motion]
    return vetos
