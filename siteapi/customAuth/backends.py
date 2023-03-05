from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from .models import CustomJWTToken
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from django.conf import settings
import jwt
import time


class UsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None


class JWTAuthentication(TokenAuthentication):
    model = CustomJWTToken
    keyword = 'Token'

    def authenticate_credentials(self, key):
        try:
            decoded_key = self.verify_jwt_token(key)
        except TypeError as e:
            print(f"TYPE ERROR {e}")
            print(f"key={key}")
            raise exceptions.AuthenticationFailed('Type error.')
        model = self.get_model()
        try:
            token = model.objects.select_related(
                'user').get(user_id=decoded_key['id'])
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')
        except TypeError:
            raise exceptions.AuthenticationFailed(
                'Invalid token OR user not found.')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        if not token.user.version == decoded_key["version"]:
            raise exceptions.AuthenticationFailed(
                'password was recently changed')

        if not token.user.username == decoded_key['username']:
            raise exceptions.AuthenticationFailed(
                'username does not match token')

        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword

    def verify_jwt_token(self, token):
        try:
            decoded_token = jwt.decode(
                token, settings.SECRET_KEY, algorithms=['HS256'])

            if 'exp' in decoded_token and decoded_token['exp'] < time.time():
                raise jwt.ExpiredSignatureError("Token has expired")

            return decoded_token

        except jwt.DecodeError as e:
            print(f"Invalid token: {e}")
            return None
        except jwt.ExpiredSignatureError as e:
            print(f"Token has expired: {e}")
            return None
