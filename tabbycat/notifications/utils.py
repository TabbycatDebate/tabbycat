"""Email generator functions

These functions assemble the necessary arguments to be parsed in email templates
to be sent to relevant parties. All these functions return a tuple with the first
element being a context dictionary with the available variables to be parsed in
the message. The second element is the Person object. All these functions are
called by NotificationQueueConsumer, which inserts the variables into a message,
using the participant object to fetch their email address and to record.

Objects should be fetched from the database here as it is an asyncronous process,
thus the object itself cannot be passed.
"""
from dataclasses import dataclass
from typing import Any, List, Protocol, Set, Tuple, TYPE_CHECKING

from django.utils import formats
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from adjallocation.allocation import AdjudicatorAllocation
from options.utils import use_team_code_names
from participants.prefetch import populate_win_counts
from results.result import ConsensusDebateResultWithScores, DebateResult, DebateResultByAdjudicatorWithScores
from results.utils import side_and_position_names

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from participants.models import Person
    from tournaments.models import Round, Tournament
    from draw.models import Debate


adj_position_names = {
    AdjudicatorAllocation.POSITION_CHAIR: _("the chair"),
    AdjudicatorAllocation.POSITION_ONLY: _("the only"),
    AdjudicatorAllocation.POSITION_PANELLIST: _("a panellist"),
    AdjudicatorAllocation.POSITION_TRAINEE: _("a trainee"),
}


@dataclass
class EmailContextData:
    USER: str


@dataclass
class AdjudicatorAssignmentContext(EmailContextData):
    ROUND: str
    VENUE: str
    PANEL: str
    DRAW: str
    POSITION: str
    URL: str


@dataclass
class RandomizedUrlContext(EmailContextData):
    KEY: str
    TOURN: str
    URL: str


@dataclass
class BallotsContext(EmailContextData):
    DEBATE: str
    SCORES: str


@dataclass
class StandingsContext(EmailContextData):
    TOURN: str
    ROUND: str
    URL: str
    POINTS: str
    TEAM: str


@dataclass
class MotionReleaseContext(EmailContextData):
    TOURN: str
    ROUND: str
    MOTIONS: str


@dataclass
class TeamSpeakerContext(EmailContextData):
    TOURN: str
    SHORT: str
    LONG: str
    CODE: str
    BREAK: str
    SPEAKERS: str
    INSTITUTION: str
    EMOJI: str


@dataclass
class TeamDrawContext(EmailContextData):
    ROUND: str
    VENUE: str
    PANEL: str
    DRAW: str
    TEAM: str
    SIDE: str


def _assemble_panel(adjs: List[Tuple['Person', str]]) -> str:
    adj_string = []
    for adj, pos in adjs:
        adj_string.append("%s (%s)" % (adj.name, adj_position_names[pos]))

    return ", ".join(adj_string)


def _check_in_to(pk: int, to_ids: Set[int]) -> bool:
    try:
        to_ids.remove(pk)
    except KeyError:
        return False
    return True


class NotificationContextGenerator(Protocol):
    def __call__(self, to: 'QuerySet[Person]', *args: Any) -> List[Tuple[EmailContextData, 'Person']]:
        return [(EmailContextData(USER=person.name), person) for person in to]


class AdjudicatorAssignmentEmailGenerator(NotificationContextGenerator):
    def __call__(self, to: 'QuerySet[Person]', url: str, round: 'Round') -> List[Tuple[AdjudicatorAssignmentContext, 'Person']]:
        emails = []
        to_ids = {p.id for p in to}
        draw = round.debate_set_with_prefetches(speakers=False).filter(debateadjudicator__adjudicator__in=to)
        use_codes = use_team_code_names(round.tournament, False)

        for debate in draw:
            for adj, pos in debate.adjudicators.with_positions():
                if not _check_in_to(adj.id, to_ids):
                    continue

                context_user = AdjudicatorAssignmentContext(
                    ROUND=round.name, USER=adj.name, POSITION=adj_position_names[pos],
                    VENUE=debate.venue.display_name if debate.venue is not None else _("TBA"),
                    PANEL=_assemble_panel(debate.adjudicators.with_positions()),
                    DRAW=debate.matchup_codes if use_codes else debate.matchup,
                    URL=url + adj.url_key + '/' if adj.url_key else '',
                )
                emails.append((context_user, adj))

        return emails


class RandomizedUrlEmailGenerator(NotificationContextGenerator):
    def __call__(self, to: 'QuerySet[Person]', url: str, tournament: 'Tournament') -> List[Tuple[RandomizedUrlContext, 'Person']]:
        return [(RandomizedUrlContext(USER=p.name, URL=url + p.url_key + '/', KEY=p.url_key, TOURN=str(tournament)), p) for p in to]


