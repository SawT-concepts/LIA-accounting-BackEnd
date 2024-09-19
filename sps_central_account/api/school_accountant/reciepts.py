from django.utils import timezone
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
# from Background_Tasks.tasks import
from sps_authentication.utils.main import check_account_type
from sps_operations_account.api.serializers import *
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import PermissionDenied

from sps_operations_account.utils.main import get_user_school
account_type = "ACCOUNTANT"


from rest_framework.pagination import PageNumberPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class GetAllReceipts(APIView):
    '''
    Returns the list of the receipts for the school. Also make it searchable by receipt ID.
    '''
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search by receipt ID", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of results per page", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response('Successful response', PaymentHistorySerializer(many=True)),
            401: 'Unauthorized'
        }
    )
    def get(self, request):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            receipts = PaymentHistory.objects.filter(school=user_school)

            search = request.query_params.get('search', None)
            if search:
                receipts = receipts.filter(receipt_id__icontains=search)

            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(receipts, request)
            serializer = PaymentHistorySerializer(result_page, many=True)

            return paginator.get_paginated_response(serializer.data)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)


class GetLatestReceipts (APIView):
    '''This api returns the latest receipt processed the latest 50'''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the latest 50 successful receipts for the school",
        responses={
            200: openapi.Response('Successful response', PaymentHistorySerializer(many=True)),
            401: 'Unauthorized'
        }
    )
    def get(self, request):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)
            receipts = PaymentHistory.objects.filter(school=user_school, payment_status="SUCCESS").order_by('-date_time_initiated')[:50]
            serializer = PaymentHistorySerializer(receipts, many=True)
            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

class GetReceiptByID(APIView):
    '''This api returns the receipt with the given receipt ID'''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get the receipt with the given receipt ID",
        manual_parameters=[
            openapi.Parameter(
                'receipt_id',
                openapi.IN_PATH,
                description="ID of the receipt to retrieve",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response('Successful response', PaymentHistoryDetailSerializer),
            401: 'Unauthorized',
            404: 'Receipt not found'
        }
    )
    def get(self, request, receipt_id):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)
            receipt = PaymentHistory.objects.filter(school=user_school, receipt_id=receipt_id).first()

            if not receipt:
                return Response({"message": "Receipt not found"}, status=HTTP_404_NOT_FOUND)

            serializer = PaymentHistoryDetailSerializer(receipt)

            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
