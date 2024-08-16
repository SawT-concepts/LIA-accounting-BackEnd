from django.db import models
from Main.model_function.helper import *


message_reason = (
    ('CASH_REQUEST', 'CASH_REQUEST',)
)

class Message (models.Model):

    reason = models.CharField(max_length=40, choices=message_reason)
    message_text = models.TextField()
    date_time = models.DateTimeField(auto_now=True)
    reciever = models.ManyToManyField("Authentication.CustomUser")


    def __str__(self):
        short_reason = get_short_reason(self.reason)
        return short_reason
    




