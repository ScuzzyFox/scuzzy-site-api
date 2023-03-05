from .views import Register, Login, ResetPassword, GetTest, DeleteUser, ListUsers
from django.urls import path

urlpatterns = [
    path("register/", Register.as_view(), name="register"),
    path("login/", Login.as_view(), name="register"),
    path("change-password/", ResetPassword.as_view(), name="reset"),
    path("get/", GetTest.as_view(), name="get"),
    path("delete-user/", DeleteUser.as_view(), name="delete-user"),
    path("users/", ListUsers.as_view(), name="list-users"),
]
