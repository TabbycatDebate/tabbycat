from draw.types import DebateSide


def is_staff(context):
    # OpenAPI generation does not have a view (sometimes context is also None in that circumstance).
    # Avoid redacting fields.
    return context is None or 'view' not in context or context['request'].user.is_staff


def get_side(side: str, seq: int) -> int:
    try:
        return DebateSide[side.upper()]
    except KeyError:
        return seq
