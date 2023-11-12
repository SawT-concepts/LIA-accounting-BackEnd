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
from Main.models import Operations_account, Operations_account_transaction_record
from Api.helper_functions.main import *
from Api.Api_pages.operations.serializers import *
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
account_type = "OPERATIONS"



class OperationsAccountIncomeLastSevenMonths(APIView):
    # this API is responsible for getting and calculating all the income coming in the operations account through transfers
    # return the income for the past seven months 
    pass



class CurrentMonthTransferBudgetSummary(APIView):
    # this API is responsible for getting and calculating all the transfer amount spent in the current month
    # this api is also responsible for getting the total amount available to transfer
    pass



class GetAllTransferTransaction (APIView):
    # this API is responsible for getting all the transfer transactions that has been made
    pass


class InititeTransferTransaction (APIView):
    '''
        This API is responsible for creating a transfer transaction and sending a notification
        to the directors
    '''
    permission_classes = [IsAuthenticated]

    def post (self, request, *args, **kwargs):
        try: 
            check_account_type(request.user, account_type)
            serializer = TransferTransactionWriteSerializer(data=request.data)

            if serializer.is_valid():
                # Modify the instance before saving
                transfer_instance = serializer.save(commit=False)

                # Modify the attributes of the instance
                transfer_instance.transaction_category = "DEBIT"
                transfer_instance.school = get_user_school(request.user).id
                transfer_instance.transaction_type = "TRANSFER"


                # Save the modified instance to the database
                transfer_instance.save()


        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)

        except APIException as e:
            return Response({"message": str(e.detail)}, status=e.status_code)

        except Exception as e:
            return Response({"message": "An error occurred"}, status=HTTP_500_INTERNAL_SERVER_ERROR)




class EditTransferTransaction(APIView):
    # this API is responsible for editing the transfer transaction
    pass


