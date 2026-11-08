"""Value aliases shared by command importers and the CSV wizard."""

import adjfeedback.models as fm
import participants.models as pm
import tournaments.models as tm
import venues.models as vm
from draw.types import DebateSide

from .base import make_lookup


class TournamentDataLookups:
    lookup_round_stage = make_lookup("round stage", {
        ("preliminary", "p"): tm.Round.Stage.PRELIMINARY,
        ("elimination", "break", "e", "b"): tm.Round.Stage.ELIMINATION,
    })

    lookup_draw_type = make_lookup("draw type", {
        ("random", "r"): tm.Round.DrawType.RANDOM,
        ("manual", "m"): tm.Round.DrawType.MANUAL,
        ("round robin", "d"): tm.Round.DrawType.ROUNDROBIN,
        ("power paired", "p"): tm.Round.DrawType.POWERPAIRED,
        ("elimination", "break", "e", "b"): tm.Round.DrawType.ELIMINATION,
    })

    lookup_gender = make_lookup("gender", {
        ("male", "m"): pm.Person.GENDER_MALE,
        ("female", "f"): pm.Person.GENDER_FEMALE,
        ("other", "o"): pm.Person.GENDER_OTHER,
    })

    lookup_team_position = make_lookup("team position", {
        ("affirmative", "aff", "a"): DebateSide.AFF,
        ("negative", "neg", "n"): DebateSide.NEG,
    })

    lookup_feedback_answer_type = make_lookup("feedback answer type", {
        "checkbox": fm.AdjudicatorFeedbackQuestion.AnswerType.BOOLEAN_CHECKBOX,
        ("yes no select", "yesno"): fm.AdjudicatorFeedbackQuestion.AnswerType.BOOLEAN_SELECT,
        ("integer textbox", "int", "integer"): fm.AdjudicatorFeedbackQuestion.AnswerType.INTEGER_TEXTBOX,
        ("integer scale", "scale"): fm.AdjudicatorFeedbackQuestion.AnswerType.INTEGER_SCALE,
        "float": fm.AdjudicatorFeedbackQuestion.AnswerType.FLOAT,
        "text": fm.AdjudicatorFeedbackQuestion.AnswerType.TEXT,
        ("textbox", "long text", "longtext"): fm.AdjudicatorFeedbackQuestion.AnswerType.LONGTEXT,
        ("select single", "single select"): fm.AdjudicatorFeedbackQuestion.AnswerType.SINGLE_SELECT,
        ("select multiple", "multiple select"): fm.AdjudicatorFeedbackQuestion.AnswerType.MULTIPLE_SELECT,
    })

    lookup_venue_category_display = make_lookup("venue category display", {
        "": vm.VenueCategory.DISPLAY_SUFFIX,
        "suffix": vm.VenueCategory.DISPLAY_SUFFIX,
        "prefix": vm.VenueCategory.DISPLAY_PREFIX,
    })
