from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import *
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
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
from Paystack.transfers import *


class LoginPaymentPortal (APIView):
    '''This api is responsible for collecting the user information and log them in if their credentials are correct.'''
    def post (self, request):
        registration_number = request.GET.get('registration_number')
        email_address = request.GET.get('email_address')

        student_instance = Student.objects.get(registration_number=registration_number)
        if student_instance is None:
            return Response( {"message": "A student with that registration number does not exist!"}, status=HTTP_404_NOT_FOUND)    
        return Response ({"token": student_instance.id}, status=HTTP_200_OK)


class GetUserPaymentStatus (APIView):
    '''This api is responsible for getting the student's payment status'''


class GetSchoolFeesBreakDownCharges (APIView):
    '''This api is responsible for getting the student's school fees break down and levy'''


class GetUniformFeeBreakDownCharges (APIView):
    '''This api is responsible for getting the student's uniform fees break down'''


class GetBusFeeBreakDownCharges (APIView):
    '''This api is responsible for getting the student's bus fees break down'''


class GetOtherPaymentBreakDownCharges (APIView):
    '''This api is responsible for getting the student's  other payment break down'''


class ProcessFeePayment (APIView):
    '''This api is responsible for handling a compilation of all the fees for the student and processing the studen's payment status'''
