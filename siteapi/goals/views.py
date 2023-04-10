from rest_framework import generics, mixins, status
from .serializers import GoalSerializer
from .models import Goal
from rest_framework.views import APIView
from customAuth.backends import JWTAuthentication
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


class ListGoals(generics.ListAPIView):
    """
    A view that returns a list of goals.

    This view has no authentication or permission requirements.
    """
    permission_classes = ()
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()


class GoalDetail(generics.RetrieveAPIView):
    """
    A view that returns a single goal by ID.

    This view has no authentication or permission requirements.
    """
    permission_classes = ()
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()


class GoalDetailSlug(generics.RetrieveAPIView):
    """
    A view that returns a single goal by slug.

    This view has no authentication or permission requirements.
    """
    permission_classes = ()
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()
    lookup_field = "slug"


class UDGoals(generics.GenericAPIView, mixins.DestroyModelMixin, mixins.UpdateModelMixin):
    """
    A view that handles updating and deleting a specific goal by ID.

    This view requires JWT authentication.
    """
    authentication_classes = [JWTAuthentication]
    serializer_class = GoalSerializer
    queryset = Goal.objects.all()

    def put(self, request, *args, **kwargs):
        """
        Update a specific goal by ID.

        This endpoint requires a JWT token in the request header.

        :param request: The HTTP request object.
        :param args: Additional arguments passed to the view.
        :param kwargs: Additional keyword arguments passed to the view.
        :return: An HTTP response with the updated goal data.
        """
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Delete a specific goal by ID.

        This endpoint requires a JWT token in the request header.

        :param request: The HTTP request object.
        :param args: Additional arguments passed to the view.
        :param kwargs: Additional keyword arguments passed to the view.
        :return: An HTTP response indicating whether the goal was successfully deleted.
        """
        return self.destroy(request, *args, **kwargs)


class CreateGoal(generics.GenericAPIView, mixins.CreateModelMixin):
    """
    A view that handles creating a new goal.

    This view requires JWT authentication.
    """
    authentication_classes = [JWTAuthentication]
    serializer_class = GoalSerializer

    def post(self, request, *args, **kwargs):
        """
        Create a new goal.

        This endpoint requires a JWT token in the request header.

        :param request: The HTTP request object.
        :param args: Additional arguments passed to the view.
        :param kwargs: Additional keyword arguments passed to the view.
        :return: An HTTP response with the newly created goal data.
        """
        return self.create(request, *args, **kwargs)


class FulfillGoal(APIView):
    """
    A view that handles marking a goal as fulfilled.

    This view requires JWT authentication.
    """
    authentication_classes = [JWTAuthentication]

    def put(self, request, pk):
        """
        Mark a goal as fulfilled.

        This endpoint requires a JWT token in the request header.

        :param request: The HTTP request object.
        :param pk: The primary key of the goal to be fulfilled.
        :return: An HTTP response with the updated goal data.
        """
        goal = get_object_or_404(Goal, pk=pk)
        goal.make_fulfilled()
        serializer = GoalSerializer(goal, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
