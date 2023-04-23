from rest_framework import serializers
from .models import TelegramChatId


class TelegramChatIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramChatId
        fields = ['chat_id']
