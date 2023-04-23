from django.db import models

# Create your models here.


class TelegramChatId(models.Model):
    chat_id = models.BigIntegerField(unique=True, primary_key=True)

    def __str__(self):
        return self.chat_id

    class Meta:
        ordering = ['chat_id']
