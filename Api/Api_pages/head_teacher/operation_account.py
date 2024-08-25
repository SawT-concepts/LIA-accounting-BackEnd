from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import *
from Api.Api_pages.operations.serializers import CashTransactionReadSerializer, TransactionModificationReadSerializer
from rest_framework import status, viewsets
from rest_framework.views import APIView
# from Background_Tasks.tasks import
from django.core.cache import cache
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from Main.models import Operations_account_transaction_record
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from Api.helper_functions.main import *
from django.db import models
account_type = "PRINCIPAL"


class HeadTeacherGetAllPendingTransactionModification(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)
            pending_transaction_list = Operations_account_transaction_modification_tracker.objects.filter(
                transaction__school=user_school, status="PENDING")
            serializer = TransactionModificationReadSerializer(
                pending_transaction_list, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class HeadTeacherGetAllPendingTransaction(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)
            pending_transaction_list = Operations_account_transaction_record.objects.filter(
                school=user_school, status=["PENDING_APPROVAL", "PENDING_EDIT", "PENDING_DELETE"], transaction_type="CASH")

            if pending_transaction_list is None:
                return Response(status=HTTP_404_NOT_FOUND, data={"message": "No pending transaction."})

            serializer = CashTransactionReadSerializer(
                pending_transaction_list, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)



class TransactionStatus(models.TextChoices):
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'CANCELLED', 'Cancelled'
    # Add other statuses if needed


class HeadTeacherModifyTransaction(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        user_school = get_user_school(request.user)
        data = request.data

        if not data or 'status' not in data:
            return Response({"message": "Status must be set"}, status=HTTP_400_BAD_REQUEST)

        status = data['status'].upper()

        if status not in TransactionStatus.values:
            return Response({"message": "Invalid status provided"}, status=HTTP_400_BAD_REQUEST)

        try:
            # account_type is not defined in the provided snippet.
            check_account_type(request.user, account_type)
            transaction_instance = get_object_or_404(
                Operations_account_transaction_record, id=id)

            transaction_instance.status = status

            # operation_type = "SUBTRACT" if status == TransactionStatus.SUCCESS else "SAFE"
            # update_operations_account(
            #     transaction_instance.amount, user_school.id, operation_type)

            transaction_instance.save()

            return Response(status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)


class HeadTeacherBulkModifyTransaction(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, status):
        modified_status = status.upper()
        if modified_status not in TransactionStatus.values:
            return Response({"message": "Invalid status"}, status=HTTP_400_BAD_REQUEST)

        data = request.data
        if not data or not isinstance(data, list):
            return Response({"message": "Data must be a list of transactions"}, status=HTTP_400_BAD_REQUEST)

        try:
            check_account_type(request.user, account_type)

            for data_instance in data:
                id = data_instance.get('id')
                if not id:
                    continue

                transaction_instance = Operations_account_transaction_record.objects.filter(
                    id=id).first()

                if transaction_instance is None:
                    continue

                transaction_instance.status = modified_status
                transaction_instance.save()

            return Response({"message": "Transactions updated successfully"}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
