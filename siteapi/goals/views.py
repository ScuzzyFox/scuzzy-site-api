from rest_framework import generics, mixins, status
from .serializers import GoalSerializer
from .models import Goal
from rest_framework.views import APIView
from customAuth.backends import JWTAuthentication
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


# Create your views here.


class ListGoals(generics.ListAPIView):
    permission_classes = ()
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()


class GoalDetail(generics.RetrieveAPIView):
    permission_classes = ()
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()


class GoalDetailSlug(generics.RetrieveAPIView):
    permission_classes = ()
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()
    lookup_field = "slug"


# update/delete a specific goal
class UDGoals(generics.GenericAPIView, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    authentication_classes = [JWTAuthentication]
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CreateGoal(generics.GenericAPIView, mixins.CreateModelMixin):

    authentication_classes = [JWTAuthentication]
    serializer_class = GoalSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class FulfillGoal(APIView):
    authentication_classes = [JWTAuthentication]

    def put(self, request, pk):
        goal = get_object_or_404(Goal, pk=pk)
        goal.make_fulfilled()
        serializer = GoalSerializer(goal, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
