from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from django.core.exceptions import PermissionDenied
from sps_authentication.utils.main import check_account_type
from sps_core.utils.main import promote_students
from sps_operations_account.api.serializers import *
from rest_framework.permissions import IsAuthenticated

from sps_operations_account.utils.main import get_user_school
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
