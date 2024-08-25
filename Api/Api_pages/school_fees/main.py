from django.utils import timezone
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework import status
from rest_framework.views import APIView
# from Background_Tasks.tasks import
from django.core.cache import cache
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from Api.helper_functions.payment_section.main import get_student_id_from_request
from Main.models import Student, SchoolConfig, PaymentStatus, FeesCategory, SchoolFeesCategory, UniformAndBooksFeeCategory, BusFeeCategory, OtherFeeCategory, PaymentHistory
from Api.helper_functions.main import *
from Api.helper_functions.auth_methods import *
from Api.helper_functions.directors.main import *
from Api.Api_pages.operations.serializers import *
from Paystack.transfers import *
from django.http import Http404
from typing import Dict, Any, Optional
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import QuerySet


class LoginPaymentPortal(APIView):
    """
    This API is responsible for collecting user information and logging them in if their credentials are correct.
    """

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'registration_number': openapi.Schema(type=openapi.TYPE_STRING, description='Student registration number'),
            },
            required=['registration_number']
        ),
        responses={
            200: openapi.Response('Successful login', openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description='Student ID token'),
                }
            )),
            404: 'Wrong Input',
            500: 'Internal Server Error',
        }
    )
    def post(self, request: Any) -> Response:
        """
        Handle POST request for login.

        Args:
            request (Any): The request object.

        Returns:
            Response: The response object containing the token or error message.
        """
        try:
            registration_number: str = request.data.get('registration_number')
            student_instance: Student = get_object_or_404(
                Student, registration_number=registration_number)
            return Response({"token": student_instance.student_id}, status=status.HTTP_200_OK)

        except Http404:
            return Response({"message": "Wrong Input"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetStudentInfo(APIView):
    """
    This API gets information about the student... first name, last name etc
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_PATH, description="Student ID", type=openapi.TYPE_STRING),
        ],
        responses={
            200: StudentSerializer,
            400: 'Bad Request',
            404: 'Student Not Found',
            500: 'Internal Server Error',
        }
    )
    def get(self, request: Any, student_id: str) -> Response:
        """
        Handle GET request for student information.

        Args:
            request (Any): The request object.
            student_id (str): The ID of the student.

        Returns:
            Response: The response object containing student information or error message.
        """
        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student: Student = get_student_id_from_request(student_id)
            serializer = StudentSerializer(student)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404:
            return Response({"message": "A student with that registration number does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSchoolStatus(APIView):
    """
    This is responsible for getting information about the school. stuffs like school current term and academic status
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_PATH, description="Student ID", type=openapi.TYPE_STRING),
        ],
        responses={
            200: SchoolConfigSerializer,
            400: 'Bad Request',
            404: 'Student Not Found',
            500: 'Internal Server Error',
        }
    )
    def get(self, request: Any, student_id: str) -> Response:
        """
        Handle GET request for school status.

        Args:
            request (Any): The request object.
            student_id (str): The ID of the student.

        Returns:
            Response: The response object containing school configuration or error message.
        """
        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student: Student = get_student_id_from_request(student_id)
            school_config: SchoolConfig = SchoolConfig.objects.get(school=student.school)

            serializer = SchoolConfigSerializer(school_config)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404:
            return Response({"message": "A student with that registration number does not exist!"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUserPaymentStatus(APIView):
    """
    This API is responsible for getting the student's payment status
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_PATH, description="Student ID", type=openapi.TYPE_STRING),
        ],
        responses={
            200: PaymentStatusSerializer,
            400: 'Bad Request',
            500: 'Internal Server Error',
        }
    )
    def get(self, request: Any, student_id: str) -> Response:
        """
        Handle GET request for user payment status.

        Args:
            request (Any): The request object.
            student_id (str): The ID of the student.

        Returns:
            Response: The response object containing payment status or error message.
        """
        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student: Student = get_student_id_from_request(student_id)
            payment_status: PaymentStatus = get_object_or_404(PaymentStatus, student=student)
            serializer = PaymentStatusSerializer(payment_status)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetSchoolFeesBreakDownCharges(APIView):
    """
    This api is responsible for getting the student's school fees break down and levy
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_PATH, description="Student ID", type=openapi.TYPE_STRING),
        ],
        responses={
            200: SchoolFeeCategorySerializer(many=True),
            400: 'Bad Request',
            500: 'Internal Server Error',
        }
    )
    def get(self, request: Any, student_id: str) -> Response:
        """
        Handle GET request for school fees breakdown charges.

        Args:
            request (Any): The request object.
            student_id (str): The ID of the student.

        Returns:
            Response: The response object containing school fees breakdown or error message.
        """
        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student: Student = get_student_id_from_request(student_id)
            school: int = student.school.id

            print(school)
            current_term: str = SchoolConfig.objects.get(school=school).term
            grade: str = student.grade

            fees_category: FeesCategory = FeesCategory.objects.get(
                school=school, category_type=category_types[0][0], grade=grade)

            school_fees_category: QuerySet[SchoolFeesCategory] = SchoolFeesCategory.objects.filter(
                term=current_term, category=fees_category)

            serializer = SchoolFeeCategorySerializer(
                school_fees_category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetUniformAndBookFeeBreakDownCharges(APIView):
    """
    This api is responsible for getting the student's uniform fees break down
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_PATH, description="Student ID", type=openapi.TYPE_STRING),
        ],
        responses={
            200: UniformAndBookFeeCategorySerializer(many=True),
            400: 'Bad Request',
            500: 'Internal Server Error',
        }
    )
    def get(self, request: Any, student_id: str) -> Response:
        """
        Handle GET request for uniform and book fee breakdown charges.

        Args:
            request (Any): The request object.
            student_id (str): The ID of the student.

        Returns:
            Response: The response object containing uniform and book fee breakdown or error message.
        """
        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student: Student = get_student_id_from_request(student_id)
            school: int = student.school.id
            grade: str = student.grade

            print(category_types[1][1])
            print(school)
            print(grade)

            fees_category: FeesCategory = FeesCategory.objects.get(
                school=school, category_type=category_types[1][1], grade=grade)

            uniform_fees_category: QuerySet[UniformAndBooksFeeCategory] = UniformAndBooksFeeCategory.objects.filter(
              category=fees_category)
            print("uniform part")
            print(uniform_fees_category)

            serializer = UniformAndBookFeeCategorySerializer(
                uniform_fees_category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetBusFeeBreakDownCharges(APIView):
    """
    This api is responsible for getting the student's bus fees break down
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_PATH, description="Student ID", type=openapi.TYPE_STRING),
        ],
        responses={
            200: BusFeeCategorySerializer(many=True),
            400: 'Bad Request',
            500: 'Internal Server Error',
        }
    )
    def get(self, request: Any, student_id: str) -> Response:
        """
        Handle GET request for bus fee breakdown charges.

        Args:
            request (Any): The request object.
            student_id (str): The ID of the student.

        Returns:
            Response: The response object containing bus fee breakdown or error message.
        """
        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student: Student = get_student_id_from_request(student_id)
            school: Any = student.school
            current_term: str = SchoolConfig.objects.get(school=school).term
            grade: str = student.grade

            fees_category: FeesCategory = FeesCategory.objects.get(
                school=school, category_type=category_types[2][1], grade=grade)

            bus_fee_category: QuerySet[BusFeeCategory] = BusFeeCategory.objects.filter(
                category=fees_category, term=current_term
            )

            serializer = BusFeeCategorySerializer(bus_fee_category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetOtherPaymentBreakDownCharges(APIView):
    """
    This api is responsible for getting the student's other payment break down
    """

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_PATH, description="Student ID", type=openapi.TYPE_STRING),
        ],
        responses={
            200: OtherFeeCategorySerializer(many=True),
            400: 'Bad Request',
            500: 'Internal Server Error',
        }
    )
    def get(self, request: Any, student_id: str) -> Response:
        """
        Handle GET request for other payment breakdown charges.

        Args:
            request (Any): The request object.
            student_id (str): The ID of the student.

        Returns:
            Response: The response object containing other payment breakdown or error message.
        """
        if not student_id:
            return Response({"message": "No student ID provided in headers"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student: Student = get_student_id_from_request(student_id)
            school: Any = student.school
            grade: str = student.grade

            fees_category: FeesCategory = FeesCategory.objects.get(
                school=school, category_type=category_types[3][1], grade=grade)

            other_fee_category: QuerySet[OtherFeeCategory] = OtherFeeCategory.objects.filter(
                category=fees_category
            )
            serializer = OtherFeeCategorySerializer(
                other_fee_category, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProcessFeePayment(APIView):
    """
    This API is responsible for handling a compilation of all the fees for the student and processing the student's payment status
    """

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'BREAKDOWN': openapi.Schema(type=openapi.TYPE_OBJECT, description='Payment breakdown'),
                'EMAIL': openapi.Schema(type=openapi.TYPE_STRING, description='User email'),
            },
            required=['BREAKDOWN', 'EMAIL']
        ),
        responses={
            200: 'Payment history created successfully',
            400: 'Bad Request',
            500: 'Internal Server Error',
        }
    )
    def post(self, request: Any) -> Response:
        """
        Handle POST request for processing fee payment.

        Args:
            request (Any): The request object.

        Returns:
            Response: The response object containing success message or error message.
        """
        student_id: Optional[str] = request.META.get('STUDENT_ID')

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
            payment_history.save()
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
