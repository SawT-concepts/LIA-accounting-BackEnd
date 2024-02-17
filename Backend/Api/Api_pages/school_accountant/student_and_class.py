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
account_type = "ACCOUNTANT"

#! THIS API HAS NO ROUTING!
class GetListOfClass (APIView):
    '''This API returns the list of all the classes available in the school'''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)
            grade = Class.objects.filter(school=user_school)
            serializer = GradeSerializer(grade, many=True)

            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)


class GetAllStudentsByClass (APIView):
    '''This API returns all the students depending on the class arguments passed'''
    permission_classes = [IsAuthenticated]

    def get(self, request, grade_id):

        try:
            check_account_type(request.user, account_type)
            grade = get_object_or_404(Class, id=grade_id)

            students = Student.objects.filter(grade=grade.id, is_active=True)
            serializer = StudentSerializer(students, many=True)

            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)


class GetStudentDetails (APIView):
    '''This API returns the details of a student based on the ID passed as a parameter... also return the student financial details'''

    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        try:
            check_account_type(request.user, account_type)

            student_details = get_object_or_404(PaymentStatus, student=student_id)
            serializer = StudentPaymentStatusDetailSerializer(student_details)

            return Response(serializer.data, status=HTTP_200_OK)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)


class GetStudentReciepts (APIView):
    '''This API returns the list of all the student's reciepts'''

    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        try:
            check_account_type(request.user, account_type)
            
            reciepts = PaymentHistory.objects.filter(student=student_id, payment_status="SUCCESS").order_by('-date_time_initiated')
            serializer = PaymentHistorySerializer(reciepts, many=True)

            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)



class GetFullRecieptInfo (APIView):
    '''This API retrieves the full student information'''
    permission_classes = [IsAuthenticated]

    def get(self, request, reciept_id):
        try:
            check_account_type(request.user, account_type)

            reciept = PaymentHistory.objects.get(id=reciept_id)
            serializer = PaymentHistoryDetailSerializer(reciept)

            return Response(serializer.data, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)




class CreateStudent(APIView):
    '''This API creates a new student'''

    def post(self, request):
        try:
            check_account_type(request.user, account_type)

            data = request.data
            user_school = get_user_school(request.user)

            # Initialize the serializer with both the data and the user school
            serializer = CreateStudentSerializer(data=data, context={'school': user_school})

            if serializer.is_valid():
                # Save the serializer and return the data
                serializer.save()
                return Response(serializer.data, status=HTTP_200_OK)
            
            else:
                # Raise a serializer error with the validation errors
                raise ValueError(serializer.errors)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)



class EditAndDeleteStudent (APIView):
    '''This API updates a student's information.... it also deletes'''
    def patch (self, request, student_id):
        try:
            check_account_type(request.user, account_type)
            data = request.data
            
            serializer = CreateStudentSerializer(data=data)

            if serializer.is_valid():
                # Save the serializer and return the data
                serializer.save()
                return Response(serializer.data, status=HTTP_200_OK)       
            else:
                # Raise a serializer error with the validation errors
                raise ValueError(serializer.errors)
            

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

