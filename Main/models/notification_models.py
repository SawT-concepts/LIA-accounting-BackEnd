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

    sender = models.ForeignKey('Authentication.CustomUser', on_delete=models.CASCADE)
    recipients = models.ManyToManyField('Authentication.CustomUser', related_name='notifications')
    recipients_viewed = models.ManyToManyField('Authentication.CustomUser', related_name='notifications_viewed')
    date_time = models.DateTimeField(auto_now=True)
    type_of_notification = models.CharField(max_length=255, choices=NOTIFICATION_TYPE_CHOICES)
    message = models.TextField()

    def __str__(self):
        recipients = ", ".join([str(recipient) for recipient in self.recipient.all()])
        return f'Sender: {self.sender}, Recipients: {recipients}'



class NotificationManager:
    @staticmethod
    def get_transaction_added_template(transaction):
        return f"New transaction added: {transaction.reason} for {transaction.amount} on {transaction.time.strftime('%Y-%m-%d %H:%M:%S')}."

    @staticmethod
    def get_transaction_edited_template(transaction, changed_fields):
        changes = ", ".join([f"{field} changed to {getattr(transaction, field)}" for field in changed_fields])
        return f"Transaction edited: {transaction.reason} - {changes} on {transaction.time.strftime('%Y-%m-%d %H:%M:%S')}."

    @staticmethod
    def get_transaction_deleted_template(transaction):
        return f"Transaction deleted: {transaction.reason} for {transaction.amount} on {transaction.time.strftime('%Y-%m-%d %H:%M:%S')}."

    @classmethod
    def create_notification(cls, notification_type, sender, recipients, transaction, changed_fields=None):
        if notification_type == 'added':
            message = cls.get_transaction_added_template(transaction)
        elif notification_type == 'edited':
            message = cls.get_transaction_edited_template(transaction, changed_fields)
        elif notification_type == 'deleted':
            message = cls.get_transaction_deleted_template(transaction)
        else:
            raise ValueError("Invalid notification type")

        return Notification.objects.create(
            sender= sender,
            message=message,
            recipients=recipients,
            type_of_notification=notification_type
        )
