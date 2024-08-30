from rest_framework.response import Response
from rest_framework.status import *
from rest_framework import status
from rest_framework.views import APIView
# from Background_Tasks.tasks import
from django.shortcuts import get_object_or_404
from paystack.service import resolve_bank_account
from sps_authentication.utils.main import check_account_type
from sps_operations_account.api.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.decorators import api_view

from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from typing import List, Dict, Any, Union

from sps_operations_account.models.operations_payment_models import Status
from sps_operations_account.utils.main import generate_staffroll, get_user_school

account_type = "OPERATIONS"


class GetAllStaffs(APIView):
    """
    API endpoint to get all the active staff.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get all active staff",
        responses={200: StaffReadSerializer(many=True)}
    )
    def get(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)
            staffs_active_in_school = Staff.objects.filter(
                school=user_school, is_active=True)
            serialized_data = StaffReadSerializer(
                staffs_active_in_school, many=True).data

            return Response(serialized_data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class AddAndEditStaff(APIView):
    """
    API endpoint for adding a new staff or editing staff details.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Add a new staff",
        request_body=StaffWriteSerializer,
        responses={201: openapi.Response("Staff created successfully")}
    )
    def post(self, request: Any) -> Response:
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            data = request.data
            serialized_data = StaffWriteSerializer(
                data=data, context={'request': request})

            if serialized_data.is_valid():
                verify_bank_account = resolve_bank_account(
                    serialized_data.validated_data['account_number'], serialized_data.validated_data['bank'].bank_code)

                if verify_bank_account is None:
                    return Response({"message": "Bank Account Details not recognized"}, status=HTTP_400_BAD_REQUEST)

                serialized_data.save(school=user_school)

                # todo: add notification
                return Response({"message": "Staff created successfully"}, status=HTTP_201_CREATED)
            return Response({"message": "Invalid details provided"}, status=HTTP_400_BAD_REQUEST)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Edit staff details",
        request_body=StaffWriteSerializer,
        responses={200: openapi.Response("Staff edited successfully")}
    )
    def patch(self, request: Any) -> Response:
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            data = request.data
            serialized_data = StaffWriteSerializer(data)

            if serialized_data.is_valid():
                serialized_data.save(school=user_school)

                # todo: add notification
                # todo: process a notification if salary deduction

                return Response({"message": "Staff edited successfully"}, status=HTTP_200_OK)
            return Response(serialized_data.errors, status=HTTP_400_BAD_REQUEST)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


@swagger_auto_schema(
    method='get',
    operation_description="Get staff types",
    responses={200: StaffTypeSerializer(many=True)}
)
@api_view(['GET'])
def ShowStaffType(request: Any) -> Response:
    '''
    API endpoint for getting the staff types.
    '''
    try:
        check_account_type(request.user, account_type)
        user_school = get_user_school(request.user)

        staff_type = StaffType.objects.filter(school=user_school)

        serialized_data = StaffTypeSerializer(staff_type, many=True).data

        return Response(serialized_data, status=HTTP_200_OK)

    except PermissionDenied:
        return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

    except APIException as e:
        return Response({"message": str(e.detail)}, status=e.status_code)

    except Exception as e:
        return Response({"message": "An error occurred"}, status=HTTP_403_FORBIDDEN)


