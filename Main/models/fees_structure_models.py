from django.db import models
from Main.configuration import *


class PaymentStatus (models.Model):
    student = models.OneToOneField("Main.Student", on_delete=models.CASCADE)
    status = models.CharField(choices=fee_status, max_length=50, default=fee_status[1][1])
    last_amount_paid = models.BigIntegerField(default=0)
    amount_in_debt = models.BigIntegerField(default=0)
    amount_outstanding = models.BigIntegerField(default=0)

    def __str__(self):
        return f'{self.student} payment status'
    


class PaymentHistory (models.Model):
    Status_choice = (
        ("PENDING", "PENDING"),
        ("INITIALIZED", "INITIALIZED"),
        ("SUCCESS", "SUCCESS"),
        ("FAILED", "FAILED"),
        ("CANCELLED", "CANCELLED"),
        ("RETRYING", "RETRYING"),
    )

    student = models.ForeignKey("Main.Student",  on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date_time_initiated = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    merchant_email = models.EmailField()
    school = models.ForeignKey("Main.School", on_delete=models.CASCADE)

    amount_debited = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=Status_choice)


    receipt_id = models.CharField(max_length=20)
    paystack_reference = models.CharField(max_length=50)


    breakdowns = models.JSONField()

    def __str__(self):
        return f'{self.student} payment reciept'
    
    #function to generate the amount debited from the JSON object
    #function to generate the name of the payment reciept
    #function to get the last payment reciept


'''
- the breakdown structure (JSON)
- add the grade section model method 
- test the models in admin agressive testing
- 
'''