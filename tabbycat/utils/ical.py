from datetime import UTC
from zoneinfo import ZoneInfo

from django.utils import timezone
from django.utils.encoding import force_str


def _escape_text(value):
    """Escape a text value as required by RFC 5545."""
    return (force_str(value).replace('\\', '\\\\').replace('\r\n', '\\n')
            .replace('\r', '\\n').replace('\n', '\\n')
            .replace(';', '\\;').replace(',', '\\,'))


def _fold_line(line):
    """Fold a content line without splitting UTF-8 characters."""
    folded = []
    current = ''
    limit = 75
    for character in line:
        if current and len((current + character).encode('utf-8')) > limit:
            folded.append(current)
            current = character
            limit = 74  # Continuation lines begin with one whitespace octet.
        else:
            current += character
    folded.append(current)
    return '\r\n '.join(folded)


def _format_datetime(value, tz):
    if timezone.is_naive(value):
        value = timezone.make_aware(value, tz)
    return value.astimezone(tz).strftime('%Y%m%dT%H%M%S')


class ICalendar:
    """A small iCalendar writer for calendars containing timed events."""

    def __init__(self, name, timezone_name, prodid):
        self.name = name
        self.timezone_name = timezone_name
        self.prodid = prodid
        self.events = []

    def add_event(self, uid, start, summary, url=None, end=None):
        self.events.append({
            'uid': uid,
            'start': start,
            'summary': summary,
            'url': url,
            'end': end,
        })

    def to_ical(self):
        calendar_timezone = ZoneInfo(self.timezone_name)
        timestamp = _format_datetime(timezone.now(), UTC) + 'Z'
        lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            f'PRODID:{self.prodid}',
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH',
            f'X-WR-CALNAME:{_escape_text(self.name)}',
            f'X-WR-TIMEZONE:{self.timezone_name}',
        ]

        for event in self.events:
            lines.extend([
                'BEGIN:VEVENT',
                f'UID:{event["uid"]}',
                f'DTSTAMP:{timestamp}',
                f'DTSTART;TZID={self.timezone_name}:{_format_datetime(event["start"], calendar_timezone)}',
            ])
            if event['end']:
                lines.append(
                    f'DTEND;TZID={self.timezone_name}:{_format_datetime(event["end"], calendar_timezone)}',
                )
            lines.append(f'SUMMARY:{_escape_text(event["summary"])}')
            if event['url']:
                lines.append(f'URL:{event["url"]}')
            lines.append('END:VEVENT')

        lines.append('END:VCALENDAR')
        return '\r\n'.join(_fold_line(line) for line in lines) + '\r\n'