class InitiatePayroll(APIView):
    '''
    API endpoint for initiating a payroll instance.
    '''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Initiate a new payroll",
        responses={201: PayrollWriteSerializer()}
    )
    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        try:
            check_account_type(request.user, account_type)
            payroll_name = Payroll.generate_payroll_name()
            user_school = get_user_school(request.user)
            staff_list = generate_staffroll(user_school)

            # create an async task here
            payroll = Payroll.objects.create(
                name=payroll_name, school=user_school)
            payroll.add_staff(staff_list)

            # delete other payrolls
            Payroll.objects.filter(
                name=payroll_name, school=user_school).delete()

            payroll.save()

            # Serialize the payroll data
            serializer = PayrollWriteSerializer(payroll)

            return Response({"message": "Payroll initiated successfully", "payroll": serializer.data}, status=status.HTTP_201_CREATED)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class GetPayrollDetails(APIView):
    @swagger_auto_schema(
        operation_description="Get details of a specific payroll",
        responses={200: PayrollSerializer()}
    )
    def get(self, request: Any, payroll_id: int) -> Response:
        try:
            check_account_type(request.user, account_type)
            payroll_instance = get_object_or_404(Payroll, id=payroll_id)

            serializer = PayrollSerializer(payroll_instance)
            return Response({"payroll": serializer.data}, status=status.HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class InitiateTaxroll(APIView):
    """
    API endpoint for initiating a taxroll instance from a payroll.
    """

    @swagger_auto_schema(
        operation_description="Initiate a taxroll from a payroll",
        responses={201: TaxRollReadSerializer()}
    )
    def post(self, request: Any, payroll_id: int, *args: Any, **kwargs: Any) -> Response:
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            taxroll_response = Taxroll.generate_taxroll_out_of_payroll(
                payroll_id, user_school)

            if taxroll_response['status'] == "SUCCESS":
                taxroll_instance = taxroll_response['data']

                # Serialize the taxroll_instance
                serialized_data = TaxRollReadSerializer(taxroll_instance)

                return Response(serialized_data.data, status=status.HTTP_201_CREATED)

            return Response({"message": taxroll_response['message']}, status=status.HTTP_404_NOT_FOUND if taxroll_response['code'] == "ERROR_404" else status.HTTP_502_BAD_GATEWAY)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateTransactionSummary(APIView):
    '''
    API endpoint for generating a transaction summary from an existing payroll transaction.
    '''

    @swagger_auto_schema(
        operation_description="Generate transaction summary for a payroll",
        responses={200: TransactionSummarySerializer()}
    )
    def get(self, request: Any, payroll_id: int, *args: Any, **kwargs: Any) -> Response:
        try:
            check_account_type(request.user, account_type)
            payroll_instance = get_object_or_404(Payroll, id=payroll_id)
            total_amount_paid = payroll_instance.get_total_salary_paid()
            total_tax_paid = payroll_instance.get_total_tax_paid()
            summary = payroll_instance.get_payment_summary()
            # todo: Add the total transfer list for all the staffs paid (total amount)

            # Create an instance of the serializer with the response data
            serializer = TransactionSummarySerializer({
                "amount_paid": total_amount_paid,
                "total_tax_paid": total_tax_paid,
                "total_staffs": summary['total_staffs']
            })

            # Return the serialized data in the response
            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class OperationsGetAllPayroll(APIView):
    '''
    API endpoint for getting all salary payments.
    '''

    @swagger_auto_schema(
        operation_description="Get all payrolls",
        responses={200: PayrollSerializer(many=True)}
    )
    def get(self, request: Any) -> Response:
        try:
            check_account_type(self.request.user, account_type)
            user_school = get_user_school(self.request.user)
            payroll_list = Payroll.objects.filter(school=user_school.id)
            serializer = PayrollSerializer(payroll_list, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred: " + str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class ReQueryFailedPayrollTransaction(APIView):
    '''
    API endpoint for requerying failed payments.
    '''

    @swagger_auto_schema(
        operation_description="Requery failed payroll transactions",
        responses={200: openapi.Response("Requery successful")}
    )
    def post(self, request: Any, payroll_id: int) -> Response:
        payroll = get_object_or_404(Payroll, id=payroll_id)

        staffs_failed = payroll.get_all_failed_staff_payment()
        # todo: Initiate bulk transaction and reupdate the staff payment status
        return Response({"message": "Requery initiated"}, status=HTTP_200_OK)


class AddStaffToPayroll(APIView):
    @swagger_auto_schema(
        operation_description="Add a staff to a payroll",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'staff_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={200: openapi.Response("Staff Added")}
    )
    def post(self, request: Any, payroll_id: int) -> Response:
        try:
            check_account_type(self.request.user, account_type)
            staff_id = request.data.get('staff_id')
            if not staff_id or not isinstance(staff_id, int):
                return Response({"message": "Invalid staff ID"}, status=HTTP_400_BAD_REQUEST)

            # Check user permissions
            check_account_type(self.request.user, account_type)

            # Retrieve instances
            staff_instance = get_object_or_404(Staff, id=staff_id)
            payroll_instance = get_object_or_404(Payroll, id=payroll_id)

            # Prepare staff data to add to payroll
            staff_data_list = [
                {
                    "staff_firstname": staff_instance.first_name,
                    "staff_id": staff_instance.id,
                    "rank": staff_instance.staff_type.name,
                    "tax": staff_instance.staff_type.tax,
                    "basic_salary": staff_instance.staff_type.basic_salary,
                    "deduction": staff_instance.salary_deduction,
                    "salary_to_be_paid": staff_instance.staff_type.basic_salary - staff_instance.staff_type.tax - staff_instance.salary_deduction,
                    "account_number": staff_instance.account_number,
                    "bank": staff_instance.bank.name,
                    "account_name": f"{staff_instance.first_name} {staff_instance.last_name}",
                    "payment_status": "PENDING",
                },
            ]

            # Add staff to payroll inside a transaction
            with transaction.atomic():
                payroll_instance.add_staff(staff_data_list)
                payroll_instance.save()  # Ensure changes are saved

            return Response({"message": "Staff Added"}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class RemoveStaffFromPayroll(APIView):
    def post(self, request, payroll_id):
        try:
            check_account_type(self.request.user, account_type)
            staff_id = request.data.get('staff_id')
            payroll_instance = get_object_or_404(Payroll, id=payroll_id)

            staff_removed = payroll_instance.remove_staff_by_id(staff_id)
            payroll_instance.save()
            serializer = PayrollSerializer(payroll_instance)
            if staff_removed:

                # Notify WebSocket group
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'payroll_updates',
                    {
                        "type": "payroll_update",
                        "message": "Staff Removed"
                    }
                )

                return Response({"message": "Staff Removed", "payroll": serializer.data}, status=HTTP_200_OK)
            else:
                return Response({"message": "Staff not found in payroll"}, status=HTTP_404_NOT_FOUND)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)



class ProcessPayrollAndTax (APIView):
    def post (self, request, payroll_id):
        try:
            check_account_type(self.request.user, account_type)
            payroll_instance = get_object_or_404(Payroll, id=payroll_id)
            taxroll_instance = get_object_or_404(Taxroll, payroll= payroll_id)

            payroll_instance.status = Status[1][1]
            taxroll_instance.status = Status[1][1]

            payroll_instance.save()
            taxroll_instance.save()

            return Response({"message": "Payroll processed"}, status=HTTP_200_OK)


        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)
