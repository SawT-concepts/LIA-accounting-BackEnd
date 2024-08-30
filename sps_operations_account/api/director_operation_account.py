from typing import List, Dict, Any
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from sps_authentication.utils.main import check_account_type
from sps_central_account.models import CapitalAccount, Receipts
from sps_core.utils.main import process_salary_payment
from sps_operations_account.api.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from paystack.transfers import *
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from sps_operations_account.utils.main import get_user_school


account_type = "DIRECTOR"

'''
    SALARY AND PAYROLL
'''
class GetAllPayroll(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all payroll records for the user's school",
        responses={200: PayrollSerializer(many=True)}
    )
    def get(self, request) -> Response:
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            payroll_list: List[Payroll] = Payroll.objects.filter(school=user_school.id)
            serialized_data = PayrollSerializer(payroll_list, many=True)

            return Response(serialized_data.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class ViewPayrollDetails(APIView):
    '''
        This would get the details of a particular payroll instance
    '''
    @swagger_auto_schema(
        operation_description="Get details of a specific payroll",
        responses={200: PayrollReadSerializer()}
    )
    def get(self, request, payroll_id: int) -> Response:
        try:
            check_account_type(request.user, account_type)
            payroll_object: Payroll = Payroll.objects.get(id=payroll_id)
            serialized_data = PayrollReadSerializer(data=payroll_object)

            return Response(serialized_data.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class ApprovePayroll(APIView):
    '''
        This API is responsible for the approval of salary payment after the operation accountant
        has processed it
    '''
    @swagger_auto_schema(
        operation_description="Approve or cancel a payroll",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, description="Approval status")
            }
        ),
        responses={200: openapi.Response(description="Payroll processed successfully")}
    )
    def post(self, request, payroll_id: int, *args, **kwargs) -> Response:
        try:
            check_account_type(request.user, account_type)

            approval_data: str = request.data['status']
            payroll_instance: Payroll = Payroll.objects.get(id=payroll_id)
            payroll_instance.status = approval_data
            payroll_instance.save()

            if approval_data == "INITIALIZED":
                process_salary_payment(payroll_id)
            elif approval_data == "CANCELLED":
                pass

            return Response({"message": "Payroll processed successfully"}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateStaffPayroll(APIView):
    '''
        This is just supposed to be a webhook that updates the staff salary payment status from
        paystack verify payment webhook.
    '''
    pass


class VerifyPayroll(APIView):
    '''
        This would get all the staff instances in a payroll and find the list of staff that hasn't been paid
    '''
    @swagger_auto_schema(
        operation_description="Verify payroll and get summary of paid and unpaid staff",
        responses={200: openapi.Response(description="Payroll verification summary")}
    )
    def post(self, request, payroll_id: int, *args, **kwargs) -> Response:
        try:
            payroll_instance: Payroll = get_object_or_404(Payroll, id=payroll_id)
            staffs: List[Dict[str, Any]] = payroll_instance.staffs

            # TODO: Implement the logic to summarize paid and unpaid staff

            return Response({"message": "Payroll verification completed"}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


'''
    TRANSFERS
'''
class ApproveTransfer(APIView):
    '''
        This would get the transaction from the operations account and there would be a decision of
        either approval or rejection of the transaction
    '''
    @swagger_auto_schema(
        operation_description="Approve or reject a transfer",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'status': openapi.Schema(type=openapi.TYPE_STRING, description="Approval status")
            }
        ),
        responses={200: openapi.Response(description="Transfer processed successfully")}
    )
    def post(self, request, transaction_id: int) -> Response:
        data: Dict[str, Any] = request.data
        try:
            check_account_type(request.user, account_type)
            transaction_record: OperationsAccountTransactionRecord = OperationsAccountTransactionRecord.objects.get(id=transaction_id)

            if data['status'] == "APPROVED":
                transaction_data: Dict[str, Any] = {
                    "amount": transaction_record.amount,
                    "reason": transaction_record.reason,
                    "reference": transaction_record.reference,
                    "recipient": transaction_record.customer_transaction_id
                }
                process_transaction(transaction_data)
                # TODO: Update the DB
            else:
                # TODO: Update the DB for canceled transactions
                pass

            return Response({"message": "Transfer processed successfully"}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class TransferFromCapitalAccountToOperationAccount(APIView):
    @swagger_auto_schema(
        operation_description="Transfer funds from capital account to operations account",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'transfer_amount': openapi.Schema(type=openapi.TYPE_INTEGER, description="Amount to transfer")
            }
        ),
        responses={200: openapi.Response(description="Transfer successful")}
    )
    def post(self, request) -> Response:
        data: Dict[str, Any] = request.data
        transfer_amount: int = data.get('transfer_amount')

        if transfer_amount is None or not isinstance(transfer_amount, int) or transfer_amount <= 0:
            return Response({"message": "Invalid transfer amount provided."}, status=HTTP_400_BAD_REQUEST)

        try:
            account_type: str = "expected_account_type"  # Define the expected account type
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            capital_account: CapitalAccount = CapitalAccount.objects.get(school=user_school)
            capital_account.transfer_to_operations_account(transfer_amount=transfer_amount)

            return Response({"message": "Transfer successful."}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except CapitalAccount.DoesNotExist:
            return Response({"message": "Capital account does not exist for the user's school."}, status=HTTP_404_NOT_FOUND)

        except OperationsAccount.DoesNotExist:
            return Response({"message": "Operations account does not exist for the user's school."}, status=HTTP_404_NOT_FOUND)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except ValueError as e:
            return Response({"message": str(e)}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class ReceiptsListView(generics.ListAPIView):
    queryset = Receipts.objects.all()
    serializer_class = ReceiptsSerializer

    @swagger_auto_schema(
        operation_description="Get a list of all receipts",
        responses={200: ReceiptsSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs) -> Response:
        return super().get(request, *args, **kwargs)
