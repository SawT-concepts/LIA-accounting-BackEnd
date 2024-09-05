from django.db import models
from django.contrib.auth.models import User
from .service import get_banks_from_paystack
import time

# Create your models here.
class Bank (models.Model):
    name = models.CharField(max_length=50)
    bank_code = models.CharField(max_length=10)
    slug = models.CharField(max_length=50)
    bank_type = models.CharField(max_length=40)
    currency = models.CharField(max_length=10)


    def __str__(self):
        return self.name

    @staticmethod
    def update_bank_from_paystack ():
        returned_banks = get_banks_from_paystack()

        for bank in returned_banks:
            bank_instance = Bank.objects.create (
                name=bank['name'],
                bank_code=bank['code'],
                slug=bank['slug'],
                bank_type=bank['type'],
                currency= bank['currency']
            )
            bank_instance.save()
            print(f"Added bank {bank['name']}")



class DedicatedAccount (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=10)
    account_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=10)
    bank_code = models.CharField(max_length=10)
    bank_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.account_number
