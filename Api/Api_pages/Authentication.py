from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK
from Api.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.views import APIView
#from Background_Tasks.tasks import 
from django.core.cache import cache
from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404


#? This api is responsible for Login in an returning a token when the user credentials are valid
class LoginView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer


class GetUserType(APIView):
    def get (self, request):
        user = request.user
        user_model = get_user_model()
        user = user_model.objects.get(id=user.id)

        return Response ({ "account_type": user.account_type})


class GetUserDetails (APIView):
    def get (self, request):
        user = request.user
        user_model = get_user_model()
        user = user_model.objects.get(id=user.id)

        first_name = user.first_name
        last_name = user.last_name

        data = {
            "name" : first_name + " " + last_name
        }

        return Response(data, status=HTTP_200_OK)