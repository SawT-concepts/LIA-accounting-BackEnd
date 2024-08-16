from django.utils import timezone
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework import status, viewsets
from rest_framework.views import APIView
# from Background_Tasks.tasks import
from django.core.cache import cache
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from Api.helper_functions.payment_section.main import get_student_id_from_request
from Main.models import Payroll, Operations_account_transaction_record
from Api.helper_functions.main import *
from Api.helper_functions.auth_methods import *
from Api.helper_functions.directors.main import *
from Api.Api_pages.operations.serializers import *
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
account_type = "SCHOOL_ACCOUNTANT"


class Get_all_reciepts (APIView):
    '''Returns the list of the reciepts for the school. Also make it searchable by reciept ID
    - make the stuff searchable to
    '''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            reciepts = PaymentHistory.objects.filter(school=user_school)
            serializer = PaymentHistorySerializer(reciepts)

            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

class GetLatestReciepts (APIView):
    '''This api returns the latest reciept processed the latest 50'''

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)
            #?check from cache  

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
