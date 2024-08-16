from rest_framework.permissions import BasePermission
from rest_framework.pagination import PageNumberPagination
from Api.helper_functions.main import *



class HasRequiredAccountType(BasePermission):
    """
    Ensure user has the required account type.
    """

    def has_permission(self, request, view, account_type):
        # Replace this line with your actual check for account type logic.
        return check_account_type(request.user, account_type)
    
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


