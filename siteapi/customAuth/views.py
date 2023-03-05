from django.shortcuts import render
from rest_framework import generics
from .serializers import UserSerializer, ChangePasswordSerializer, ListUserSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from .models import CustomJWTToken, ScuzzyFoxContentManagerUser

# Create your views here.


# this view needs to return a token too, but currently doesn't
class Register(generics.CreateAPIView):
    # anyone can access this view
    permission_classes = ()
    serializer_class = UserSerializer


class Login(APIView):
    # anyone can access this view
    permission_classes = ()

    def get(self, request):
        return Response("Please login using username/password")

    def post(self, request):
        username = request.data.get("username").lower()
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            user_serializer = UserSerializer(user)
            returnData = dict(user_serializer.data)
            return Response(returnData)
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):

    def post(self, request):
        user = request.user
        content = dict(request.data)
        content["username"] = user.username
        serializer = ChangePasswordSerializer(data=content)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            CustomJWTToken.objects.get(user=user).save()

            user_serializer = UserSerializer(user)
            returnData = dict(user_serializer.data)
            returnData["Token"] = user.jwt_auth_token.key
            return Response(returnData)
        else:
            return Response({"error": "could not validate new passwords"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetTest(APIView):

    def get(self, request):
        return Response({"Authentication": "was successful!!"})


class DeleteUser(APIView):

    def delete(self, request):
        user = request.user
        user_serializer = UserSerializer(user)
        ScuzzyFoxContentManagerUser.objects.get(id=user.id).delete()

        return Response(user_serializer.data, status=status.HTTP_200_OK)


class ListUsers(APIView):
    permission_classes = ()

    def get(self, request):
        users = ScuzzyFoxContentManagerUser.objects.all()
        serializer = ListUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
