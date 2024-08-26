from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
# from Background_Tasks.tasks import
from django.shortcuts import get_object_or_404
from sps_authentication.utils.main import check_account_type
from sps_operations_account.api.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from typing import Any, Dict
from django.core.exceptions import PermissionDenied

from sps_operations_account.utils.main import get_cash_left_and_month_summary, get_user_school

account_type = "OPERATIONS"


class GetCashLeftInSafeAndCurrentMonthTransferSummary(APIView):
    '''
    This API is responsible for getting and calculating all the transfer amount spent in the current month
    and getting the total amount available to transfer
    '''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get cash left in safe and current month transfer summary",
        responses={200: CashTransactionDetailsSerializer()}
    )
    def get(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)
            data = get_cash_left_and_month_summary(user_school, transaction_type="TRANSFER")

            serializer = CashTransactionDetailsSerializer(data)
            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class GetAllTransferTransaction(APIView):
    '''
    This API is responsible for getting all the transfer transactions that have been made
    '''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all transfer transactions",
        manual_parameters=[
            openapi.Parameter('pending', openapi.IN_PATH, description="Filter by pending status", type=openapi.TYPE_STRING)
        ],
        responses={200: OperationsAccountCashTransactionRecordSerializer(many=True)}
    )
    def get(self, request: Any, pending: str) -> Response:
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            if pending == "pending":
               OperationsAccount_cash_transaction = OperationsAccountTransactionRecord.get_transaction(
                    school=user_school, transaction_type="TRANSFER"
                ).order_by('-time').filter(status="PENDING")
            else:
               OperationsAccount_cash_transaction = OperationsAccountTransactionRecord.get_transaction(
                    school=user_school, transaction_type="TRANSFER").order_by('-time').filter(status="SUCCESS")

            serializer = OperationsAccountCashTransactionRecordSerializer(
               OperationsAccount_cash_transaction, many=True)

            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class InititeTransferTransaction(APIView):
    '''
    This API is responsible for creating a transfer transaction and sending a notification
    to the directors
    '''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Initiate a transfer transaction",
        request_body=TransferTransactionWriteSerializer,
        responses={201: openapi.Response("Transfer transaction created successfully")}
    )
    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        try:
            check_account_type(request.user, account_type)
            serializer = TransferTransactionWriteSerializer(data=request.data)

            if serializer.is_valid():
                transfer_instance = serializer.save(commit=False)
                transfer_instance.transaction_category = "DEBIT"
                transfer_instance.school = get_user_school(request.user).id
                transfer_instance.transaction_type = "TRANSFER"
                transfer_instance.save()
                # TODO: Fire a notification

                return Response({"message": "Transfer transaction created successfully"}, status=HTTP_201_CREATED)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class EditTransferTransaction(APIView):
    '''
    This API is responsible for editing the transfer transaction
    '''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Edit a transfer transaction",
        request_body=TransferTransactionWriteSerializer,
        responses={200: openapi.Response("Transfer transaction updated successfully")}
    )
    def put(self, request: Any, transaction_id: int) -> Response:
        try:
            check_account_type(request.user, account_type)
            transaction = get_object_or_404(OperationsAccountTransactionRecord, id=transaction_id)
            serializer = TransferTransactionWriteSerializer(transaction, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Transfer transaction updated successfully"}, status=HTTP_200_OK)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)
