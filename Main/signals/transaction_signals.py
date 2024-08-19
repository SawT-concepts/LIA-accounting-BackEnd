from django.dispatch import receiver
from Api.helper_functions.main import OperationType, update_operations_account
from Main.models.transaction_records_models import Operations_account_transaction_record
from django.db.models.signals import post_save




@receiver(post_save, sender=Operations_account_transaction_record)
def update_operations_account_on_transaction(sender, instance, created, **kwargs):
    """
    Signal receiver that updates the operations account based on the transaction record.
    Handles 'SUCCESS' and 'CANCELLED' statuses to update or reverse the transaction effect.

    Parameters:
        sender (Model): The model class that sent the signal.
        instance (Operations_account_transaction_record): The actual instance being saved.
        created (bool): A boolean indicating whether the instance was created.
        **kwargs: Additional keyword arguments.
    """

    if instance.status == "SUCCESS":
        # Determine the operation type based on transaction category
        operation_type = None
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

    elif instance.status == "CANCELLED":
        # Reverse the operation type based on transaction category
        reverse_operation_type = None
        if instance.transaction_category == "CREDIT":
            reverse_operation_type = OperationType.SUBTRACT.value
        elif instance.transaction_category == "DEBIT":
            reverse_operation_type = OperationType.ADD.value

        # If a reverse operation type is determined, update the operations account
        if reverse_operation_type:
            update_operations_account(
                amount=instance.amount,
                school_id=instance.school.id,
                operation_type=reverse_operation_type
            )
