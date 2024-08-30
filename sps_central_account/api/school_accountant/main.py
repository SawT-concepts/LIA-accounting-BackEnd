from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
# from Background_Tasks.tasks import
from rest_framework.exceptions import  PermissionDenied
from django.shortcuts import get_object_or_404
from sps_authentication.utils.main import check_account_type
from sps_central_account.utils.main import generate_grade_summary, get_payment_summary
from sps_operations_account.api.serializers import *
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from typing import Any, Dict

from sps_operations_account.utils.main import get_user_school

account_type = "ACCOUNTANT"


class CreateGrade(APIView):
    '''This function creates a new class'''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new class",
        request_body=CreateGradeSerializer,
        responses={201: openapi.Response("Grade created successfully")}
    )
    def post(self, request: Any) -> Response:
        try:
            check_account_type(request.user, account_type)
            serializer = CreateGradeSerializer(data=request.data)

            if serializer.is_valid():
                user_school = get_user_school(request.user)
                serializer.validated_data['school'] = user_school

                new_class = serializer.save()

                return Response({"message": "Grade created successfully", "class_id": new_class.id}, status=HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)


class EditGrade(APIView):
    '''This function edits and/or deletes a class'''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Edit a class",
        request_body=CreateGradeSerializer,
        responses={200: openapi.Response("Grade edited successfully")}
    )
    def patch(self, request: Any, class_id: int) -> Response:
        try:
            check_account_type(request.user, account_type)
            class_instance = Grade.objects.get(id=class_id)
            serializer = CreateGradeSerializer(
                instance=class_instance, data=request.data, partial=True)

            if serializer.is_valid():
                user_school = get_user_school(request.user)
                serializer.validated_data['school'] = user_school

                edited_class = serializer.save()

                return Response({"message": "Grade edited successfully", "class_id": edited_class.id}, status=HTTP_200_OK)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except Grade.DoesNotExist:
            return Response({"message": "Grade not found"}, status=HTTP_404_NOT_FOUND)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)


class GetPercentageSummary(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get percentage summary",
        responses={200: LevyAnalyticsSerializer()}
    )
    def get(self, request: Any) -> Response:
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            analytics = get_object_or_404(SchoolLevyAnalytics.objects.select_related('school'), school=user_school.id)

            serializer = LevyAnalyticsSerializer(analytics)
            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)


class GetPaymentSummaryByGrade(APIView):
    '''This api returns the payment summary statistics of students in the specified class'''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get payment summary by class",
        responses={200: openapi.Response("Payment summary retrieved successfully")}
    )
    def get(self, request: Any, class_id: int) -> Response:
        try:
            check_account_type(request.user, account_type)

            grade = Grade.objects.get(id=class_id)
            students = Student.objects.filter(grade=grade)

            summary = get_payment_summary(students)

            return Response({"data": summary}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)


class GetGraphOfGradePayment(APIView):
    '''This api returns the payment graph of all the graph and how much is being paid'''
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get graph of class payment",
        responses={200: openapi.Response("Graph data retrieved successfully")}
    )
    def get(self, request: Any) -> Response:
        try:
            user_school = get_user_school(request.user)

            result = generate_grade_summary(user_school)

            return Response({"data": result}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)
