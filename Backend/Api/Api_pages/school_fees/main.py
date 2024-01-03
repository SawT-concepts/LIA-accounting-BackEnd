from turtle import st
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
from Paystack.transfers import *
from django.http import Http404
#! i haven't configured this file with the URL.py


class LoginPaymentPortal(APIView):
    '''
    This API is responsible for collecting user information and logging them in if their credentials are correct.
    '''

    def post(self, request):
        try:
            registration_number = request.data.get('registration_number')
            student_instance = get_object_or_404(
                Student, registration_number=registration_number)
            return Response({"token": student_instance.student_id}, status=status.HTTP_200_OK)

        except Http404:
            return Response({"message": "A student with that registration number does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetStudentInfo (APIView):
    '''This API gets information about the student... first name, last name etc'''

    def get(self, request, student_id):

        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Assuming you have a utility function to retrieve a student by ID
            student = get_student_id_from_request(student_id)
            serializer = StudentSerializer(student)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404:
            return Response({"message": "A student with that registration number does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSchoolStatus (APIView):
    '''This is responsible for getting information about the school. stuffs like school current term and academic status'''

    def get(self, request, student_id):

        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Assuming you have a utility function to retrieve a student by ID
            student = get_student_id_from_request(student_id)
            school_config = SchoolConfig.objects.get(school=student.school)

            serializer = SchoolConfigSerializer(school_config)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404:
            return Response({"message": "A student with that registration number does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUserPaymentStatus(APIView):
    '''This API is responsible for getting the student's payment status'''

    def get(self, request, student_id):
        # Extract student ID from request headers

        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Assuming you have a utility function to retrieve a student by ID
            student = get_student_id_from_request(student_id)

            # Assuming PaymentStatus is related to Student and has a foreign key to Student
            payment_status = get_object_or_404(PaymentStatus, student=student)
            serializer = PaymentStatusSerializer(payment_status)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSchoolFeesBreakDownCharges (APIView):
    '''This api is responsible for getting the student's school fees break down and levy'''

    def get(self, request, student_id):

        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)


        try:
            student = get_student_id_from_request(student_id)
            school = student.school.id

            print(school)
            current_term = SchoolConfig.objects.get(school=school).term
            grade = student.grade

            fees_category = FeesCategory.objects.get(
                school=school, category_type=category_types[0][0], grade=grade)

            school_fees_category = SchoolFeesCategory.objects.filter(
                term=current_term, category=fees_category)

            serializer = SchoolFeeCategorySerializer(
                school_fees_category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUniformAndBookFeeBreakDownCharges (APIView):
    '''This api is responsible for getting the student's uniform fees break down'''

    def get(self, request):
        student_id = request.META.get('STUDENT_ID')

        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = get_student_id_from_request(student_id)
            school = student.school
            grade = student.grade

            fees_category = FeesCategory.objects.get(
                school=school, category_type=category_types[1], grade=grade)

            uniform_fees_category = UniformAndBooksFeeCategory.objects.filter(
                grades=grade, category=fees_category)

            serializer = UniformAndBookFeeCategorySerializer(
                uniform_fees_category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetBusFeeBreakDownCharges (APIView):
    '''This api is responsible for getting the student's bus fees break down'''

    def get(self, request):
        student_id = request.META.get('STUDENT_ID')

        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = get_student_id_from_request(student_id)
            school = student.school
            grade = student.grade

            fees_category = FeesCategory.objects.get(
                school=school, category_type=category_types[2], grade=grade)

            bus_fee_category = BusFeeCategory.objects.filter(
                category=fees_category
            )

            serializer = BusFeeCategorySerializer(bus_fee_category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetOtherPaymentBreakDownCharges (APIView):
    '''This api is responsible for getting the student's  other payment break down'''

    def get(self, request):
        student_id = request.META.get('STUDENT_ID')

        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = get_student_id_from_request(student_id)
            school = student.school
            grade = student.grade

            fees_category = FeesCategory.objects.get(
                school=school, category_type=category_types[3], grade=grade)

            other_fee_category = OtherFeeCategory.objects.filter(
                category=fees_category, grades=grade
            )
            serializer = OtherFeeCategorySerializer(
                other_fee_category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProcessFeePayment(APIView):
    '''This API is responsible for handling a compilation of all the fees for the student and processing the student's payment status'''

    def post(self, request):
        student_id = request.META.get('STUDENT_ID')

        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = get_student_id_from_request(student_id)
            receipt_name = f'School fees for {student.first_name}'

            # Check for the existence of 'BREAKDOWN' in request data
            breakdown = request.data.get('BREAKDOWN')
            email = request.data.email('EMAIL')
            if breakdown is None:
                return Response({"message": "'BREAKDOWN' not provided in request data"}, status=status.HTTP_400_BAD_REQUEST)

            payment_history = PaymentHistory.objects.create(
                name=receipt_name,
                student=student,
                date_time_initiated=timezone.now(),
                is_active=True,
                merchant_email=email,
                payment_status="PENDING",
                breakdowns=breakdown
            )
            return Response({"message": "Payment history created successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MakePaymentFromHistory (APIView):
    '''This api is responsible for initiating a transaction to paystack'''

    def post(self, request):
        pass


class VerifyAndUpdatePayment(APIView):
    '''This api is responsible for verifying and updating the payment. It updates the student payment status too on the server'''

    def post(self, request):
        reference = request.data.get('REFRENCE')

        # payment_info = verify_payment(reference)

        # if payment_info.status is successful then update the student payment status
