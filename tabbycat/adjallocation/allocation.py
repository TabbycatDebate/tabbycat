from warnings import warn

from .models import DebateAdjudicator


class AdjudicatorAllocation:
    """Class for handling the adjudicators on a panel."""

    POSITION_CHAIR = 'c'
    POSITION_ONLY = 'o'
    POSITION_PANELLIST = 'p'
    POSITION_TRAINEE = 't'

    def __init__(self, debate, chair=None, panellists=[], trainees=[], from_db=False):
        self.debate = debate

        if from_db:
            if chair or panellists or trainees:
                warn("The chair, panellists and trainees arguments are ignored when from_db is used.")
            self.chair = None
            self.panellists = []
            self.trainees = []
            for a in self.debate.debateadjudicator_set.prefetch_related('adjudicator').all():
                if a.type is a.TYPE_CHAIR:
                    self.chair = a.adjudicator
                if a.type is a.TYPE_PANEL:
                    self.panellists.append(a.adjudicator)
                if a.type is a.TYPE_TRAINEE:
                    self.trainees.append(a.adjudicator)

        else:
            self.chair = chair
            self.panellists = panellists
            self.trainees = trainees

    def __len__(self):
        return (0 if self.chair is None else 1) + len(self.panellists) + len(self.trainees)

    def __str__(self):
        items = [str(getattr(x, "name", x)) for x in self.list]
        return ", ".join(items)

    def __contains__(self, item):
        return item == self.chair or item in self.panellists or item in self.trainees

    def __eq__(self, other):
        return self.debate == other.debate and \
            self.chair == other.chair and \
            set(self.panellists) == set(other.panellists) and \
            set(self.trainees) == set(other.trainees)

    # ==========================================================================
    # Booleans and other quick properties
    # ==========================================================================

    @property
    def has_chair(self):
        return self.chair is not None

    @property
    def is_panel(self):
        return len(self.panellists) > 0

    @property
    def valid(self):
        return self.has_chair and len(self.panellists) % 2 == 0

    @property
    def num_voting(self):
        return (0 if self.chair is None else 1) + len(self.panellists)

    # ==========================================================================
    # Iterators
    # ==========================================================================

    def voting(self):
        """Iterates through voting members of the panel."""
        if self.chair is not None:
            yield self.chair
        for a in self.panellists:
            yield a

    def all(self):
        """Iterates through all members of the panel."""
        for a in self.voting():
            yield a
        for a in self.trainees:
            yield a

    def with_positions(self):
        """Iterates through 2-tuples `(adj, type)`, where `type` is one of the
        `AdjudicatorAllocation.POSITION_*` constants (`CHAIR`, `ONLY`,
        `PANELLIST` or `TRAINEE`).

        Note that the `AdjudicatorAllocation.POSITION_*` constants are not
        necessarily the same as the `DebateAdjudicator.TYPE_*` constants."""

        if self.chair is not None:
            yield self.chair, self.POSITION_CHAIR if self.is_panel else self.POSITION_ONLY
        for a in self.panellists:
            yield a, self.POSITION_PANELLIST
        for a in self.trainees:
            yield a, self.POSITION_TRAINEE

    # ==========================================================================
    # Database operations
    # ==========================================================================

    def delete(self):
        """Delete existing, current allocation"""
        self.debate.debateadjudicator_set.all().delete()
        self.chair = None
        self.panellists = []
        self.trainees = []

    def save(self):
        self.debate.debateadjudicator_set.all().delete()
        for adj, t in self.with_positions():
            if adj:
                DebateAdjudicator(debate=self.debate, adjudicator=adj, type=t).save()

    # ==========================================================================
    # Deprecated
    # ==========================================================================

    @property
    def list(self):
        warn("AdjudicatorAllocation.list is deprecated, use AdjudicatorAllocation.voting() instead", stacklevel=2)
        a = [self.chair]
        a.extend(self.panellists)
        return a

    def __iter__(self):
        warn("AdjudicatorAllocation.__iter__() is deprecated, use AdjudicatorAllocation.with_positions() instead", stacklevel=2)
        if self.chair is not None:
            yield DebateAdjudicator.TYPE_CHAIR, self.chair
        for a in self.panellists:
            yield DebateAdjudicator.TYPE_PANEL, a
        for a in self.trainees:
            yield DebateAdjudicator.TYPE_TRAINEE, a

    @property
    def panel(self):
        warn("AdjudicatorAllocation.panel is deprecated, use AdjudicatorAllocation.panellists instead", stacklevel=2)
        return self.panellists
