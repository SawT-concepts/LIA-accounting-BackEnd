from django.db import models
from django.core.exceptions import ObjectDoesNotExist


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
    
class Operations_account(models.Model):
    name = models.CharField(max_length=100, verbose_name="Bank Account Name")
    account_number = models.CharField(max_length=100, verbose_name="Account Number")
    school = models.OneToOneField("Main.School", on_delete=models.CASCADE)
    amount_available_cash = models.BigIntegerField()
    amount_available_transfer = models.BigIntegerField()

    def get_total_amount_available(self):
        return self.amount_available_cash + self.amount_available_transfer

    def deduct_operations_account(self, deduction_amount):
        total_amount = self.get_total_amount_available()
        if deduction_amount > total_amount:
            raise ValueError("Deduction amount exceeds total available funds.")
        
        if deduction_amount <= self.amount_available_cash:
            self.amount_available_cash -= deduction_amount
        else:
            deduction_from_transfer = deduction_amount - self.amount_available_cash
            self.amount_available_cash = 0
            self.amount_available_transfer -= deduction_from_transfer

        self.save()

    def fund_operations_account(self, additional_amount_cash=0, additional_amount_transfer=0):
        self.amount_available_cash += additional_amount_cash
        self.amount_available_transfer += additional_amount_transfer
        self.save()

    def __str__(self):
        return f'{self.school.name} Operation account'


class Capital_Account(models.Model):
    name = models.CharField(max_length=100, verbose_name="Bank Account Name")
    account_number = models.CharField(max_length=100, verbose_name="Account Number")
    school = models.OneToOneField("Main.School", on_delete=models.CASCADE)
    amount_availabe = models.BigIntegerField()

    def transfer_to_operations_account(self, transfer_amount):
        if transfer_amount > self.amount_availabe:
            raise ValueError("Transfer amount exceeds available capital funds.")
        
        try:
            operations_account = Operations_account.objects.get(school=self.school)
        except ObjectDoesNotExist:
            raise ValueError("Operations account does not exist for this school.")

        self.amount_availabe -= transfer_amount
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
