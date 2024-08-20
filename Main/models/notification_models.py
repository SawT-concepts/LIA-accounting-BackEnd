from django.db import models
from Main.models.payment_models import *
from Main.models.school_operations_models import *
from Main.models.transaction_records_models import *

class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ('transaction', 'Transaction'),
        ('payment', 'Payment'),
        ('school', 'School'),
        ('system', 'System'),
    ]

    sender = models.ForeignKey('Authentication.CustomUser', on_delete=models.CASCADE, blank=True, null=True)
    recipients = models.ManyToManyField('Authentication.CustomUser', related_name='notifications')
    recipients_viewed = models.ManyToManyField('Authentication.CustomUser', related_name='notifications_viewed')
    date_time = models.DateTimeField(auto_now=True)
    type_of_notification = models.CharField(max_length=255, choices=NOTIFICATION_TYPE_CHOICES)
    message = models.TextField()

    def __str__(self):
        recipients = ", ".join([str(recipient) for recipient in self.recipients.all()])
        return f'Sender: {self.sender}, Recipients: {recipients}'



class NotificationManager:
    @staticmethod
    def get_transaction_added_template(transaction):
        return f"New transaction added: {transaction.reason} for {transaction.amount} on {transaction.time.strftime('%Y-%m-%d %H:%M:%S')}."

    @staticmethod
    def get_transaction_edited_template(transaction, changed_fields):
        if not changed_fields:
            return f"Transaction edited: {transaction.reason} on {transaction.time.strftime('%Y-%m-%d %H:%M:%S')}."

        num_changes = len(changed_fields)
        return f"Transaction edited: {transaction.reason} - {num_changes} item{'s' if num_changes != 1 else ''} changed on {transaction.time.strftime('%Y-%m-%d %H:%M:%S')}."

    @staticmethod
    def get_transaction_deleted_template(transaction):
        return f"Transaction deleted: {transaction.reason} for {transaction.amount} on {transaction.time.strftime('%Y-%m-%d %H:%M:%S')}."

    @classmethod
    def create_notification(cls, notification_category, recipients, transaction, changed_fields=None):


        if notification_category['category'] == 'added':
            message = cls.get_transaction_added_template(transaction)
        elif notification_category['category'] == 'edited':
            message = cls.get_transaction_edited_template(transaction, changed_fields)
        elif notification_category['category'] == 'cancelled':
            message = cls.get_transaction_deleted_template(transaction)
        else:
            raise ValueError("Invalid notification type")

        notification_instance = Notification.objects.create(
            message=message,
            type_of_notification=notification_category['type_of_notification']
        )
        notification_instance.recipients.add(*recipients)
        notification_instance.save()

        return notification_instance
