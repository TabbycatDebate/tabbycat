from participants.models import Speaker
from utils.forms import BaseEligibilityForm


class SpeakerCategoryEligibilityForm(BaseEligibilityForm):
    """Sets which teams are eligible for the break."""

    categories_field_name = 'categories'

    def __init__(self, tournament, *args, **kwargs):
        self.tournament = tournament
        super().__init__(*args, **kwargs)

    def get_instance_queryset(self):
        return Speaker.objects.filter(team__tournament=self.tournament).order_by(
                'team__short_name').select_related('team', 'team__institution')

    def get_category_queryset(self):
        return self.tournament.speakercategory_set.all()
