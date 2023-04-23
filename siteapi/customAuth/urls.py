from .views import Register, Login, ResetPassword, CheckJWTToken, DeleteUser, ListUsers, ListTempTokens, ListJWTTokens, GenerateDeleteOrListPermanentToken
from django.urls import path

urlpatterns = [
    path("register/", Register.as_view(), name="register"),
    path("login/", Login.as_view(), name="register"),
    path("change-password/", ResetPassword.as_view(), name="reset"),
    path("check-jwt-token/", CheckJWTToken.as_view(), name="check-jwt-token"),
    path("delete-user/", DeleteUser.as_view(), name="delete-user"),
    path("users/", ListUsers.as_view(), name="list-users"),
    path("temp-tokens/", ListTempTokens.as_view(), name="temp-tokens"),
    path("jwt-tokens/", ListJWTTokens.as_view(), name="jwt-tokens"),
    path("permanent-tokens/",  GenerateDeleteOrListPermanentToken.as_view(),
         name="permanent-tokens"),
]
