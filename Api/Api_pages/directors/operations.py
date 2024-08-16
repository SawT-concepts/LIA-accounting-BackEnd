from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import *
from Api.serializers import TokenObtainPairSerializer, ReceiptsSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status, viewsets
from rest_framework.views import APIView
# from Background_Tasks.tasks import
from django.core.cache import cache
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from Main.models import Payroll, Operations_account_transaction_record
from Api.helper_functions.main import *
from Api.helper_functions.auth_methods import *
from Api.helper_functions.directors.main import *
from Api.Api_pages.operations.serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from Paystack.transfers import *
from rest_framework import generics


account_type = "DIRECTOR"

'''
    SALARY AND PAYROLL
'''
class GetAllPayroll(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            payroll_list = Payroll.objects.filter(school=user_school.id)
            serialized_data = PayrollSerializer(payroll_list, many=True)

            return Response(serialized_data.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)


class ViewPayrollDetails (APIView):
    '''
        This would get the details of a particular payroll instance
    '''
    def get(self, request, payroll_id):
        try:
            check_account_type(request.user, account_type)    
            payroll_object = Payroll.objects.get(id=payroll_id)
            serialized_data = PayrollReadSerializer(data=payroll_object)


            return Response(serialized_data.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)



class ApprovePayroll (APIView):
    '''
        This API is responsible for the approval of salary payment after the operation accountant
        has processed it
    '''
    def post (self, request, payroll_id, *args, **kwargs):
        try:
            # Check if the authenticated user has the required account type.
            check_account_type(request.user, account_type)

            approval_data = request.data['status']
            payroll_instance = Payroll.objects.get(id=payroll_id)
            payroll_instance.status = (approval_data)
            payroll_instance.save()
    
            if approval_data == "INITIALIZED":
                #send a notification to the operations
                process_salary_payment(payroll_id)
                #todo [update payroll staff status]
             

            elif approval_data == "CANCELLED":
                #send a notification to the operations accountant 
                pass 

            return Response({"message": "cool"}, status=HTTP_200_OK)


        except PermissionDenied:
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            # Handle specific API-related errors and return their details.
            return Response({"message": str(e.detail)}, status=e.status_code)


        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)



class UpdateStaffPayroll(APIView):
    '''
        This is just supposed to be a webhook that updates the staff salary payment status from
        paystack verify payment webhook.
    '''

class VerifyPayroll (APIView):
    '''
        This would get all the staff instances in a payroll  and find the list of staff that hasn't been paid
    '''
    def post (self, request, payroll_id, *args, **kwargs):
        try:
            payroll_instance = get_object_or_404(Payroll, id=payroll_id)
            staffs = payroll_instance.staffs

            

            # return the summary (summary of all the staffs that have been paid)
            # return the total number of staffs that haven't been paid
            # 

            pass


        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)



'''
    TRANSFERS
'''
class ApproveTransfer (APIView):
    '''
        This would get the transaction from the operations account and there would be a desicion of
        either approval or rejection of the transaction
    '''
    def post (self, request, transaction_id):

        data = request.data
        try:
            check_account_type(request.user, account_type)
            transaction_record = Operations_account_transaction_record.objects.get(id=transaction_id)

            if data['status'] == "APPROVED":
                transaction_data = {
                    "amount" : transaction_record.amount,
                    "reason": transaction_record.reason,
                    "reference": transaction_record.reference,
                    "reciepient": transaction_record.customer_transaction_id
                }
                process_transaction(transaction_data)
                #todo [update the DB]
            else:
                '''update the db for canceled transactions'''

            return Response({"message": "cool"}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)



class TransferFromCapitalAccountToOperationAccount(APIView):
    def post(self, request):
        data = request.data
        transfer_amount = data.get('transfer_amount')

        if transfer_amount is None or not isinstance(transfer_amount, int) or transfer_amount <= 0:
            return Response({"message": "Invalid transfer amount provided."}, status=HTTP_400_BAD_REQUEST)

        try:
            account_type = "expected_account_type"  # Define the expected account type
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            capital_account = Capital_Account.objects.get(school=user_school)
            capital_account.transfer_to_operations_account(transfer_amount=transfer_amount)

            return Response({"message": "Transfer successful."}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except Capital_Account.DoesNotExist:
            return Response({"message": "Capital account does not exist for the user's school."}, status=HTTP_404_NOT_FOUND)

        except Operations_account.DoesNotExist:
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