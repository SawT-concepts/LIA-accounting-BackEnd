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
from Api.helper_functions.head_teacher.main import *
from Api.Api_pages.operations.serializers import *
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.exceptions import APIException
account_type = "HEAD_TEACHER"



#! The API is not routed 

class GetSchoolConfig (APIView):
    '''this api gets all theSchoolConfig'''
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            check_account_type(request.user, 'account_type')
            user_school = get_user_school(request.user)
            
            school_settings = SchoolConfig.objects.get(school=user_school)
            serializer = SchoolConfigSerializer(school_settings)

            return Response(serializer.data, status=HTTP_200_OK)
        

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)

class ChangeAcademicSession(APIView):
    '''This API changes and modifies the academic session of a school'''
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            # Make sure to replace 'account_type' with the actual account type you are checking
            check_account_type(request.user, 'account_type')

            user_school = get_user_school(request.user)
            data = request.data

            school_settings = SchoolConfig.objects.get(school=user_school)

            # Update the academic session and save the changes
            school_settings.academic_session = data.get("academic_session")
            school_settings.term = data.get("term")
            
            school_settings.save()

            return Response({"message": "Successful"}, status=HTTP_201_CREATED)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except SchoolConfig.DoesNotExist:
            return Response({"message": "School configuration not found"}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Handle other exceptions and provide details in the response
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)



class PromoteStudent (APIView):
    ''' this API automatically promotes all the students of a school'''

    def post (self, request):
        try:
            # Make sure to replace 'account_type' with the actual account type you are checking
            check_account_type(request.user, 'account_type')
            user_school = get_user_school(request.user)

            data = request.data 
            demoted_students = data['demoted_students']
            promote_students(user_school, demoted_students)

            return Response({"message": "Successful"}, status=HTTP_200_OK)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)