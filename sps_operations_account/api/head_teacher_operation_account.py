from typing import Any, Dict, List
from rest_framework.response import Response
from rest_framework.status import *
from sps_authentication.utils.main import check_account_type
from sps_operations_account.api.serializers import  OperationsAccountCashTransactionRecordSerializer, TransactionModificationReadSerializer
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import InvalidPage
from rest_framework.views import APIView
# from Background_Tasks.tasks import
from django.shortcuts import get_object_or_404
from sps_operations_account.models import OperationsAccountTransactionRecord, OperationsAccountTransactionModificationTracker
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied
from django.db import models
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from sps_operations_account.utils.main import get_user_school

account_type: str = "PRINCIPAL"


class HeadTeacherGetAllPendingTransactionModification(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all pending transaction modifications for the head teacher's school",
        responses={
            200: TransactionModificationReadSerializer(many=True),
            401: 'Unauthorized',
            500: 'Internal Server Error'
        }
    )
    def get(self, request: Any) -> Response:
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)
            pending_transaction_list: List[OperationsAccountTransactionModificationTracker] = OperationsAccountTransactionModificationTracker.objects.filter(
                transaction__school=user_school, status="PENDING")
            serializer = TransactionModificationReadSerializer(
                pending_transaction_list, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class HeadTeacherGetAllPendingTransaction(APIView):
    """
    API endpoint to get all pending cash transactions for the head teacher's school.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all pending cash transactions for the head teacher's school",
        responses={
            200: OperationsAccountCashTransactionRecordSerializer(many=True),
            401: 'Unauthorized',
            403: 'Forbidden',
            404: 'Not Found',
            500: 'Internal Server Error'
        }
    )
    def get(self, request) -> Response:
        try:
            # check_account_type(request.user, account_type)
            user_school: Any = get_user_school(request.user)

            if user_school is None:
                return Response({"message": "User school not found"}, status=HTTP_404_NOT_FOUND)

            pending_transaction_list: List[OperationsAccountTransactionRecord] = OperationsAccountTransactionRecord.objects.filter(
                school=user_school.id, transaction_type="CASH",
                status__in=["PENDING_APPROVAL", "PENDING_DELETE", "PENDING_EDIT"]
            ).order_by('-time')

            return self.paginate_and_serialize(request, pending_transaction_list)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"message": str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    def paginate_and_serialize(self, request, transactions):
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        paginator = PageNumberPagination()
        paginator.page_size = page_size

        try:
            paginated_transactions = paginator.paginate_queryset(transactions, request)
            serializer: OperationsAccountCashTransactionRecordSerializer = OperationsAccountCashTransactionRecordSerializer(
                paginated_transactions, many=True
            )
            return paginator.get_paginated_response(serializer.data)
        except InvalidPage:
            paginator.page = 1
            paginated_transactions = paginator.paginate_queryset(transactions, request)
            serializer: OperationsAccountCashTransactionRecordSerializer = OperationsAccountCashTransactionRecordSerializer(
                paginated_transactions, many=True
            )
            return paginator.get_paginated_response(serializer.data)



class TransactionStatus(models.TextChoices):
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'CANCELLED', 'Cancelled'
    # Add other statuses if needed


class HeadTeacherModifyTransaction(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Modify a transaction's status",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, description='New status for the transaction'),
            },
            required=['status']
        ),
        responses={
            200: 'OK',
            400: 'Bad Request',
            401: 'Unauthorized',
            404: 'Not Found'
        }
    )
    def post(self, request: Any, id: int) -> Response:
        user_school = get_user_school(request.user)
        data: Dict[str, Any] = request.data

        if not data or 'status' not in data:
            return Response({"message": "Status must be set"}, status=HTTP_400_BAD_REQUEST)

        status: str = data['status'].upper()

        if status not in TransactionStatus.values:
            return Response({"message": "Invalid status provided"}, status=HTTP_400_BAD_REQUEST)

        try:
            check_account_type(request.user, account_type)
            transaction_instance: OperationsAccountTransactionRecord = get_object_or_404(
                OperationsAccountTransactionRecord, id=id)

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

    @swagger_auto_schema(
        operation_description="Bulk modify transactions' status",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Transaction ID'),
                },
                required=['id']
            )
        ),
        responses={
            200: 'OK',
            400: 'Bad Request',
            401: 'Unauthorized'
        }
    )
    def post(self, request: Any, status: str) -> Response:
        modified_status: str = status.upper()
        if modified_status not in TransactionStatus.values:
            return Response({"message": "Invalid status"}, status=HTTP_400_BAD_REQUEST)

        data: List[Dict[str, Any]] = request.data
        if not data or not isinstance(data, list):
            return Response({"message": "Data must be a list of transactions"}, status=HTTP_400_BAD_REQUEST)

        try:
            check_account_type(request.user, account_type)

            for data_instance in data:
                id: int = data_instance.get('id')
                if not id:
                    continue

                transaction_instance: OperationsAccountTransactionRecord = OperationsAccountTransactionRecord.objects.filter(
                    id=id).first()

                if transaction_instance is None:
                    continue

                transaction_instance.status = modified_status
                transaction_instance.save()

            return Response({"message": "Transactions updated successfully"}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
