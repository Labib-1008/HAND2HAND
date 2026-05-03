from django.contrib import admin
from .models import ContactMessage

# Register your models here.

from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__username", "message")





@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'short_message', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_filter = ('created_at',)

    def short_message(self, obj):
        return obj.message[:50] + ("..." if len(obj.message) > 50 else "")
    short_message.short_description = "Message"






