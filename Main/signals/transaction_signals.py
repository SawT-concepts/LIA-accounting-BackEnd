from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from Api.helper_functions.main import OperationType, update_operations_account
from Authentication.models import CustomUser
from Main.models.notification_models import NotificationManager, Notification
from Main.models.transaction_records_models import Operations_account_transaction_modification_tracker, Operations_account_transaction_record, Operations_account_transaction_records_edited_fields


@receiver(pre_save, sender=Operations_account_transaction_record)
def track_previous_amount(sender, instance, **kwargs):
    """
    Track the previous amount and changes before saving the transaction.
    ☑️this works fine.. ive tested it
    """
    if instance.pk:
        try:
            old_instance = Operations_account_transaction_record.objects.get(pk=instance.pk,)
            Operations_account_transaction_modification_tracker.objects.filter(transaction=instance, status="PENDING").update(status="CANCELLED")
            tracker = Operations_account_transaction_modification_tracker.objects.create(
                transaction=instance,
                status="PENDING",
                head_teacher_comment=""
            )

            # Check for changes in specific fields
            fields_to_track = [field[0] for field in Operations_account_transaction_records_edited_fields.ATTRIBUTE_CHOICES]
            for field in fields_to_track:
                old_value = getattr(old_instance, field)
                new_value = getattr(instance, field)
                if old_value != new_value:
                    tracker.operations_account_transaction_records_edited_fields_set.create(
                        previous_state_attribute=field,
                        previous_state_value=str(old_value),
                        new_state_attribute=field,
                        new_state_value=str(new_value)
                    )

        except Operations_account_transaction_record.DoesNotExist:
            pass



@receiver(post_save, sender=Operations_account_transaction_record)
def update_operations_account_on_transaction(sender, instance, created, **kwargs):
    """
    Signal receiver that updates the operations account based on the transaction record.
    Handles 'SUCCESS', 'CANCELLED', 'PENDING_DELETE', and 'PENDING_EDIT' statuses
    to update or reverse the transaction effect.

    omo men😅... i dont even know wtf i had in mind while creating this function.
    its sha not working that was why i abandoned it!

    Parameters:
        sender (Model): The model class that sent the signal.
        instance (Operations_account_transaction_record): The actual instance being saved.
        created (bool): A boolean indicating whether the instance was created.
        **kwargs: Additional keyword arguments.
    """
    print("Alfred hichok")
    print(instance.status)
    notification_recipients = CustomUser.objects.filter(school=instance.school)

    if instance.status == "PENDING_APPROVAL" or instance.status == "PENDING_EDIT" or instance.status == "PENDING_DELETE":
        notification_recipients = notification_recipients.filter(account_type=CustomUser.ACCOUNT_TYPE_CHOICES[3][0])

    if instance.status == "CANCELLED" or instance.status == "SUCCESS":
        notification_recipients = notification_recipients.filter(account_type=CustomUser.ACCOUNT_TYPE_CHOICES[0][0])


    notification_category = {
        'type_of_notification': Notification.NOTIFICATION_TYPE_CHOICES[0][0],
        'category': 'edited' if instance.status == "PENDING_APPROVAL" or instance.status == "PENDING_EDIT" else 'cancelled' if instance.status == "CANCELLED" else 'success'
    }

    changed_fields = None
    if notification_recipients.exists():
        if hasattr(instance, '_tracker'):
            changed_fields = Operations_account_transaction_records_edited_fields.objects.filter(
                tracker=instance._tracker
            )

        # #todo--- Put this in a background task
        NotificationManager.create_notification(
            notification_category=notification_category,
            transaction=instance,
            recipients=notification_recipients,
            changed_fields=changed_fields
        )




            # update_operations_account(
            #     amount=instance.amount,
            #     school_id=instance.school.id,
            #     operation_type=operation_type
            # )
