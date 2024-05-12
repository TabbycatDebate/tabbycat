def is_staff(context):
    # OpenAPI generation does not have a view (sometimes context is also None in that circumstance).
    # Avoid redacting fields.
    return context is None or 'view' not in context or not context['request'].user.is_anonymous
