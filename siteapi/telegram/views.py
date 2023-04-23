from customAuth.backends import PermanentTokenAuthentication, JWTAuthentication
from .serializers import TelegramChatIdSerializer
from rest_framework import views
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response
from .models import TelegramChatId


# view to create, delete, and list all chat id's. Uses a read only or is authenticated permission
class TelegramChatIdView(views.APIView):
    authentication_classes = [PermanentTokenAuthentication, JWTAuthentication]

    def get(self, request):
        chat_id = TelegramChatId.objects.all()
        serializer = TelegramChatIdSerializer(chat_id, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TelegramChatIdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        try:
            TelegramChatId.objects.get(
                chat_id=request.data['chat_id']).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TelegramChatId.DoesNotExist:
            return Response("This chat id does not exist", status=status.HTTP_404_NOT_FOUND)
