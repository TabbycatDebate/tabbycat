from . import models

from utils.views import *

@login_required
@tournament_view
def action_log_update(request, t):

    actions = models.ActionLog.objects.filter(tournament=t).order_by('-id')[:20].select_related(
        'user', 'debate', 'ballot_submission'
    )

    import datetime
    now = datetime.datetime.now()
    action_objects = []
    timestamp_template = Template("{% load humanize %}{{ t|naturaltime }}")
    for a in actions:
        action = {
            'user': a.user.username if a.user else a.ip_address or "anonymous",
            'type': a.get_type_display(),
            'param': a.get_parameters_display(),
            'timestamp': timestamp_template.render(Context({'t': a.timestamp})),
        }
        action_objects.append(action)

    return HttpResponse(json.dumps(action_objects), content_type="text/json")
