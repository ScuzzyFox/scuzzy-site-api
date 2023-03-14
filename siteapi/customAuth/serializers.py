from .models import ScuzzyFoxContentManagerUser, CustomJWTToken, TemporaryToken
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate


class TemporaryTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = TemporaryToken
        fields = ('user_id', 'username', 'created')


class JWTTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = CustomJWTToken
        fields = ('user_id', 'username')


class UserSerializer(serializers.ModelSerializer):
    jwt_auth_token = serializers.StringRelatedField()

    class Meta:
        model = ScuzzyFoxContentManagerUser
        fields = ('username', 'email', 'password', 'jwt_auth_token')
        extra_kwargs = {'password': {'write_only': True},
                        'jwt_auth_token': {'required': False}}

    def create(self, validated_data):

        user = ScuzzyFoxContentManagerUser(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        CustomJWTToken.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        user = ScuzzyFoxContentManagerUser(
            username=validated_data['username']
        )
        instance.password = make_password(validated_data['password'])

        del validated_data['password']
        return super().update(instance, validated_data)


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScuzzyFoxContentManagerUser
        fields = ['username']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)
    username = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("New passwords do not match")
        if data['new_password'] == data['old_password']:
            raise serializers.ValidationError(
                "New password cannot be the same as new password")
        user = authenticate(
            username=data['username'], password=data['old_password'])
        if user is None:
            raise serializers.ValidationError("Current password is incorrect.")

        return data


class RegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

    def validate(self, data):

        if int(len(data["username"])) > 15:
            raise serializers.ValidationError("username is too long")
        if int(len(data["password"]) < 8):
            raise serializers.ValidationError("password is too short")
        data["username"] = str(data["username"]).lower()

        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=15, required=True)
    password = serializers.CharField(required=True)
