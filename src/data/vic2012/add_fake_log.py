import debate.models as m
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

AL = m.ActionLog

def log(*args, **kwargs):
    action = m.ActionLog(*args, **kwargs)
    try:
        action.full_clean()
    except ValidationError, e:
        print str(e)
        return
    action.save()

def get_user(username):
    return User.objects.get(username=username)

def get_debate(id):
    return m.Debate.objects.get(id=id)

#log(type=AL.ACTION_TYPE_BALLOT_CHECKIN, user=get_user('czlee1'))
#log(type=AL.ACTION_TYPE_BALLOT_CHECKIN, user=get_user('czlee1'), debate=get_debate(145))
#log(type=AL.ACTION_TYPE_DRAW_CONFIRM, user=get_user('czlee1'), debate=get_debate(145))
#log(type=AL.ACTION_TYPE_FEEDBACK_SUBMIT, user=get_user('czlee1'), debate=get_debate(145))

for al in m.ActionLog.objects.all():
    print repr(al)