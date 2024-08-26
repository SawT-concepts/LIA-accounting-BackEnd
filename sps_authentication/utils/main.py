from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied





def check_account_type(user, account_type):
    '''
        This api is used to check if the correct user role is accessing the API. if its not the user
        then it should raise a PermissionDenied exception
    '''
    def get_user_type(user, account_type):
        user_model = get_user_model()
        user = user_model.objects.get(id=user.id)

        if user.account_type != account_type:
            raise PermissionDenied()  # Raise an exception if unauthorized

    get_user_type(user, account_type)  # Call the inner function




class HasRequiredAccountType(BasePermission):
    """
    Ensure user has the required account type.
    """

    def has_permission(self, request, view, account_type):
        return check_account_type(request.user, account_type)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000
