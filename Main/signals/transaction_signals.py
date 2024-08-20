from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from Api.helper_functions.main import OperationType, update_operations_account
from Main.models.transaction_records_models import Operations_account_transaction_record

@receiver(pre_save, sender=Operations_account_transaction_record)
def track_previous_amount(sender, instance, **kwargs):
    """
    Track the previous amount before saving the transaction to handle the PENDING_EDIT status.
    """
    if instance.pk:
        try:
            # Get the previous instance before the update
            previous_instance = sender.objects.get(pk=instance.pk)
            instance._previous_amount = previous_instance.amount
        except sender.DoesNotExist:
            instance._previous_amount = 0
    else:
        instance._previous_amount = 0

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
        print("Instance is being deleted")
        # First, add back the previous amount
        update_operations_account(
            amount=instance._previous_amount,
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
