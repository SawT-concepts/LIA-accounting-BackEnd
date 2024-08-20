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
            pass  # This shouldn't happen, but just in case


@receiver(post_save, sender=Operations_account_transaction_record)
def update_operations_account_on_transaction(sender, instance, created, **kwargs):
    """
    Signal receiver that updates the operations account based on the transaction record.
    Handles 'SUCCESS', 'CANCELLED', 'PENDING_DELETE', and 'PENDING_EDIT' statuses
    to update or reverse the transaction effect.

    Parameters:
        sender (Model): The model class that sent the signal.
        instance (Operations_account_transaction_record): The actual instance being saved.
        created (bool): A boolean indicating whether the instance was created.
        **kwargs: Additional keyword arguments.
    """
    operation_type = None
    notification_recipients = CustomUser.objects.filter(school=instance.school)

    if instance.status == Operations_account_transaction_record.Status_choice[0][0]:
        # Awaiting approval from the head teacher
        notification_recipients = notification_recipients.filter(account_type=CustomUser.ACCOUNT_TYPE_CHOICES[3][0])
        operation_type = OperationType.ADD.value

    elif instance.status in [Operations_account_transaction_record.Status_choice[3][0],  # PENDING_DELETE
                             Operations_account_transaction_record.Status_choice[4][0]]: # PENDING_EDIT
        operation_type = OperationType.ADD.value
        notification_recipients = notification_recipients.filter(account_type=CustomUser.ACCOUNT_TYPE_CHOICES[3][0])

        if instance.status == Operations_account_transaction_record.Status_choice[4][0]:
            previous_amount = instance._previous_amount

            # Add back the previous amount
            update_operations_account(
                amount=previous_amount,
                school_id=instance.school.id,
                operation_type=OperationType.ADD.value
            )
            operation_type = OperationType.SUBTRACT.value

    elif instance.status == Operations_account_transaction_record.Status_choice[6][0]:  # CANCELLED
        operation_type = OperationType.ADD.value

    elif instance.status == Operations_account_transaction_record.Status_choice[5][0]:  # SUCCESS
        operation_type = OperationType.ADD.value if instance.transaction_category == Operations_account_transaction_record.Transaction_category[0][0] else OperationType.SUBTRACT.value

    if notification_recipients.exists():
        changed_fields = None
        if hasattr(instance, '_tracker'):
            changed_fields = Operations_account_transaction_records_edited_fields.objects.filter(
                tracker=instance._tracker
            )

        notification_category = {
            'type_of_notification': Notification.NOTIFICATION_TYPE_CHOICES[0][0]
        }

        if instance.status == Operations_account_transaction_record.Status_choice[5][0]:  # SUCCESS
            notification_category['category'] = 'success'
            notification_recipients = notification_recipients.filter(account_type=CustomUser.ACCOUNT_TYPE_CHOICES[0][0])
        elif instance.status == Operations_account_transaction_record.Status_choice[6][0]:  # CANCELLED
            notification_category['category'] = 'cancelled'
            notification_recipients = notification_recipients.filter(account_type=CustomUser.ACCOUNT_TYPE_CHOICES[0][0])
        else:
            notification_category['category'] = 'edited'

        # Put this in a background task
        NotificationManager.create_notification(
            notification_category=notification_category,
            transaction=instance,
            recipients=notification_recipients,
            changed_fields=changed_fields
        )

    # Update the operations account if an operation type is determined
    if operation_type:
        update_operations_account(
            amount=instance.amount,
            school_id=instance.school.id,
            operation_type=operation_type
        )
