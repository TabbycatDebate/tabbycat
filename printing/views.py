from debate.views import round_view, admin_required, r2r
from debate.models import Round, Motion

@admin_required
@round_view
def draw_print_feedback(request, round):
    draw = round.get_draw_by_room()
    config = round.tournament.config
    questions = round.tournament.adj_feedback_questions
    for question in questions:
        if question.choices:
            question.choice_options = question.choices.split("//")
        if question.min_value is not None and question.max_value is not None:
            step = max((int(question.max_value) - int(question.min_value)) / 10, 1)
            question.number_options = range(int(question.min_value), int(question.max_value+1), int(step) )

    return r2r(request, "printing/feedback_list.html", dict(
        draw=draw, config=config, questions=questions))

@admin_required
@round_view
def draw_print_scoresheets(request, round):
    draw = round.get_draw_by_room()
    config = round.tournament.config
    motions = Motion.objects.filter(round=round)

    return r2r(request, "printing/scoresheet_list.html", dict(
        draw=draw, config=config, motions=motions))

