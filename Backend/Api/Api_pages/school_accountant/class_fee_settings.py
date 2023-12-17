from unicodedata import category
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

class GetFinancialInfoForAClass(APIView):
    '''This function returns information about the payment summary for the given class'''
    permission_classes = [IsAuthenticated]

    def get(self, request, grade_id, term):
        try:
            # Make sure to replace 'account_type' with the actual account type you are checking
            check_account_type(request.user, account_type)

            user_school = get_user_school(request.user)

            # Retrieve fees category for the given grade
            fees_category = FeesCategory.objects.get(school=user_school, grade=grade_id)

            # Retrieve financial information related to school fees
            school_fees_category = SchoolFeesCategory.objects.filter(term=term, category=fees_category)

            # Retrieve financial information related to bus fees
            bus_fee_category = BusFeeCategory.objects.filter(category=fees_category)

            # Retrieve financial information related to uniform and books fees
            uniform_and_books = UniformAndBooksFeeCategory.objects.filter(grades=grade_id, school=user_school)

            # Retrieve financial information related to other fees
            other_fees = OtherFeeCategory.objects.filter(grades=grade_id, school=user_school)

            # Serialize the data for the API response
            serialized_data = {
                "school_fees": SchoolFeesCategorySerializer(school_fees_category, many=True).data,
                "bus_fee": BusFeeCategorySerializer(bus_fee_category, many=True).data,
                "uniform_and_books": UniformAndBooksFeeCategorySerializer(uniform_and_books, many=True).data,
                "other_fees": OtherFeeCategorySerializer(other_fees, many=True).data,
            }

            return Response(serialized_data, status=HTTP_200_OK)

        except FeesCategory.DoesNotExist:
            return Response({"message": "Fees category not found for the given grade"}, status=HTTP_401_UNAUTHORIZED)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)


class CreateSchoolFeesCategory(APIView):
    '''Create a new school fees category'''
    permission_classes = [IsAuthenticated]
    def post(self, request, category):
        try:
            # Make sure to replace 'account_type' with the actual account type you are checking
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            # Deserialize the incoming data
            serializer = SchoolFeesCategorySerializer(data=request.data)

            if serializer.is_valid():
                serializer.validated_data['category'] = category
                serializer.save()

                return Response({"message": "School fees category created successfully"}, status=HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)
        
    def delete(self, request, category_id):
            try:
                school_fees_category = SchoolFeesCategory.objects.get(id=category_id)
                school_fees_category.delete()
                return Response({"message": "School fees category deleted successfully"}, status=HTTP_204_NO_CONTENT)

            except SchoolFeesCategory.DoesNotExist:
                return Response({"message": "School fees category not found"}, status=HTTP_400_BAD_REQUEST)
            except PermissionDenied:
                return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)


class EditSchoolFeesCategory(APIView):
    '''This section is used to edit school fees category. for example editing the tuiton fee for a grade in a particular term'''
    permission_classes = [IsAuthenticated]

    def patch(self, request, category_id):
        try:
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            # Retrieve the SchoolFeesCategory instance by category_id
            school_fees_category = SchoolFeesCategory.objects.get(id=category_id, category__school=user_school)

            # Deserialize the incoming data
            updated_data = request.data

            # Serialize the current instance data
            serializer = SchoolFeesCategorySerializer(instance=school_fees_category, data=updated_data, partial=True)

            if serializer.is_valid():
                # Update the SchoolFeesCategory instance with the new data
                serializer.save()
                return Response({"message": "School fees category updated successfully"}, status=HTTP_200_OK)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except SchoolFeesCategory.DoesNotExist:
            return Response({"message": "School fees category not found"}, status=HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)

class CreateBusFeeCategory(APIView):
    '''This is going to create bus fee category'''
    permission_classes = [IsAuthenticated]

    def post(self, request, category):
        try:
            # Make sure to replace 'account_type' with the actual account type you are checking
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            # Deserialize the incoming data
            serializer = BusFeeCategorySerializer(data=request.data)

            if serializer.is_valid():
                # Set the school and save the new BusFeeCategory instance
                serializer.validated_data['category'] = category
                serializer.save()

                return Response({"message": "Bus fee category created successfully"}, status=HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)


