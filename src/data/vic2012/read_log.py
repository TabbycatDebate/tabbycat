import debate.models as m

for al in m.ActionLog.objects.all():
    print repr(al)