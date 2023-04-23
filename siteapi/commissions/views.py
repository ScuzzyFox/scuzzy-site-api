from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CommissionSerializer, CommissionCategorySerializer, CommissionVisualSerializer, CommissionOptionSerializer, CommissionOrderSerializer, CommissionStatusSerializer, CharacterReferenceSerializer
from rest_framework import generics, mixins, status, permissions
from customAuth.backends import JWTAuthentication
from .models import Commission, CommissionCategory, CommissionVisual, CommissionOption, CommissionOrder, CommissionStatus, CharacterReference


# get all commissions or create a new one
class CommissionView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CommissionSerializer
    queryset = Commission.objects.all()

    def get(self, request):
        commissions = CommissionSerializer(
            Commission.objects.all(), many=True).data
        return Response(commissions)

    def post(self, request):
        data = request.data
        serializer = CommissionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# get, update, or delete a specific commission via its id


class CommissionDetailView(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CommissionSerializer
    queryset = Commission.objects.all()

    # updates can be partial
    def put(self, request, *args, **kwargs):
        return self.partial_update(request=request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request=request, *args, **kwargs)

    def get(self, request, pk):
        return self.retrieve(request=request, pk=pk)

# will be routed to a url that uses slugs instead. same as regular detail view.


class commissionDetailSlugView(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CommissionSerializer
    queryset = Commission.objects.all()
    lookup_field = ["slug"]

    # updates can be partial
    def put(self, request, *args, **kwargs):
        return self.partial_update(request=request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request=request, *args, **kwargs)

    def get(self, request, slug):
        return self.retrieve(request=request, slug=slug)
