"""Sandbox for figuring out how to do standings and other aggregates."""

import header
import tournaments.models as tm
from django.db import models

import argparse
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("round", type=int, help="Round to look at")
parser.add_argument("--teams", action="store_true")
parser.add_argument("--speakers", action="store_true")
parser.add_argument("--replies", action="store_true")
args = parser.parse_args()

round = tm.Round.objects.get(seq=args.round)

if args.teams:
    teams = tm.Team.objects

    teams = teams.filter(
        institution__tournament = round.tournament,
        debateteam__debate__round__seq__lte = round.seq,
    )

    #teams = teams.filter(
        #debateteam__teamscore__ballot_submission__confirmed = True
    #).annotate(
        #points = models.Count('debateteam__teamscore__points'),
        #speaker_score = models.Count('debateteam__teamscore__score'),
    #).order_by('-points', '-speaker_score')

    #teams = teams.annotate(
        #points = models.Count('debateteam__teamscore__points'),
        #speaker_score = models.Count('debateteam__teamscore__score'),
    #)

    #teams = teams.order_by('-points', '-speaker_score')

    # Sum the team scores for each team for which
    #teams = teams.extra({"points": """
        #SELECT DISTINCT SUM("points")
        #FROM "results_teamscore"
        #JOIN "results_ballotsubmission" ON "results_teamscore"."ballot_submission_id" = "results_ballotsubmission"."id"
        #JOIN "draws_debateteam" ON "results_teamscore"."debate_team_id" = "draws_debateteam"."id"
        #JOIN "draws_debate" ON "draws_debateteam"."debate_id" = "draws_debate"."id"
        #JOIN "debate_round" ON "draws_debate"."round_id" = "debate_round"."id"
        #JOIN "debate_institution" ON "debate_team"."instition_id" = "debate_institution"."id"
        #WHERE "results_ballotsubmission"."confirmed" = True
        #AND "draws_debateteam"."team_id" = "debate_team"."id"
        #AND "debate_institution"."tournament_id" = {tournament:d}
        #AND "debate_round"."seq" <= {round:d}
    #""".format(tournament=round.tournament.id, round=round.seq),
    #"speaker_score": """
        #SELECT SUM("score")
        #FROM "results_teamscore"
        #JOIN "results_ballotsubmission" ON "results_teamscore"."ballot_submission_id" = "results_ballotsubmission"."id"
        #JOIN "draws_debateteam" ON "results_teamscore"."debate_team_id" = "draws_debateteam"."id"
        #JOIN "draws_debate" ON "draws_debateteam"."debate_id" = "draws_debate"."id"
        #JOIN "debate_round" ON "draws_debate"."round_id" = "debate_round"."id"
        #JOIN "debate_institution" ON "debate_team"."institution_id" = "debate_institution"."id"
        #WHERE "results_ballotsubmission"."confirmed" = True
        #AND "draws_debateteam"."team_id" = "debate_team"."id"
        #AND "debate_institution"."tournament_id" = {tournament:d}
        #AND "debate_round"."seq" <= {round:d}
    #""".format(tournament=round.tournament.id, round=round.seq)}).distinct()

    EXTRA_QUERY = """
        SELECT DISTINCT SUM({field:s})
        FROM "results_teamscore"
        JOIN "results_ballotsubmission" ON "results_teamscore"."ballot_submission_id" = "results_ballotsubmission"."id"
        JOIN "draws_debateteam" ON "results_teamscore"."debate_team_id" = "draws_debateteam"."id"
        JOIN "draws_debate" ON "draws_debateteam"."debate_id" = "draws_debate"."id"
        JOIN "debate_round" ON "draws_debate"."round_id" = "debate_round"."id"
        WHERE "results_ballotsubmission"."confirmed" = True
        AND "draws_debateteam"."team_id" = "debate_team"."id"
        AND "debate_round"."seq" <= {round:d}
    """
    teams = teams.extra({
        "points": EXTRA_QUERY.format(field="points", round=round.seq),
        "speaker_score": EXTRA_QUERY.format(field="score", round=round.seq, affects_averages=True)}
    ).distinct().order_by("-points", "-speaker_score")

    print teams.query
    print teams.count()

    for team in teams:
        print "{0:<20} {1:>10} {2:>5}".format(team.short_name, team.points, team.speaker_score)

