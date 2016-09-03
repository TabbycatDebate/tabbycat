from django.contrib.humanize.templatetags.humanize import naturaltime

from utils.mixins import JsonDataResponseView, LoginRequiredMixin
from tournaments.mixins import TournamentMixin

from .models import ActionLogEntry


class LatestActionsView(LoginRequiredMixin, TournamentMixin, JsonDataResponseView):

    def get_data(self):
        actions = self.get_tournament().actionlogentry_set.select_related(
                'user', 'debate', 'ballot_submission').order_by('-timestamp')[:15]

        action_objects = []
        for a in actions:
            action_objects.append({
                'user': a.user.username if a.user else a.ip_address or "anonymous",
                'type': a.get_type_display(),
                'param': a.get_parameters_display(),
                'timestamp': naturaltime(a.timestamp),
            })
        return action_objects
