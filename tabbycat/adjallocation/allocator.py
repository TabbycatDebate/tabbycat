
def allocate_adjudicators(round, alloc_class):
    if round.draw_status != round.STATUS_CONFIRMED:
        raise RuntimeError("Tried to allocate adjudicators on unconfirmed draw")

    debates = round.get_draw()
    adjs = list(round.active_adjudicators.accredited())
    allocator = alloc_class(debates, adjs)

    for alloc in allocator.allocate():
        alloc.save()

    round.adjudicator_status = round.STATUS_DRAFT
    round.save()


class Allocator(object):
    def __init__(self, debates, adjudicators):
        self.debates = list(debates)
        self.adjudicators = adjudicators

    def allocate(self):
        raise NotImplementedError
