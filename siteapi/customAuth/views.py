from django.shortcuts import render
from rest_framework import generics
from .serializers import UserSerializer, ChangePasswordSerializer, ListUserSerializer, RegistrationSerializer, LoginSerializer, TemporaryTokenSerializer, JWTTokenSerializer
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from .models import CustomJWTToken, ScuzzyFoxContentManagerUser, TemporaryToken
from .backends import TemporaryTokenAuthentication, JWTAuthentication

# Create your views here.


class ListTempTokens(generics.ListAPIView):
    permission_classes = ()
    serializer_class = TemporaryTokenSerializer
    queryset = TemporaryToken.objects.all()


class ListJWTTokens(generics.ListAPIView):
    permission_classes = ()
    serializer_class = JWTTokenSerializer
    queryset = CustomJWTToken.objects.all()


class Register(APIView):
    # someone needs to have been given a token for you to register
    authentication_classes = [TemporaryTokenAuthentication, JWTAuthentication]
    serializer_class = RegistrationSerializer

    def get(self, request):
        token = TemporaryToken.objects.create(user=request.user)
        return Response({"Token": token.key})

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = ScuzzyFoxContentManagerUser.objects.create_user(
                username=data["username"], email=data["email"], password=data["password"])
            CustomJWTToken.objects.create(user=user)
            return Response(UserSerializer(user).data)
        else:
            return Response({"error: invalid data"}, status=status.HTTP_400_BAD_REQUEST)


class Login(APIView):
    # anyone can access this view
    permission_classes = ()
    serializer_class = LoginSerializer

    def get(self, request):
        return Response("Please login using username/password")

    def post(self, request):
        username = request.data.get("username").lower()
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        if user:
            user_serializer = UserSerializer(user)
            returnData = dict(user_serializer.data)
            # refresh the jwt token (expiration and version number).
            CustomJWTToken.objects.get(user=user).save()
            return Response(returnData)
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)


class ResetPassword(APIView):
    authentication_classes = [JWTAuthentication]

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
            return Response(returnData)
        else:
            return Response({"error": "could not validate new passwords"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetTest(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response({"Authentication": "was successful!"})


class DeleteUser(APIView):
    authentication_classes = [JWTAuthentication]

    def delete(self, request):
        user = request.user
        user_serializer = UserSerializer(user)

        confirmedUser = authenticate(
            username=user.username, password=request.data["password"])

        if confirmedUser is not None:
            confirmedUser.delete()

        # ScuzzyFoxContentManagerUser.objects.get(id=user.id).delete()

        return Response(user_serializer.data, status=status.HTTP_200_OK)


class ListUsers(APIView):
    permission_classes = ()

    def get(self, request):
        users = ScuzzyFoxContentManagerUser.objects.all()
        serializer = ListUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


""" class GenerateTempToken(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        token = TemporaryToken.objects.create(user=user)
        return Response({"Token: ": token.key}, status=status.HTTP_200_OK) """
