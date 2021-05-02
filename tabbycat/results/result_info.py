"""Debate result classes using attributes

These classes are basically the same as DebateResult classes, but where methods
to get data from the object is replaced with the use of attributes, for easier
use with Django REST serializers. In effect, these objects are an easy way to
get all result information for a DebateResult.

These objects are initialized with a DebateResult object and expanded in a
standardized format, equivalent to:
{
    "sheets": [
        {
            "adjudicator": Adjudicator/None,
            "teams": [
                {
                    "team": Team,
                    "side": str,
                    "points": int/None,
                    "win": bool
                    "score": float/None,
                    "speeches": [
                        {
                            "speaker": Speaker,
                            "score": float,
                            "ghost": bool
                        }
                    ]
                }
            ]
        }
    ]
}
"""


class SpeechInfo:
    def __init__(self, result, adj, side, pos):
        self.speaker = result.get_speaker(side, pos)
        self.ghost = result.get_ghost(side, pos)

        if adj is None:
            self.score = result.speakerscore_field_score(side, pos)
        else:
            self.score = result.speakerscorebyadj_field_score(adj, side, pos)


class TeamSheetInfo:
    def __init__(self, result, adj, dt):
        self.team = dt.team
        self.side = dt.side

        metric_kwargs = {'side': dt.side}
        if adj is not None:
            metric_kwargs['adj'] = adj
            self.points = int(result.teamscorebyadj_field_win(**metric_kwargs))
            self.score = result.teamscorebyadj_field_score(**metric_kwargs)
            self.win = result.teamscorebyadj_field_win(**metric_kwargs)
        else:
            self.points = result.teamscore_field_points(**metric_kwargs)
            self.score = result.teamscore_field_score(**metric_kwargs)
            self.win = result.teamscore_field_win(**metric_kwargs)

        if result.uses_speakers:
            self.speeches = [SpeechInfo(result, adj, dt.side, pos) for pos in result.positions]


class SheetInfo:
    def __init__(self, result, d_adj=None):
        self.adjudicator = getattr(d_adj, 'adjudicator', None)
        self.teams = [TeamSheetInfo(result, self.adjudicator, dt) for dt in result.debateteams.values()]


class DebateResultInfo:
    def __init__(self, result):
        if result.is_voting:
            self.sheets = [SheetInfo(result, d_adj) for d_adj in result.debateadjs.values()]
        else:
            self.sheets = [SheetInfo(result)]
