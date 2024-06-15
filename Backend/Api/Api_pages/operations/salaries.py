from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import *
from Api.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, viewsets
from rest_framework.views import APIView
# from Background_Tasks.tasks import
from django.core.cache import cache
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from Main.models import Staff, Payroll
from Api.helper_functions.main import *
from Api.helper_functions.auth_methods import *
from Api.Api_pages.operations.serializers import *
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
from rest_framework.decorators import api_view
from Main.model_function.helper import generate_staffroll
from django.db import transaction
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

account_type = "OPERATIONS"


class GetAllStaffs(APIView):
    """
    API endpoint to get all the active staff.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Check if the authenticated user has the required account type.
            check_account_type(request.user, account_type)

            # Fetch the school associated with the requesting user.
            user_school = get_user_school(request.user)

            # Filter out the active staff members associated with the user's school.
            staffs_active_in_school = Staff.objects.filter(
                school=user_school, is_active=True)

            # Serialize the staff data for the response.
            serialized_data = StaffReadSerializer(
                staffs_active_in_school, many=True).data

            # Return the serialized staff data with a 200 OK status.
            return Response(serialized_data, status=HTTP_200_OK)

        except PermissionDenied:
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            # Handle specific API-related errors and return their details.
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            # For all other exceptions, return a generic error message.
            return Response({"message": "An error occurred"}, status=HTTP_403_FORBIDDEN)


class AddAndEditStaff (APIView):
    """
        this api is responsible for adding a new staff 
        this api is responsible for editing the details of the staff
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Check if the authenticated user has the required account type.
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
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            # Handle specific API-related errors and return their details.
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            # For all other exceptions, return a generic error message.
            return Response({"message": "An error occurred"}, status=HTTP_403_FORBIDDEN)

    def patch(self, request):
        try:
            # Check if the authenticated user has the required account type.
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
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            # Handle specific API-related errors and return their details.
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            # For all other exceptions, return a generic error message.
            return Response({"message": "An error occurred"}, status=HTTP_403_FORBIDDEN)


@api_view(['GET'])
def ShowStaffType(request):
    '''
        this API is responsible for getting the staff type
    '''
    try:
        check_account_type(request.user, account_type)
        user_school = get_user_school(request.user)

        staff_type = Staff_type.objects.filter(school=user_school)

        serialized_data = StaffTypeSerializer(staff_type, many=True).data

        return Response(serialized_data, status=HTTP_200_OK)

    except PermissionDenied:
        # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
        return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

    except APIException as e:
        # Handle specific API-related errors and return their details.
        return Response({"message": str(e.detail)}, status=e.status_code)

    except Exception as e:
        # For all other exceptions, return a generic error message.
        return Response({"message": "An error occurred"}, status=HTTP_403_FORBIDDEN)


class InitiatePayroll (APIView):
    '''
        -The Api is responsible for initiating payroll instance
        -(TODO) Also the would be a patch request to modify the staffs too
    '''
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
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
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            # Handle specific API-related errors and return their details.
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            # For all other exceptions, return a generic error message.
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class GetPayrollDetails (APIView):
    def get(self, request, payroll_id):
        try:
            check_account_type(request.user, account_type)
            payroll_instance = get_object_or_404(Payroll, id=payroll_id)

            serializer = PayrollSerializer(payroll_instance)
            return Response({"payroll": serializer.data}, status=status.HTTP_200_OK)

        except PermissionDenied:
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            # Handle specific API-related errors and return their details.
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            # For all other exceptions, return a generic error message.
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class InitiateTaxroll(APIView):
    """
    The API is responsible for initiating payroll instance.
    """

    def post(self, request, payroll_id, *args, **kwargs):
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
            return Response({"message": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateTransactionSummary (APIView):
    '''this api is responsible for returning a TransactionSummary from an existing payroll transaction'''

    def get(self, request, payroll_id, *args, **kwargs):
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
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            # Handle specific API-related errors and return their details.
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            # For all other exceptions, return a generic error message.
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class GetAllPayroll (APIView):
    '''this api is responsible for getting all SalaryPayments'''

    def get(self, request):
        try:
            check_account_type(self.request.user, account_type)
            user_school = get_user_school(self.request.user)
            payroll_list = Payroll.objects.filter(school=user_school.id)

            serializer = PayrollSerializer(data=payroll_list, many=True)

            # Return the serialized data in the response
            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            # Handle specific API-related errors and return their details.
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            # For all other exceptions, return a generic error message.
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class RequeryFailedPayrollTransaction (APIView):
    '''
        this api is responsible for requerying failed payments
    '''

    def post(self, request, payroll_id):
        payroll = get_object_or_404(Payroll, id=payroll_id)

        staffs_failed = payroll.get_all_failed_staff_payment()
        # todo:u Initiate bulk transaction and reupdate the staff payment status


class GetPayrollDetails (APIView):

    def get(self, request, payroll_id):
        try:
            check_account_type(self.request.user, account_type)
            payroll_instance = get_object_or_404(Payroll, id=payroll_id)

            serializer = PayrollDetailSerializer(payroll_instance)
            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            # Handle specific API-related errors and return their details.
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            # For all other exceptions, return a generic error message.
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class AddStaffToPayroll(APIView):
    def post(self, request, payroll_id):
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
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

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
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)