class BallotsEmailGenerator(NotificationContextGenerator):
    def __call__(self, to: 'QuerySet[Person]', debate: 'Debate') -> List[Tuple[BallotsContext, 'Person']]:  # "to" is unused
        emails = []
        tournament = debate.round.tournament
        results = DebateResult(debate.confirmed_ballot)
        round_name = _("%(tournament)s %(round)s @ %(room)s") % {'tournament': str(tournament),
                                                                 'round': debate.round.name, 'room': debate.venue.name}

        use_codes = use_team_code_names(tournament, False)

        def _create_ballot(result, scoresheet):
            ballot = "<ul>"

            for side, (side_name, pos_names) in zip(tournament.sides, side_and_position_names(tournament)):
                side_string = ""
                if tournament.pref('teams_in_debate') == 'bp':
                    side_string += _("<li>%(side)s: %(team)s (%(points)d points with %(speaks)s total speaks)")
                    points = 4 - scoresheet.rank(side)
                else:
                    side_string += _("<li>%(side)s: %(team)s (%(points)s - %(speaks)s total speaks)")
                    points = _("Win") if side in scoresheet.winners() else _("Loss")

                ballot += side_string % {
                    'side': side_name,
                    'team': result.debateteams[side].team.code_name if use_codes else result.debateteams[side].team.short_name,
                    'speaks': formats.localize(scoresheet.get_total(side)),
                    'points': points,
                }

                ballot += "<ul>"

                for pos, pos_name in zip(tournament.positions, pos_names):
                    ballot += _("<li>%(pos)s: %(speaker)s (%(score)s)</li>") % {
                        'pos': pos_name,
                        'speaker': result.get_speaker(side, pos).name,
                        'score': formats.localize(scoresheet.get_score(side, pos)),
                    }

                ballot += "</ul></li>"

            ballot += "</ul>"

            return mark_safe(ballot)

        if isinstance(results, DebateResultByAdjudicatorWithScores):
            for adj, ballot in results.scoresheets.items():
                if adj.email is None:  # As "to" is None, must check if eligible email
                    continue

                context = BallotsContext(DEBATE=round_name, USER=adj.name, SCORES=_create_ballot(results, ballot))
                emails.append((context, adj))
        elif isinstance(results, ConsensusDebateResultWithScores):
            for adj in debate.debateadjudicator_set.all().select_related('adjudicator'):
                if adj.adjudicator.email is None:
                    continue

                context_user = BallotsContext(
                    DEBATE=round_name, USER=adj.adjudicator.name,
                    SCORES=_create_ballot(results, results.scoresheet),
                )
                emails.append((context_user, adj.adjudicator))

        return emails


class StandingsEmailGenerator(NotificationContextGenerator):
    def __call__(self, to: 'QuerySet[Person]', url: str, round: 'Round') -> List[Tuple[StandingsContext, 'Person']]:
        emails = []
        to_ids = {p.id for p in to}

        teams = round.active_teams.filter(speaker__in=to).prefetch_related('speaker_set')
        populate_win_counts(teams, round)

        for team in teams:
            for speaker in team.speaker_set.all():
                if not _check_in_to(speaker.id, to_ids):
                    continue

                context_user = StandingsContext(
                    TOURN=str(round.tournament), ROUND=round.name, URL=url,
                    POINTS=str(team.points_count), TEAM=team.short_name,
                    USER=speaker.name,
                )
                emails.append((context_user, speaker))

        return emails


class MotionReleaseEmailGenerator(NotificationContextGenerator):
    def __call__(self, to: 'QuerySet[Person]', round: 'Round') -> List[Tuple[MotionReleaseContext, 'Person']]:
        def _create_motion_list():
            motion_list = "<ul>"
            for motion in round.motion_set.all():
                motion_list += _("<li>%(text)s (%(ref)s)</li>") % {'text': motion.text, 'ref': motion.reference}

                if motion.info_slide:
                    motion_list += "   %s\n" % (motion.info_slide)

            motion_list += "</ul>"

            return mark_safe(motion_list)

        return [(MotionReleaseContext(TOURN=str(round.tournament), ROUND=round.name, MOTIONS=_create_motion_list(), USER=p.name), p) for p in to]


class TeamSpeakerEmailGenerator(NotificationContextGenerator):
    def __call__(self, to: 'QuerySet[Person]', tournament: 'Tournament') -> List[Tuple[TeamSpeakerContext, 'Person']]:
        emails = []
        to_ids = {p.id for p in to}

        teams = tournament.team_set.filter(speaker__in=to).prefetch_related('speaker_set', 'break_categories').select_related('institution')
        for team in teams:
            for speaker in team.speakers:
                if not _check_in_to(speaker.id, to_ids):
                    continue

                context_user = TeamSpeakerContext(
                    TOURN=str(tournament), SHORT=team.short_name, LONG=team.long_name, CODE=team.code_name,
                    BREAK=_(", ").join([breakq.name for breakq in team.break_categories.all()]),
                    SPEAKERS=_(", ").join([p.name for p in team.speaker_set.all()]),
                    INSTITUTION=str(team.institution), EMOJI=team.emoji,
                )
                emails.append((context_user, speaker))

        return emails


class TeamDrawEmailGenerator(NotificationContextGenerator):
    def __call__(self, to: 'QuerySet[Person]', round: 'Round') -> List[Tuple[TeamDrawContext, 'Person']]:
        emails = []
        to_ids = {p.id for p in to}
        tournament = round.tournament
        draw = round.debate_set_with_prefetches(speakers=True).filter(debateteam__team__speaker__in=to)
        use_codes = use_team_code_names(tournament, False)

        for debate in draw:
            for dt in debate.debateteam_set.all():
                for speaker in dt.team.speakers:
                    if not _check_in_to(speaker.id, to_ids):
                        continue

                    context_user = TeamDrawContext(
                        ROUND=round.name, VENUE=debate.venue.name, USER=speaker.name,
                        TEAM=dt.team.code_name if use_codes else dt.team.short_name,
                        SIDE=dt.get_side_name(tournament=round.tournament),
                        DRAW=debate.matchup_codes if use_codes else debate.matchup,
                        PANEL=_assemble_panel(debate.adjudicators.with_positions()),
                    )
                    emails.append((context_user, speaker))

        return emails
