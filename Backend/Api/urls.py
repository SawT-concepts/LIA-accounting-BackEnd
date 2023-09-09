from django.urls import path
from .views import LoginView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),  #? API responsible for the login functionality
    path('refresh_token', TokenRefreshView.as_view(), name='refresh'),  #? API responsible for the refresh functionality
]
