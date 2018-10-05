from django.db.models import Exists, OuterRef
from django.utils.translation import gettext as _

from adjallocation.allocation import AdjudicatorAllocation
from adjallocation.models import DebateAdjudicator
from draw.models import Debate
from results.result import DebateResult
from options.utils import use_team_code_names
from participants.prefetch import populate_win_counts
from tournaments.models import Round, Tournament

from .models import SentMessageRecord


def adjudicator_assignment_email_generator(round_id):
    emails = []
    round = Round.objects.get(id=round_id)
    tournament = round.tournament
    draw = round.debate_set_with_prefetches(speakers=False, divisions=False).all()
    use_codes = use_team_code_names(tournament, False)

    adj_position_names = {
        AdjudicatorAllocation.POSITION_CHAIR: _("the chair"),
        AdjudicatorAllocation.POSITION_ONLY: _("the only"),
        AdjudicatorAllocation.POSITION_PANELLIST: _("a panellist"),
        AdjudicatorAllocation.POSITION_TRAINEE: _("a trainee"),
    }

    def _assemble_panel(adjs):
        adj_string = []
        for adj, pos in adjs:
            adj_string.append("%s (%s)" % (adj.name, adj_position_names[pos]))

        return ", ".join(adj_string)

    for debate in draw:
        matchup = debate.matchup_codes if use_codes else debate.matchup
        context = {
            'ROUND': round.name,
            'VENUE': debate.venue.name,
            'PANEL': _assemble_panel(debate.adjudicators.with_positions()),
            'DRAW': matchup
        }

        for adj, pos in debate.adjudicators.with_positions():
            if adj.email is None:
                continue

            context_user = context.copy()
            context_user['USER'] = adj.name
            context_user['POSITION'] = adj_position_names[pos]

            emails.append((context_user, adj))

    return emails


def randomized_url_email_generator(url, tournament_id):
    emails = []
    tournament = Tournament.objects.get(id=tournament_id)

    subquery = SentMessageRecord.objects.filter(
        event=SentMessageRecord.EVENT_TYPE_URL,
        tournament=tournament, email=OuterRef('email')
    )
    participants = tournament.participants.filter(
        url_key__isnull=False, email__isnull=False
    ).exclude(email__exact="").annotate(already_sent=Exists(subquery)).filter(already_sent=False)

    for instance in participants:
        url_ind = url + instance.url_key + '/'

        variables = {'USER': instance.name, 'URL': url_ind, 'KEY': instance.url_key, 'TOURN': str(tournament)}

        emails.append((variables, instance))

    return emails


def ballots_email_generator(debate_id):
    emails = []
    debate = Debate.objects.get(id=debate_id)
    tournament = debate.round.tournament
    ballots = DebateResult(debate.confirmed_ballot).as_dicts()
    round_name = _("%(tournament)s %(round)s @ %(room)s") % {'tournament': str(tournament),
                                                             'round': debate.round.name, 'room': debate.venue.name}

    context = {'DEBATE': round_name}
    use_codes = use_team_code_names(debate.round.tournament, False)

    for ballot in ballots:
        if 'adjudicator' in ballot:
            judge = ballot['adjudicator']
        else:
            judge = debate.debateadjudicator_set.get(type=DebateAdjudicator.TYPE_CHAIR).adjudicator

        if judge.email is None:
            continue

        scores = ""
        for team in ballot['teams']:

            team_name = team['team'].code_name if use_codes else team['team'].short_name
            scores += _("(%(side)s) %(team)s\n") % {'side': team['side'], 'team': team_name}

            for speaker in team['speakers']:
                scores += _("- %(debater)s: %(score)s\n") % {'debater': speaker['speaker'], 'score': speaker['score']}

        context_user = context.copy()
        context_user['USER'] = judge.name
        context_user['SCORES'] = scores

        emails.append((context, judge))

    return emails


def standings_email_generator(url, round_id):
    emails = []
    round = Round.objects.get(id=round_id)
    tournament = round.tournament

    teams = round.active_teams.prefetch_related('speaker_set')
    populate_win_counts(teams)

    context = {
        'TOURN': str(tournament),
        'ROUND': round.name,
        'URL': url if tournament.pref('public_team_standings') else ""
    }

    for team in teams:
        context_team = context.copy()
        context_team['POINTS'] = str(team.points_count)
        context_team['TEAM'] = team.short_name

        for speaker in team.speaker_set.all():
            if speaker.email is None:
                continue

            context_user = context_team.copy()
            context_user['USER'] = speaker.name

            emails.append((context_user, speaker))

    return emails


def motion_release_email_generator(round_id):
    emails = []
    round = Round.objects.get(id=round_id)

    def _create_motion_list():
        motion_list = ""
        for motion in round.motion_set.all():
            motion_list += _(" - %s (%s)\n") % (motion.text, motion.reference)

            if motion.info_slide:
                motion_list += "   %s\n" % (motion.info_slide)

        return motion_list

    context = {
        'TOURN': str(round.tournament),
        'ROUND': round.name,
        'MOTIONS': _create_motion_list()
    }

    teams = round.tournament.team_set.filter(round_availabilities__round=round).prefetch_related('speaker_set')
    for team in teams:
        for speaker in team.speaker_set.all():
            if speaker.email is None:
                continue

            context_user = context.copy()
            context_user['USER'] = speaker.name

            emails.append((context_user, speaker))

    return emails


def team_speaker_email_generator(tournament_id):
    emails = []
    tournament = Tournament.objects.get(id=tournament_id)

    for team in tournament.team_set.all().prefetch_related('speaker_set', 'break_categories').select_related('division', 'institution'):
        context = {
            'TOURN': str(tournament),
            'SHORT': team.short_name,
            'LONG': team.long_name,
            'CODE': team.code_name,
            'DIVISION': team.division.name if team.division is not None else "",
            'BREAK': _(", ").join([breakq.name for breakq in team.break_categories.all()]),
            'SPEAKERS': _(", ").join([p.name for p in team.speaker_set.all()]),
            'INSTITUTION': str(team.institution),
            'EMOJI': team.emoji
        }

        for speaker in team.speakers:
            if speaker.email is None:
                continue

            context_user = context.copy()
            context_user['USER'] = speaker.name

            emails.append((context_user, speaker))

    return emails
