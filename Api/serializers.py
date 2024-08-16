from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as JwtTokenObtainPairSerializer
from django.contrib.auth import get_user_model
from Main.models import Receipts
from rest_framework import serializers


class TokenObtainPairSerializer(JwtTokenObtainPairSerializer):
    username_field = get_user_model().USERNAME_FIELD




class ReceiptsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipts
        fields = '__all__'