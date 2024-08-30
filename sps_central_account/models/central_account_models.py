from django.db import models


from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from sps_operations_account.models import OperationsAccount


class Receipts(models.Model):
    title = models.CharField(max_length=300)
    transaction_id = models.AutoField(primary_key=True)
    from_account = models.CharField(max_length=100)
    to_account = models.CharField(max_length=100)
    amount = models.BigIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Save initially to get a transaction_id
        if not self.transaction_id:
            super(Receipts, self).save(*args, **kwargs)
        # Update title after getting the transaction_id
        self.title = f'Receipt {self.transaction_id}: {self.amount} transferred from {self.from_account} to {self.to_account}'
        super(Receipts, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class CapitalAccount(models.Model):
    name = models.CharField(max_length=100, verbose_name="Bank Account Name")
    account_number = models.CharField(max_length=100, verbose_name="Account Number")
    school = models.OneToOneField("sps_core.school", on_delete=models.CASCADE)
    amount_available = models.BigIntegerField(default=0)

    def transfer_to_operations_account(self, transfer_amount):
        if transfer_amount > self.amount_available:
            raise ValueError("Transfer amount exceeds available capital funds.")

        try:
           operations_account = OperationsAccount.objects.get(school=self.school)
        except ObjectDoesNotExist:
            raise ValueError("Operations account does not exist for this school.")

        self.amount_available -= transfer_amount
        operations_account.fund_operations_account(additional_amount_cash=transfer_amount)
        self.save()
        operations_account.save()

        # Create receipt
        Receipts.objects.create(
            from_account=self.account_number,
            to_account=operations_account.account_number,
            amount=transfer_amount,
            description=f'Transferred {transfer_amount} from capital to operations account for school {self.school.name}'
        )

    def __str__(self):
        return f'{self.school.name} Capital account'




# Create your models here.
class CapitalAccountTransactionRecord (models.Model):
    Transaction_category = (
        ("CREDIT", "CREDIT"),
        ("DEBIT", "DEBIT"),
    )
    time = models.DateTimeField(auto_now_add=True)
    amount = models.BigIntegerField()
    school = models.ForeignKey("sps_core.school", on_delete=models.CASCADE)
