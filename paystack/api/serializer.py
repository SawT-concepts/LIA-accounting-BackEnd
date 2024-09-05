from rest_framework import serializers
from paystack.models import DedicatedAccount

class DedicatedAccountSerializer(serializers.ModelSerializer):


    class Meta:
        model = DedicatedAccount
        fields = ("account_number", "bank_name", "bank_code", "account_name")
