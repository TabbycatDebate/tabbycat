import string
from typing import TYPE_CHECKING

from django.middleware.csrf import get_token
from django.utils.html import format_html
from django.utils.translation import gettext as _

from participants.models import RegistrationStatus
from tournaments.models import Tournament
from utils.misc import generate_identifier_string, reverse_tournament

from .models import Invitation, SlotTransferRequest

if TYPE_CHECKING:
    from django.http import HttpRequest

    from utils.tables import TabbycatTableBuilder


def populate_invitation_url_keys(instances: list[Invitation], tournament: Tournament, length: int = 15, num_attempts: int = 10) -> None:
    """Populates the URL key field for every instance in the given QuerySet."""
    chars = string.ascii_lowercase + string.digits

    existing_keys = list(Invitation.objects.exclude(url_key__isnull=True).values_list('url_key', flat=True))
    for instance in instances:
        for i in range(num_attempts):
            new_key = generate_identifier_string(chars, length)
            if new_key not in existing_keys:
                instance.url_key = new_key
                existing_keys.append(new_key)
                break


confirm_html = """
<form method="POST" action="{}" style="display: inline;">
    <input type="hidden" name="csrfmiddlewaretoken" value="{}"/>
    <button type="submit" class="btn btn-sm btn-success">
        <div class="d-flex justify-content-center align-items-center">
            <i data-feather="check-circle" style="height: 16px;width: 16px;margin-bottom: -2.5px;"></i>
        </div>
    </button>
</form>"""


def add_confirm_button_column(table: 'TabbycatTableBuilder', instances: list, url_name: str, request: 'HttpRequest') -> None:
    csrf_token = get_token(request)
    confirm_buttons = []
    for instance in instances:
        if instance.registration_status != RegistrationStatus.CONFIRMED:
            confirm_url = reverse_tournament(url_name, table.tournament, kwargs={'pk': instance.pk})
            confirm_buttons.append({
                'text': format_html(confirm_html, confirm_url, csrf_token),
                'sort': 0,
            })
        else:
            confirm_buttons.append({'icon': 'check', 'sort': 1, 'class': 'text-success'})
    table.add_column({'key': 'confirm', 'title': _("Confirm")}, confirm_buttons)


slot_transfer_approve_html = """
<form method="POST" action="{}" style="display: inline;">
    <input type="hidden" name="csrfmiddlewaretoken" value="{}"/>
    <input type="hidden" name="action" value="approve"/>
    <button type="submit" class="btn btn-sm btn-success">{}</button>
</form>"""


def add_slot_transfer_status_column(table: 'TabbycatTableBuilder', transfers: list, request: 'HttpRequest') -> None:
    """Add a Status column: Approve button for PENDING, otherwise status text."""
    csrf_token = get_token(request)
    status_cells = []
    for transfer in transfers:
        if transfer.status == SlotTransferRequest.Status.PENDING:
            url = reverse_tournament('reg-slot-transfer-update', table.tournament, kwargs={'pk': transfer.pk})
            status_cells.append({
                'text': format_html(slot_transfer_approve_html, url, csrf_token, _("Approve")),
                'sort': 0,
            })
        else:
            status_cells.append({'text': transfer.get_status_display(), 'sort': 1})
    table.add_column({'key': 'status', 'title': _("Status")}, status_cells)
