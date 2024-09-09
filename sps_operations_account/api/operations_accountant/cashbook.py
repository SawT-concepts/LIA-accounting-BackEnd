from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework import status, viewsets
from rest_framework.views import APIView
# from Background_Tasks.tasks import
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from sps_authentication.utils.main import check_account_type
from sps_central_account.models import CapitalAccount
from sps_core.models import School
from sps_operations_account.api.serializers import *
from rest_framework.permissions import IsAuthenticated
from typing import List, Dict, Any, Union
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import InvalidPage
from sps_operations_account.utils.main import calculate_cash_and_transfer_transaction_total, get_cash_left_and_month_summary, get_transaction_summary_by_header, get_unarranged_transaction_seven_days_ago, get_unarranged_transaction_six_months_ago, get_user_school, process_and_sort_transactions_by_days, process_and_sort_transactions_by_months

account_type: str = "OPERATIONS"



class GetMonthlyTransaction(APIView):
    '''
        Returns all the transactions that has happened for the last seven months. it sorts the transaction
        by month
    '''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get monthly transactions for the last seven months",
        responses={200: MonthlyTransactionSerializer(many=True),
                   404: "No transactions have been made for the past six months."}
    )
    def get(self, request) -> Response:
        user_school: Any = get_user_school(request.user)
        unarranged_transaction_list: Union[List[Any], None] = get_unarranged_transaction_six_months_ago(
            user_school)

        if unarranged_transaction_list is None:
            return Response(status=HTTP_404_NOT_FOUND, data={"message": "No transactions have been made for the past six months."})

        processed_data: List[Dict[str, Any]] = process_and_sort_transactions_by_months(
            unarranged_transaction_list)

        transaction_serializer: MonthlyTransactionSerializer = MonthlyTransactionSerializer(
            processed_data, many=True)

        return Response(transaction_serializer.data, status=HTTP_200_OK)



class GetAmountAvailableOperationsAccount(APIView):
    '''Get all the amount available in the operations account'''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the amount available in the operations account",
        responses={200: OperationsAccountSerializer()}
    )
    def get(self, request) -> Response:
        user_school: Any = get_user_school(request.user)
        operations_account:OperationsAccount = get_object_or_404(
           OperationsAccount, school=user_school)

        serializer: OperationsAccountSerializer = OperationsAccountSerializer(operations_account)

        return Response(serializer.data, status=HTTP_200_OK)



class GetOperationsAndCentralAccountTotal(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the total of operations and central accounts",
        responses={200: OperationsAndCapitalAccountSerializer()}
    )
    def get(self, request) -> Response:
        user_school: Any = get_user_school(request.user)
        operations_account:OperationsAccount = get_object_or_404(OperationsAccount, school=user_school)
        central_account: Any = get_object_or_404(CapitalAccount, school=user_school)

        data: Dict[str, Any] = {
            'operations_account':operations_account,
            'central_account': central_account
        }

        serializer: OperationsAndCapitalAccountSerializer = OperationsAndCapitalAccountSerializer(data)

        return Response(serializer.data, status=HTTP_200_OK)



