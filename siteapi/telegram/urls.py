from django.urls import path
from .views import TelegramChatIdView

urlpatterns = [
    path('telegram/', TelegramChatIdView.as_view(), name='telegram'),
]
