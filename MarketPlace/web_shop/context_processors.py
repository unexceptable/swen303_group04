from .models import ChatNotification

def notifications_processor(request):
    #Check login
    if request.user.is_authenticated():
        notifs = ChatNotification.objects.filter(to=request.user)
        return {'notifications': notifs}
    else:
        return {'notifications': None}
