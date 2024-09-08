from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from sps_authentication.models import CustomUser
from sps_notifications.models import Notification, NotificationManager
from sps_operations_account.models import OperationsAccountTransactionModificationTracker, OperationsAccountTransactionRecord, OperationsAccountTransactionRecordsEditedField




@receiver(post_save, sender=OperationsAccountTransactionRecord)
def update_notifications_on_transaction(sender, instance, created, **kwargs):
    """
    Parameters:
        sender (Model): The model class that sent the signal.
        instance (OperationsAccountTransactionRecord): The actual instance being saved.
        created (bool): A boolean indicating whether the instance was created.
        **kwargs: Additional keyword arguments.
    """
    notification_recipients = CustomUser.objects.filter(school=instance.school)

    if instance.status == "PENDING_APPROVAL" or instance.status == "PENDING_EDIT" or instance.status == "PENDING_DELETE":
        notification_recipients = notification_recipients.filter(account_type=CustomUser.ACCOUNT_TYPE_CHOICES[3][0])

    if instance.status == "CANCELLED" or instance.status == "SUCCESS":
        notification_recipients = notification_recipients.filter(account_type=CustomUser.ACCOUNT_TYPE_CHOICES[0][0])
        OperationsAccountTransactionModificationTracker.objects.filter(transaction=instance, status="PENDING").update(status="APPROVED")


    notification_category = {
        'type_of_notification': Notification.NOTIFICATION_TYPE_CHOICES[0][0],
        'category': 'edited' if instance.status == "PENDING_APPROVAL" or instance.status == "PENDING_EDIT" else 'cancelled' if instance.status == "CANCELLED" else 'success'
    }

    changed_fields = None
    if notification_recipients.exists():
        if hasattr(instance, '_tracker'):
            changed_fields = OperationsAccountTransactionRecordsEditedField.objects.filter(
                tracker=instance._tracker
            )

        # #todo--- Put this in a background task
        NotificationManager.create_notification(
            notification_category=notification_category,
            transaction=instance,
            recipients=notification_recipients,
            changed_fields=changed_fields
        )