if args.speakers:
    speakers = m.Speaker.objects.filter(
        team__institution__tournament=round.tournament,
        speakerscore__position__lte=round.tournament.LAST_SUBSTANTIVE_POSITION,
        speakerscore__debate_team__debate__round__seq__lte = round.seq,
    )

    # TODO fix this, should only aggregate over confirmed ballots
    #speakers = speakers.annotate(
        #total = models.Sum('speakerscore__score'),
    #).order_by('-total', 'name')

    EXTRA_QUERY = """
        SELECT DISTINCT SUM("score")
        FROM "debate_speakerscore"
        JOIN "draws_debateteam" ON "debate_speakerscore"."debate_team_id" = "draws_debateteam"."id"
        JOIN "draws_debate" ON "draws_debateteam"."debate_id" = "draws_debate"."id"
        JOIN "debate_round" ON "draws_debate"."round_id" = "debate_round"."id"
        JOIN "results_ballotsubmission" ON "debate_speakerscore"."ballot_submission_id" = "results_ballotsubmission"."id"
        WHERE "results_ballotsubmission"."confirmed" = True
        AND "debate_speakerscore"."speaker_id" = "participants_speaker"."person_ptr_id"
        AND "debate_speakerscore"."position" <= {position:d}
        AND "debate_round"."seq" <= {round:d}
    """.format(
        round = round.seq,
        position = round.tournament.LAST_SUBSTANTIVE_POSITION
    )
    speakers = speakers.extra({"total": EXTRA_QUERY}).distinct().order_by("-total")

    print speakers.query
    print speakers.count()
    #print m.SpeakerScore.objects.filter(
        #ballot_submission__confirmed=True,
        #debate_team__debate__round__seq__lte = round.seq,
        #position__lte = round.tournament.LAST_SUBSTANTIVE_POSITION
    #).distinct().count()

    for speaker in speakers:
        print "{0:<30} {1:>10.2f}".format(speaker.name, speaker.total)

if args.replies:
    speakers = m.Speaker.objects.filter(
        team__institution__tournament=round.tournament,
        speakerscore__position=round.tournament.REPLY_POSITION,
        speakerscore__debate_team__debate__round__seq__lte =
        round.seq,
    )

    EXTRA_QUERY = """
        SELECT DISTINCT {aggregator:s}("score")
        FROM "debate_speakerscore"
        JOIN "draws_debateteam" ON "debate_speakerscore"."debate_team_id" = "draws_debateteam"."id"
        JOIN "draws_debate" ON "draws_debateteam"."debate_id" = "draws_debate"."id"
        JOIN "debate_round" ON "draws_debate"."round_id" = "debate_round"."id"
        JOIN "results_ballotsubmission" ON "debate_speakerscore"."ballot_submission_id" = "results_ballotsubmission"."id"
        WHERE "results_ballotsubmission"."confirmed" = True
        AND "debate_speakerscore"."speaker_id" = "participants_speaker"."person_ptr_id"
        AND "debate_speakerscore"."position" = {position:d}
        AND "debate_round"."seq" <= {round:d}
    """
    speakers = speakers.extra({"average": EXTRA_QUERY.format(
        aggregator = "AVG",
        round = round.seq,
        position = round.tournament.REPLY_POSITION
    ), "replies": EXTRA_QUERY.format(
        aggregator = "COUNT",
        round = round.seq,
        position = round.tournament.REPLY_POSITION
    )}).distinct().order_by('-average', '-replies', 'name')

    print speakers.query
    print speakers.count()

    for speaker in speakers:
        print "{0:<30} {1:>7.2f} {2:>2d}".format(speaker.name, speaker.average, speaker.replies)
