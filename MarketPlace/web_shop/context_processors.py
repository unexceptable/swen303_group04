from .models import Notification

def notifications_processor(request):
    #Check login
    if request.user.is_authenticated():
        notifs = Notification.objects.filter(to=request.user)
        return {'notifications': notifs}
    else:
        return {'notifications': None}
