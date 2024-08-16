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
account_type = "OPERATIONS"


# tested✅😊
# todo: later also pass expense data to
class GetMonthlyTransaction(APIView):
    '''
        Returns all the transactions that has happened for the last seven months. it sorts the transaction
        by month
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_school = get_user_school(request.user)
        unarranged_transaction_list = get_unarranged_transaction_six_months_ago(
            user_school)

        if unarranged_transaction_list is None:
            return Response(status=HTTP_404_NOT_FOUND, data={"message": "No transactions have been made for the past six months."})

        processed_data = process_and_sort_transactions_by_months(
            unarranged_transaction_list)

        transaction_serializer = MonthlyTransactionSerializer(
            processed_data, many=True)

        return Response(transaction_serializer.data, status=HTTP_200_OK)



class GetAmountAvailableOperationsAccount(APIView):
    '''Get all the amount available in the operations account'''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_school = get_user_school(request.user)
        operations_account = get_object_or_404(
            Operations_account, school=user_school)

        serializer = OperationsAccountSerializer(operations_account)

        return Response(serializer.data, status=HTTP_200_OK)



class GetOperationsAndCenteralAccountTotal(APIView):
    permission_classes = [IsAuthenticated]    

    def get(self, request):
        user_school = get_user_school(request.user)
        operations_account = get_object_or_404(Operations_account, school=user_school)
        central_account = get_object_or_404(Capital_Account, school=user_school)
        
        data = {
            'operations_account': operations_account,
            'central_account': central_account
        }
        
        serializer = OperationsAndCapitalAccountSerializer(data)
        
        return Response(serializer.data, status=HTTP_200_OK)



class GetTransactionSevenDaysAgo (APIView):
    '''
        Returns the total amount of money spent in the past 7 days and the sum of money spent in the past 7 days
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)
            unarranged_transaction_list = get_unarranged_transaction_seven_days_ago(
                user_school)

            if unarranged_transaction_list is None:
                return Response(status=HTTP_404_NOT_FOUND, data={"message": "No transactions have been made for the past seven days."})

            processed_data = process_and_sort_transactions_by_days(
                unarranged_transaction_list)
            cash_total, transfer_total = calculate_cash_and_transfer_transaction_total(
                unarranged_transaction_list)

            cash_and_transaction_data = {
                "cash_total": cash_total,
                "transfer_total": transfer_total
            }

            transaction_serializer = SummaryTransactionSerializer(
                processed_data, many=True)
            cash_and_transfer_total_serializer = CashandTransactionTotalSerializer(
                cash_and_transaction_data)

            data = {
                "summary": cash_and_transfer_total_serializer.data,
                "transfer_list": transaction_serializer.data
            }

            return Response(data, status=HTTP_200_OK)
        
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        



# tested✅😊
class GetAllCashTransactions(APIView):
    """
    API endpoint to get all approved cash transactions.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pending):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            # Check if the 'pending' argument is in the request's query parameters
            if pending == "pending":
                # Modify the query for pending transactions
                operations_account_cash_transaction = Operations_account_transaction_record.get_transaction(
                    school=user_school, transaction_type="CASH"
                ).order_by('-time').filter(status="PENDING")

            else:
                operations_account_cash_transaction = Operations_account_transaction_record.get_transaction(
                    school=user_school, transaction_type="CASH").order_by('-time').filter(status="SUCCESS")

            print(operations_account_cash_transaction)
            serializer = OperationsAccountCashTransactionRecordSerializer(
                operations_account_cash_transaction, many=True)

            return Response(serializer.data, status=HTTP_200_OK)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)



class ViewAndModifyCashTransaction(viewsets.ModelViewSet):
    """
    API endpoint to view and modify cash transactions.

    Requires authentication.

    Methods:
        - GET: Retrieves a list of all cash transactions (not supported).
        - POST: Creates a new cash transaction (not supported).
        - PUT: Updates a cash transaction (not supported).
        - PATCH: Partially updates a cash transaction. Supports modifying the status of the
                 transaction, and may initiate actions such as cancellation or pending approval.

    Permissions:
        - IsAuthenticated: Only authenticated users can access this endpoint.
    """
    queryset = Operations_account_transaction_record.objects.all()
    serializer_class = CashTransactionWriteSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return CashTransactionWriteSerializer
        return super().get_serializer_class()  # Default behavior

    def partial_update(self, request, *args, **kwargs):
        try:
            check_account_type(request.user, account_type)
            instance = self.get_object()
            user_school = get_user_school(request.user)


            # Merge current instance data with incoming data
            merged_data = {**self.get_serializer(instance).data, **request.data}

            # Now validate this merged data with your serializer
            serializer = self.get_serializer(instance, data=merged_data)

            #refactor this
            if serializer.is_valid():
                if serializer.validated_data == "CANCELLED":
                    serializer.save()
                else:
                    operation_type = "ADD"
                    instance = self.get_object()

                    update_operations_account(instance.amount, user_school.id, operation_type)
                    serializer.save(status="PENDING")
                # initiate a notification here later to head teacher
                #! reduce amount from operations account
                return Response({"message": "Successfully modified"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)



    def list(self, request, *args, **kwargs):
        return Response({"message": "This method is not supported"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def create(self, request, *args, **kwargs):
        return Response({"message": "This method is not supported"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response({"message": "This method is not supported"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response({"message": "This method is not supported"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    # tested✅😊


# APi to to add or creat cash transaction instance
class CreateCashTransaction (APIView):
    """
    API endpoint to create a cash transaction.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """
        Create a cash transaction.

        Parameters:
            request: The HTTP request object.
            format: The requested format for the response (default is None).

        Returns:
            Response: The HTTP response containing a success message if the transaction is created
                      successfully, or an error message if there are issues with the provided data
                      or user permissions.
        """
        try:
            check_account_type(request.user, account_type)
            serializer = CashTransactionWriteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(status="PENDING", school=get_user_school(
                    request.user), transaction_type="CASH", transaction_category="DEBIT")
                # initiate a notification here later to the head teacher
                return Response({"message": "Transaction created successfully"}, status=status.HTTP_201_CREATED)
            return Response({"message": "Your form information is in-correct"}, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)


class GetCashLeftInSafeAndCurrentMonthCashSummary (APIView):
    """
    API endpoint to retrieve the remaining cash in the safe and a summary of total amount of
    cash transactions spent for the current month.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_school = get_user_school(request.user)
        data = get_cash_left_and_month_summary(user_school, transaction_type="CASH")

        serializer = CashTransactionDetailsSerializer(data)
        return Response(serializer.data, status=HTTP_200_OK)




class GetIncomeGraph (APIView):
    permission_classes = [IsAuthenticated]

    def get (self, request):
        try:
            check_account_type(request.user, account_type)
            
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)





# API to get the summary of amount spent in the operatins account for a particular
class GetParticularsSummary(APIView):

    def get(self, request):
        user_school = get_user_school(request.user)
        operations_account_transaction_list = Operations_account_transaction_record.objects.filter(school=user_school)

        summary_dict = get_transaction_summary_by_header(operations_account_transaction_list)
        
        # Convert the summary dictionary to a list of dictionaries suitable for the serializer
        summary_list = [
            {'particulars_name': key, **value}
            for key, value in summary_dict.items()
        ]
        
        serializer = PercentageSummarySerializer(summary_list, many=True)
        return Response(serializer.data, status=HTTP_200_OK)