class GetTransactionSevenDaysAgo (APIView):
    '''
        Returns the total amount of money spent in the past 7 days and the sum of money spent in the past 7 days
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        try:
            # check_account_type(request.user, account_type)
            user_school: Any = get_user_school(request.user)
            unarranged_transaction_list: Union[List[Any], None] = get_unarranged_transaction_seven_days_ago(
                user_school)

            if unarranged_transaction_list is None:
                return Response(status=HTTP_404_NOT_FOUND, data={"message": "No transactions have been made for the past seven days."})

            processed_data: List[Dict[str, Any]] = process_and_sort_transactions_by_days(
                unarranged_transaction_list)
            cash_total: float
            transfer_total: float
            cash_total, transfer_total = calculate_cash_and_transfer_transaction_total(
                unarranged_transaction_list)

            cash_and_transaction_data: Dict[str, float] = {
                "cash_total": cash_total,
                "transfer_total": transfer_total
            }

            transaction_serializer: SummaryTransactionSerializer = SummaryTransactionSerializer(
                processed_data, many=True)
            cash_and_transfer_total_serializer: CashandTransactionTotalSerializer = CashandTransactionTotalSerializer(
                cash_and_transaction_data)

            data: Dict[str, Any] = {
                "summary": cash_and_transfer_total_serializer.data,
                "transfer_list": transaction_serializer.data
            }

            return Response(data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)



class GetAllApprovedCashTransactions(APIView):
    """
    API endpoint to get all approved cash transactions.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        try:
            # check_account_type(request.user, account_type)
            user_school: Any = get_user_school(request.user)

            if user_school is None:
                return Response({"message": "User school not found"}, status=HTTP_404_NOT_FOUND)

            operations_account_cash_transaction: List[OperationsAccountTransactionRecord] = OperationsAccountTransactionRecord.get_transaction(
                school=user_school.id, transaction_type="CASH"
            ).order_by('-time').filter(status="SUCCESS")

            return self.paginate_and_serialize(request, operations_account_cash_transaction)

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


class GetAllPendingCashTransactions(APIView):
    """
    API endpoint to get all pending cash transactions.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        try:
            # check_account_type(request.user, account_type)
            user_school: Any = get_user_school(request.user)

            if user_school is None:
                return Response({"message": "User school not found"}, status=HTTP_404_NOT_FOUND)

            operations_account_cash_transaction: List[OperationsAccountTransactionRecord] = OperationsAccountTransactionRecord.objects.filter(
                school=user_school.id, transaction_type="CASH",
                status__in=["PENDING_APPROVAL", "PENDING_DELETE", "PENDING_EDIT"]
            ).order_by('-time')

            return self.paginate_and_serialize(request, operations_account_cash_transaction)

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
    """
    API endpoint to get all approved cash transactions.
    """
    permission_classes = [IsAuthenticated]



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
    queryset = OperationsAccountTransactionRecord.objects.all()
    serializer_class = CashTransactionWriteSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return CashTransactionWriteSerializer
        return super().get_serializer_class()  # Default behavior

    @swagger_auto_schema(
        operation_description="Partially update a cash transaction",
        request_body=CashTransactionWriteSerializer,
        responses={
            200: "Successfully modified",
            400: "Bad Request",
            401: "Permission denied"
        }
    )
    def partial_update(self, request, *args, **kwargs) -> Response:
        try:
            check_account_type(request.user, account_type)
            instance: OperationsAccountTransactionRecord = self.get_object()
            merged_data: Dict[str, Any] = {**self.get_serializer(instance).data, **request.data}
            serializer: CashTransactionWriteSerializer = self.get_serializer(instance, data=merged_data)
            if serializer.is_valid():
                if serializer.validated_data["status"] in ["CANCELLED", "PENDING_APPROVAL"]:
                    if instance.status == "SUCCESS":
                        return Response({"message": "Cannot edit a successful transaction."}, status=status.HTTP_400_BAD_REQUEST)
                    serializer.save()
                else:
                    serializer.save(status="PENDING_APPROVAL")
                return Response({"message": "Successfully modified"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=status.HTTP_401_UNAUTHORIZED)


    @swagger_auto_schema(auto_schema=None)
    def list(self, request, *args, **kwargs) -> Response:
        return Response({"message": "This method is not supported"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @swagger_auto_schema(auto_schema=None)
    def create(self, request, *args, **kwargs) -> Response:
        return Response({"message": "This method is not supported"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @swagger_auto_schema(auto_schema=None)
    def destroy(self, request, *args, **kwargs) -> Response:
        return Response({"message": "This method is not supported"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @swagger_auto_schema(auto_schema=None)
    def update(self, request, *args, **kwargs) -> Response:
        return Response({"message": "This method is not supported"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



# APi to to add or creat cash transaction instance
class CreateCashTransaction (APIView):
    """
    API endpoint to create a cash transaction.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a cash transaction",
        request_body=CashTransactionWriteSerializer,
        responses={
            201: "Transaction created successfully",
            400: "Your form information is in-correct",
            401: "Permission denied"
        }
    )
    def post(self, request, format=None) -> Response:
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
            serializer: CashTransactionWriteSerializer = CashTransactionWriteSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(status="PENDING_APPROVAL", school=get_user_school(
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

    @swagger_auto_schema(
        operation_description="Get cash left in safe and current month cash summary",
        responses={200: CashTransactionDetailsSerializer()}
    )
    def get(self, request) -> Response:
        user_school: School = get_user_school(request.user)
        data: Dict[str, Any] = get_cash_left_and_month_summary(user_school, transaction_type="CASH")

        serializer: CashTransactionDetailsSerializer = CashTransactionDetailsSerializer(data)
        return Response(serializer.data, status=HTTP_200_OK)




class GetIncomeGraph (APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get income graph data",
        responses={
            401: "Permission denied"
        }
    )
    def get (self, request) -> Response:
        try:
            check_account_type(request.user, account_type)
            # TODO: Implement the logic for getting income graph data
            return Response({"message": "Not implemented"}, status=HTTP_501_NOT_IMPLEMENTED)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)





# API to get the summary of amount spent in the operatins account for a particular
class GetParticularSummary(APIView):

    @swagger_auto_schema(
        operation_description="Get summary of amount spent in the operations account for particulars",
        responses={200: PercentageSummarySerializer(many=True)}
    )
    def get(self, request) -> Response:
        user_school: School = get_user_school(request.user)
        operations_account_transaction_list: Any = OperationsAccountTransactionRecord.objects.filter(school=user_school, status="SUCCESS")

        summary_dict: Dict[str, Any] = get_transaction_summary_by_header(operations_account_transaction_list)

        # Convert the summary dictionary to a list of dictionaries suitable for the serializer
        summary_list: List[Dict[str, Any]] = [
            {'particulars_name': key, **value}
            for key, value in summary_dict.items()
        ]

        serializer: PercentageSummarySerializer = PercentageSummarySerializer(summary_list, many=True)
        return Response(serializer.data, status=HTTP_200_OK)



class ViewAndAddParticulars(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get list of particulars for the user's school",
        responses={
            200: ParticularSerializer(many=True),
            401: "Permission denied"
        }
    )
    def get(self, request):
        try:
            user_school = get_user_school(request.user)
            particulars = Particular.objects.filter(school=user_school)
            serializer = ParticularSerializer(particulars, many=True)
            return Response(serializer.data, status=HTTP_200_OK)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        operation_description="Add a new particular for the user's school",
        request_body=ParticularSerializer,
        responses={
            201: ParticularSerializer,
            400: "Bad Request",
            401: "Permission denied"
        }
    )
    def post(self, request):
        try:
            user_school = get_user_school(request.user)
            serializer = ParticularSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(school=user_school)
                return Response(serializer.data, status=HTTP_201_CREATED)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
