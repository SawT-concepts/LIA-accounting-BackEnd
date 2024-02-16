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
from Api.helper_functions.payment_section.main import generate_grade_summary, get_payment_summary
from Main.models import Payroll, Operations_account_transaction_record
from Api.helper_functions.main import *
from Api.helper_functions.auth_methods import *
from Api.helper_functions.directors.main import *
from Api.Api_pages.operations.serializers import *
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
account_type = "ACCOUNTANT"


class CreateClass(APIView):
    '''This function creates a new class'''

    def post(self, request):
        try:
            # Check if the authenticated user has the required account type.
            check_account_type(request.user, account_type)
            # Assuming your serializer is named ClassSerializer, replace it with your actual serializer
            serializer = CreateClassSerializer(data=request.data)

            if serializer.is_valid():
                # Set the school based on the user making the request
                user_school = get_user_school(request.user)
                serializer.validated_data['school'] = user_school

                # Create the new class instance
                new_class = serializer.save()

                return Response({"message": "Class created successfully", "class_id": new_class.id}, status=HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except PermissionDenied:
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)


class EditClass(APIView):
    '''This function edits and/or deletes a class'''
    permission_classes = [IsAuthenticated]

    def patch(self, request, class_id):
        try:
            # Check if the authenticated user has the required account type.
            check_account_type(request.user, account_type)
            class_instance = Class.objects.get(id=class_id)
            serializer = CreateClassSerializer(
                instance=class_instance, data=request.data, partial=True)

            if serializer.is_valid():
                user_school = get_user_school(request.user)
                serializer.validated_data['school'] = user_school

                edited_class = serializer.save()

                return Response({"message": "Class edited successfully", "class_id": edited_class.id}, status=HTTP_200_OK)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except Class.DoesNotExist:
            return Response({"message": "Class not found"}, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)


class GetPercentageSummary (APIView):
    '''This api returns the percentage and the total number of students that have paid fees complete'''

    def get(self, request):
        try:
            # Check if the authenticated user has the required account type.
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            analytics = SchoolLevyAnalytics.objects.get(school=user_school.id)

            serializer = LevyAnalyticsSerializer(analytics)

            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)



class GetPaymentSmmaryByClass (APIView):
    '''This api returns the payment summary statistics of students in the specified class'''

    def get(self, request, class_id):
        try:
            # Check if the authenticated user has the required account type.
            check_account_type(request.user, account_type)

            grade = Class.objects.get(id=class_id)

            students = Student.objects.filter(grade=grade)

            summary = get_payment_summary(students)

            return Response({"data": summary}, status=HTTP_200_OK)

        except PermissionDenied:
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)


class GetGraphOfClassPayment (APIView):
    '''This api returns the payment graph of all the graph and how much is being paid'''

    def get(self, request):
        try:
            # Check if the authenticated user has the required account type.
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            grades = Class.objects.filter(user_school=user_school)
            result = generate_grade_summary(grades)

            return Response({"data": result}, status=HTTP_200_OK)
         
        except PermissionDenied:
            # If the user doesn't have the required permissions, return an HTTP 403 Forbidden response.
            return Response({"message": "Permission denied"}, status=HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)
