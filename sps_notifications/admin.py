from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('sender', 'get_recipients', 'date_time', 'type_of_notification', 'message')
    list_filter = ('type_of_notification', 'date_time')
    search_fields = ('sender__username', 'recipients__username', 'message')
    readonly_fields = ('date_time',)

    def get_recipients(self, obj):
        return ", ".join([str(recipient) for recipient in obj.recipients.all()])
    get_recipients.short_description = 'Recipients'


