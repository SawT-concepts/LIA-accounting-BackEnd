
from django.db import models

from datetime import datetime
from Paystack.service import *
from Main.model_function.helper import generate_transaction_reference

class Operations_account_transaction_record(models.Model):

    Transaction_type = (
        ("TRANSFER", "TRANSFER"),
        ("CASH", "CASH"),
    )
    Transaction_category = (
        ("CREDIT", "CREDIT"),
        ("DEBIT", "DEBIT"),
    )
    Status_choice = (
        ("PENDING_APPROVAL", "PENDING_APPROVAL"),
        ("PENDING_EDIT", "PENDING_EDIT"),
        ("PENDING_DELETE", "PENDING_DELETE"),
        ("INITIALIZED", "INITIALIZED"),
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
        ("CANCELLED", "CANCELLED"),
        ("RETRYING", "RETRYING"),
    )

    time = models.DateTimeField(default=datetime.now)
    amount = models.BigIntegerField()

    transaction_type = models.CharField(
        max_length=100, choices=Transaction_type)
    status = models.CharField(choices=Status_choice,
                              max_length=50, default="PENDING")
    transaction_category = models.CharField(
        max_length=50, choices=Transaction_category)
    particulars = models.ForeignKey(
        "Main.Particulars", on_delete=models.CASCADE)
    reason = models.TextField(null=True)

    school = models.ForeignKey("Main.School", on_delete=models.CASCADE)

    name_of_reciever = models.CharField(
        max_length=100, blank=False, null=False)
    account_number_of_reciever = models.CharField(
        max_length=20, null=True, blank=True)
    bank = models.ForeignKey("Paystack.Bank",  on_delete=models.CASCADE, blank=True, null=True)

    #paystack
    customer_transaction_id = models.CharField(max_length=50, null=True, blank=True)
    reference = models.CharField( blank=True, max_length=50)


    # ? Methods

    @staticmethod
    def get_transaction(transaction_type=None, transaction_category=None, start_date=None, end_date=None, status=None, school=None):
        query = Operations_account_transaction_record.objects.all()

        if transaction_type:
            query = query.filter(transaction_type=transaction_type)

        if transaction_category:
            query = query.filter(transaction_category=transaction_category)

        if start_date:
            query = query.filter(time__date__gte=start_date)

        if end_date:
            query = query.filter(time__date__lte=end_date)

        if status:
            query = query.filter(status=status)

        if school:
            query = query.filter(school=school)

        return query

    def save(self, *args, **kwargs):
        # Check if it's a "Transfer" transaction type
        if self.transaction_type == "TRANSFER":

            # Check if account number and receiver name are provided and raise validation error
            if not self.account_number_of_reciever and not self.name_of_reciever:
                raise ValueError(
                    "Both account number and receiver name must be provided for a Transfer transaction.")

            if not self.customer_transaction_id:
                #generate customer transaction ID
                transction_id = generate_paystack_id(self, full_name_present=True)
                self.customer_transaction_id  = transction_id['data']


            if not self.reference:
                #generate transaction refrence number
                self.reference = generate_transaction_reference()


        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.reason}' f'{self.transaction_type} transaction {self.school.name}'


class Operations_account_transaction_modification_tracker (models.Model):
    transaction = models.OneToOneField(Operations_account_transaction_record, on_delete=models.CASCADE)


class Operations_account_transaction_records_edited_fields (models.Model):
    ATTRIBUTE_CHOICES = (
        ("amount", "amount"),
        ("particulars", "particulars"),
        ("reason", "reason"),
        ("name_of_reciever", "name_of_reciever"),
        ("account_number_of_reciever", "account_number_of_reciever"),
        ("bank", "bank"),
    )

    previous_state_attribute = models.CharField(max_length=50, choices=ATTRIBUTE_CHOICES)
    previous_state_value = models.CharField( max_length=50)
    new_state_attribute = models.CharField(max_length=50, choices=ATTRIBUTE_CHOICES)
    new_state_value = models.CharField(max_length=50)
    tracker = models.ForeignKey(Operations_account_transaction_modification_tracker, on_delete=models.CASCADE)
    date_of_modification = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.previous_state_attribute} {self.previous_state_value} {self.new_state_attribute} {self.new_state_value}'





class Capital_account_transaction_record (models.Model):
    Transaction_category = (
        ("CREDIT", "CREDIT"),
        ("DEBIT", "DEBIT"),
    )
    time = models.DateTimeField(auto_now_add=True)
    amount = models.BigIntegerField()
    school = models.ForeignKey("Main.School", on_delete=models.CASCADE)


class Particulars (models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey("Main.School", on_delete=models.CASCADE)

    def __str__(self):
        return self.name
