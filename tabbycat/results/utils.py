from warnings import warn

from django.db.models import Count

from draw.models import Debate

def get_result_status_stats(round):
    """Returns a dict where keys are result statuses of debates; values are the
    number of debates in the round with that status.

    There is also an additional key 'B' that denotes those with ballots checked
    in, but whose results are not entered."""

    # query looks like: [{'result_status': 'C', 'result_status__count': 8}, ...]
    query = round.debate_set.values('result_status').annotate(Count('result_status')).order_by()

    # The query doesn't return zeroes where appropriate - for statuses with no
    # debates, it just omits the item altogether. So initialize a dict:
    choices = [code for code, name in Debate.STATUS_CHOICES]
    stats = dict.fromkeys(choices, 0)
    for item in query:
        stats[item['result_status']] = item['result_status__count']

    # separately, count ballot-in debates and subtract from the 'None' count
    ballot_in = round.debate_set.filter(result_status=Debate.STATUS_NONE, ballot_in=True).count()
    stats['B'] = ballot_in
    stats[Debate.STATUS_NONE] -= ballot_in

    return stats
