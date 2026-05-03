# donations/context_processors.py
from .models import Notification

def notifications_context(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        notifications = []
        unread_count = 0

    return {
        'notifications': notifications,
        'notifications_unread_count': unread_count
    }