class EditBusFeeCategory(APIView):
    '''This api exist to edit a single instance of a bus fee. for example editing kuje moring bus fee'''
    permission_classes = [IsAuthenticated]

    def patch(self, request, category_id): 
        try:
            # Make sure to replace 'account_type' with the actual account type you are checking
            check_account_type(request.user, account_type)
            user_school = get_user_school(request.user)

            # Retrieve the BusFeeCategory instance by category_id
            bus_fee_category = BusFeeCategory.objects.get(id=category_id, category__school=user_school)

            # Deserialize the incoming data
            updated_data = request.data

            # Serialize the current instance data
            serializer = BusFeeCategorySerializer(instance=bus_fee_category, data=updated_data, partial=True)

            if serializer.is_valid():
                # Update the BusFeeCategory instance with the new data
                serializer.save()
                return Response({"message": "Bus fee category updated successfully"}, status=HTTP_200_OK)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except BusFeeCategory.DoesNotExist:
            return Response({"message": "Bus fee category not found"}, status=HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)
        
class CreateUniformAndBooksFeeCategory(APIView):
    '''This API is used to create a uniform and books fee category'''
    permission_classes = [IsAuthenticated]

    def post(self, request, category):
        try:
            # Make sure to replace 'account_type' with the actual account type you are checking
            check_account_type(request.user, 'account_type')
            user_school = get_user_school(request.user)

            # Deserialize the incoming data
            serializer = UniformAndBooksFeeCategorySerializer(data=request.data)

            if serializer.is_valid():
                # Set the school and save the new UniformAndBooksFeeCategory instance
                serializer.validated_data['category'] = category
                serializer.save()

                return Response({"message": "Uniform and books fee category created successfully"}, status=HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)
        


class EditUniformAndBooksFeeCategory(APIView):
    '''Edit the price of uniform and books fee category. for exmaple altering the price of labcoat'''
    permission_classes = [IsAuthenticated]

    def patch(self, request, category_id):
        try:
            # Make sure to replace 'account_type' with the actual account type you are checking
            check_account_type(request.user, 'account_type')
            user_school = get_user_school(request.user)

            # Retrieve the UniformAndBooksFeeCategory instance by category_id
            uniform_and_books_category = UniformAndBooksFeeCategory.objects.get(id=category_id, category__school=user_school)

            # Deserialize the incoming data
            updated_data = request.data

            # Serialize the current instance data
            serializer = UniformAndBooksFeeCategorySerializer(instance=uniform_and_books_category, data=updated_data, partial=True)

            if serializer.is_valid():
                # Update the UniformAndBooksFeeCategory instance with the new data
                serializer.save()
                return Response({"message": "Uniform and books fee category updated successfully"}, status=HTTP_200_OK)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except UniformAndBooksFeeCategory.DoesNotExist:
            return Response({"message": "Uniform and books fee category not found"}, status=HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)


class CreateOtherFeeCategory(APIView):
    '''Create a new other fee category'''
    permission_classes = [IsAuthenticated]

    def post(self, request, category):
        try:
            # Make sure to replace 'account_type' with the actual account type you are checking
            check_account_type(request.user, 'account_type')
            user_school = get_user_school(request.user)

            # Deserialize the incoming data
            serializer = OtherFeeCategorySerializer(data=request.data)

            if serializer.is_valid():
                # Set the school and save the new OtherFeeCategory instance
                serializer.validated_data['category'] = category
                serializer.save()

                return Response({"message": "Other fee category created successfully"}, status=HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)

class EditOtherFeeCategory(APIView):
    '''This makes editing other fee categories possible'''
    permission_classes = [IsAuthenticated]

    def patch(self, request, category_id):
        try:
            # Make sure to replace 'account_type' with the actual account type you are checking
            check_account_type(request.user, 'account_type')
            user_school = get_user_school(request.user)

            # Retrieve the OtherFeeCategory instance by category_id
            other_fee_category = OtherFeeCategory.objects.get(id=category_id, category__school=user_school)

            # Deserialize the incoming data
            updated_data = request.data

            # Serialize the current instance data
            serializer = OtherFeeCategorySerializer(instance=other_fee_category, data=updated_data, partial=True)

            if serializer.is_valid():
                # Update the OtherFeeCategory instance with the new data
                serializer.save()
                return Response({"message": "Other fee category updated successfully"}, status=HTTP_200_OK)
            else:
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        except OtherFeeCategory.DoesNotExist:
            return Response({"message": "Other fee category not found"}, status=HTTP_400_BAD_REQUEST)
        except PermissionDenied:
            return Response({"message": "Permission denied"}, status=HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"message": f"An error occurred: {str(e)}"}, status=HTTP_400_BAD_REQUEST)

