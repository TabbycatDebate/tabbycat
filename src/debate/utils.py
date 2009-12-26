from functools import wraps

def memoize(fn):
    cache = {}
    @wraps(fn)
    def foo(*args):
        if args not in cache:
            cache[args] = fn(*args)

        return cache[(args)]

    foo.func_name = fn.func_name
    return foo

        
def pair_list(ls):
    half = len(ls)/2
    return zip(ls[:half], ls[half:])

def gen_results():
    import random

    r = {'aff': (0,), 'neg': (0,)}

    def do():
        s = [random.randint(60, 80) for i in range(3)]
        s.append(random.randint(30,40))
        return s

    while sum(r['aff']) == sum(r['neg']):
        r['aff'] = do()
        r['neg'] = do()

    return r

def generate_random_results(round):
    from debate.models import Debate, DebateResult

    debates = Debate.objects.filter(round=round)

    for debate in debates:
        dr = DebateResult(debate)
        
        rr = gen_results()
        for team in ('aff', 'neg'):
            speakers = getattr(debate, '%s_team' % team).speakers
            scores = rr[team]
            for i in range(1, 4):
                dr.set_speaker_entry(
                    team = team,
                    pos = i,
                    speaker = speakers[i - 1],
                    score = scores[i-1],
                )
            dr.set_speaker_entry(
                team = team,
                pos = 4,
                speaker = speakers[0],
                score = scores[3]
            )

        dr.save()
        debate.result_status = debate.STATUS_CONFIRMED
        debate.save()

        
def test_gen():
    from debate.models import Round
    generate_random_results(Round.objects.get(pk=1))

