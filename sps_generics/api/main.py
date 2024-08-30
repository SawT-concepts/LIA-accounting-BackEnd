from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from paystack.service import resolve_bank_account
from sps_authentication.utils.main import check_account_type
from sps_operations_account.api.serializers import BankSerializer, ParticularSerializer, RankSerializer
from sps_operations_account.utils.main import get_all_banks, get_all_school_header, get_all_school_ranks, get_user_school
from django.core.exceptions import PermissionDenied


account_type = "OPERATIONS"


class FetchHeader(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            school_header = get_all_school_header(user_school)

            serializer = ParticularSerializer(
                school_header, many=True)

            return Response(serializer.data)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)


class GetRanks(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            school_ranks = get_all_school_ranks(user_school)

            serializer = RankSerializer(
                school_ranks, many=True)

            return Response(serializer.data)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)


class GetBanks(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            check_account_type(request.user, account_type)

            school_banks = get_all_banks()

            serializer = BankSerializer(
                school_banks, many=True)

            return Response(serializer.data)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)


class VerifyAccountNumber (APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            check_account_type(request.user, account_type)

            account_number = request.data['account_number']
            bank_code = request.data['bank_code']

            if not account_number or not bank_code:
                return Response({"message": "Account number and bank code are required"}, status=HTTP_400_BAD_REQUEST)

            response = resolve_bank_account(account_number, bank_code)

            if response:
                return Response({"data": response}, status=HTTP_200_OK)
            else:
                return Response({"message": "Invalid account number"}, status=HTTP_400_BAD_REQUEST)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
