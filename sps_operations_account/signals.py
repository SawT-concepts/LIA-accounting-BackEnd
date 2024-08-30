from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from sps_authentication.models import CustomUser
from sps_notifications.models import Notification, NotificationManager
from django.db import transaction
from sps_operations_account.models import OperationsAccountTransactionModificationTracker, OperationsAccountTransactionRecord, OperationsAccountTransactionRecordsEditedField
from sps_operations_account.models.main_models import OperationsAccount



@receiver(pre_save, sender=OperationsAccountTransactionRecord)
def track_previous_amount(sender, instance, **kwargs):
    """
    Track the previous amount and changes before saving the transaction.
    """
    if instance.pk:
        try:
            old_instance = OperationsAccountTransactionRecord.objects.get(pk=instance.pk)
            pending_tracker = OperationsAccountTransactionModificationTracker.objects.filter(
                transaction=instance, status="PENDING"
            ).first()

            pending_edited_fields = OperationsAccountTransactionRecordsEditedField.objects.filter(
                tracker=pending_tracker
            ) if pending_tracker else OperationsAccountTransactionRecordsEditedField.objects.none()
            OperationsAccountTransactionModificationTracker.objects.filter(
                transaction=instance, status="PENDING"
            ).update(status="CANCELLED")
            new_tracker = OperationsAccountTransactionModificationTracker.objects.create(
                transaction=instance,
                status="PENDING",
                head_teacher_comment=""
            )
            fields_to_track = [field[0] for field in OperationsAccountTransactionRecordsEditedField.ATTRIBUTE_CHOICES]
            for field in fields_to_track:
                old_value = getattr(old_instance, field)
                new_value = getattr(instance, field)
                if str(old_value) != str(new_value):
                    previous_edit = pending_edited_fields.filter(new_state_attribute=field).first()

                    if previous_edit and previous_edit.new_state_value == str(new_value):
                        previous_edit.tracker = new_tracker
                        previous_edit.save()
                    else:
                        OperationsAccountTransactionRecordsEditedField.objects.create(
                            tracker=new_tracker,
                            previous_state_attribute=field,
                            previous_state_value=str(old_value),
                            new_state_attribute=field,
                            new_state_value=str(new_value)
                        )
                        if previous_edit:
                            previous_edit.delete()
                else:
                    if pending_tracker:
                        previous_edit = pending_edited_fields.filter(new_state_attribute=field).first()
                        if previous_edit:
                            previous_edit.tracker = new_tracker
                            previous_edit.save()

        except OperationsAccountTransactionRecord.DoesNotExist:
            pass

@receiver(pre_save, sender=OperationsAccountTransactionRecord)
def update_operations_account_on_transaction(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        with transaction.atomic():
            previous_instance = OperationsAccountTransactionRecord.objects.select_for_update().get(pk=instance.pk)
            previous_amount = OperationsAccountTransactionRecordsEditedField.objects.filter(
                tracker__transaction=instance,
                tracker__status="PENDING",
                new_state_attribute="amount"
            ).order_by('-date_of_modification').first()

            if previous_amount:
                previous_amount = float(previous_amount.previous_state_value)
            else:
                previous_amount = previous_instance.amount

            operations_account = OperationsAccount.objects.select_for_update().get(school=instance.school)

            if instance.status == 'SUCCESS':
                if previous_instance.status == 'PENDING_EDIT':
                    # Revert the previous amount and apply the new amount
                    operations_account.amount_available_cash += previous_amount
                    operations_account.amount_available_cash -= instance.amount
                elif previous_instance.status == 'PENDING_DELETE':
                    # Revert the previous amount and cancel the instance
                    operations_account.amount_available_cash += previous_amount
                    instance.status = 'CANCELLED'
                elif previous_instance.status == 'PENDING_APPROVAL':
                    # Deduct the new amount
                    operations_account.amount_available_cash -= instance.amount
                operations_account.save()

            elif instance.status == 'CANCELLED':
                if previous_instance.status != 'PENDING_APPROVAL':
                    instance.status = 'SUCCESS'



    except OperationsAccountTransactionRecord.DoesNotExist:
        print("OperationsAccountTransactionRecord does not exist")
    except OperationsAccount.DoesNotExist:
        print("OperationsAccount does not exist")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


@receiver(post_save, sender=OperationsAccountTransactionRecord)
def update_notifications_on_transaction(sender, instance, created, **kwargs):
    """
    Signal receiver that updates the operations account based on the transaction record.
    Handles 'SUCCESS', 'CANCELLED', 'PENDING_DELETE', and 'PENDING_EDIT' statuses
    to update or reverse the transaction effect.

    omo men😅... i dont even know wtf i had in mind while creating this function.
    its sha not working that was why i abandoned it!

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
