from django.db import models
from django.core.exceptions import ObjectDoesNotExist




class OperationsAccount(models.Model):
    name = models.CharField(max_length=100, verbose_name="Bank Account Name")
    account_number = models.CharField(max_length=100, verbose_name="Account Number")
    school = models.OneToOneField("sps_core.school", on_delete=models.CASCADE)
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
