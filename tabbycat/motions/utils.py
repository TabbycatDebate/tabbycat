from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils.translation import gettext as _

from .models import DebateTeamMotionPreference


def merge_motions(new_bs, bses):
    n_motions = bses.aggregate(n_motions=Count('motion', distinct=True))['n_motions']
    if n_motions > 1:
        raise ValidationError(_("Not all latest ballots list the same motion, so could not be merged."))
    elif n_motions == 1:
        new_bs.motion = bses[0].motion


def merge_motion_vetos(new_bs, bses):
    vetos = {}
    pref_lists = [list(bs.debateteammotionpreference_set.all().values_list(
        'debate_team', 'debate_team__side', 'motion', 'preference')) for bs in bses]
    preferences = {p for p in pref_lists}

    if len({p[0] for p in preferences}) != len(preferences):
        # If a team is repeated, means different values were given and the length of both sets would
        # be different. First term could just be "2" (expected to be {'aff', 'neg'}).
        raise ValidationError(_("Motion vetos are inconsistent, so could not be merged."))

    for dt, side, motion, preference in preferences:
        vetos[side] = DebateTeamMotionPreference(
            debate_team_id=dt, motion_id=motion, preference=preference, ballot_submission=new_bs)
    return vetos
