class BaseAnnotator:
    """Base class for all annotators."""

    key = NotImplemented
    name = NotImplemented
    abbr = NotImplemented
    glyphicon = None
    format = None
    record_method = NotImplemented

    def annotate(self, standings, *args, **kwargs):
        getattr(standings, self.record_method)(self.key, self.name, self.abbr, self.glyphicon, self.format)
        self.annotate_teams(standings, *args, **kwargs)

    def annotate_teams(self, *args, **kwargs):
        """Annotates the given `standings` by calling `add_ranking()` on every
        `TeamStandingInfo` object in `standings`.

        `standings` is a `TeamStandings` object.
        """
        raise NotImplementedError("BaseMetricAnnotator subclasses must implement annotate()")
