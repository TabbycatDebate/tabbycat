from django.template import Context, Template

from utils.mixins import JsonDataResponseView, LoginRequiredMixin, TournamentMixin

from .models import ActionLogEntry


class GetLatestActions(JsonDataResponseView, LoginRequiredMixin, TournamentMixin):

    def get_data(self):
        t = self.get_tournament()
        action_objects = []
        actions = ActionLogEntry.objects.filter(tournament=t).order_by(
            '-timestamp')[:15].select_related('user', 'debate', 'ballot_submission')

        timestamp_template = Template("{% load humanize %}{{ t|naturaltime }}")
        for a in actions:
            action_objects.append({
                'user': a.user.username if a.user else a.ip_address or "anonymous",
                'type': a.get_type_display(),
                'param': a.get_parameters_display(),
                'timestamp': timestamp_template.render(Context({'t': a.timestamp})),
            })
        return action_objects
