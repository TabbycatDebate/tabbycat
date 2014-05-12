import debate.models as m

for al in m.ActionLog.objects.all():
    print repr(al)
    for field in m.ActionLog.ALL_OPTIONAL_FIELDS:
        field_value = getattr(al, field)
        if field_value:
            print "    ", field, getattr(al, field)