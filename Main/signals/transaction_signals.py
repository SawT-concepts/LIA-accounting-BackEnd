from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from Api.helper_functions.main import OperationType, update_operations_account
from Main.models.transaction_records_models import Operations_account_transaction_modification_tracker, Operations_account_transaction_record, Operations_account_transaction_records_edited_fields

@receiver(pre_save, sender=Operations_account_transaction_record)
def track_previous_amount(sender, instance, **kwargs):
    """
    Track the previous amount and changes before saving the transaction.
    """
    if not instance.pk:
        return

    try:
        previous_instance = sender.objects.get(pk=instance.pk)
        instance._previous_amount = previous_instance.amount

        fields_to_check = ['amount', 'particulars', 'reason', 'name_of_reciever', 'account_number_of_reciever', 'bank']
        changed_fields = [field for field in fields_to_check if getattr(previous_instance, field) != getattr(instance, field)]

        if changed_fields:
            tracker, _ = Operations_account_transaction_modification_tracker.objects.get_or_create(transaction=instance)

            for field in changed_fields:
                Operations_account_transaction_records_edited_fields.objects.create(
                    tracker=tracker,
                    previous_state_attribute=field,
                    previous_state_value=str(getattr(previous_instance, field)),
                    new_state_attribute=field,
                    new_state_value=str(getattr(instance, field))
                )
    except sender.DoesNotExist:
        pass

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

    # Handle PENDING_DELETE: Add the transaction amount back
    if instance.status == "PENDING_DELETE":
        operation_type = OperationType.ADD.value

    # Handle PENDING_EDIT: Add previous amount, then subtract the new amount
    elif instance.status == "PENDING_EDIT":
        tracker = Operations_account_transaction_modification_tracker.objects.get(transaction=instance)
        previous_amount = int(Operations_account_transaction_records_edited_fields.objects.get(
            tracker=tracker,
            previous_state_attribute='amount'
        ).previous_state_value)

        # First, add back the previous amount
        update_operations_account(
            amount=previous_amount,
            school_id=instance.school.id,
            operation_type=OperationType.ADD.value
        )
        # Then, subtract the new amount
        operation_type = OperationType.SUBTRACT.value

    # Handle SUCCESS: Add or subtract based on transaction category
    elif instance.status == "SUCCESS":
        if instance.transaction_category == "CREDIT":
            operation_type = OperationType.ADD.value
        elif instance.transaction_category == "DEBIT":
            operation_type = OperationType.SUBTRACT.value

    # If an operation type is determined, update the operations account
    if operation_type:
        update_operations_account(
            amount=instance.amount,
            school_id=instance.school.id,
            operation_type=operation_type
        )
