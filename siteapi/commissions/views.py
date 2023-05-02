from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CommissionSerializer, CommissionCategorySerializer, CommissionVisualSerializer, CommissionOptionSerializer, CommissionOrderSerializer, CommissionStatusSerializer, CharacterReferenceSerializer
from rest_framework import generics, mixins, status, permissions, request
from customAuth.backends import JWTAuthentication
from .models import Commission, CommissionCategory, CommissionVisual, CommissionOption, CommissionOrder, CommissionStatus, CharacterReference


# get all commissions or create a new one
class CommissionView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CommissionSerializer

    def get_queryset(self):
        # fileter by category
        queryset = Commission.objects.all()
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(cagtegories=category)

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
    lookup_field = "slug"

    # updates can be partial
    def put(self, request, *args, **kwargs):
        return self.partial_update(request=request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request=request, *args, **kwargs)

    def get(self, request, slug):
        return self.retrieve(request=request, slug=slug)


class CommissionAddRemoveOption(APIView):
    # add or remove an option from a commission
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, commission_id, option_id, *args, **kwargs):
        commission = get_object_or_404(Commission, id=commission_id)
        option = get_object_or_404(CommissionOption, id=option_id)
        commission.options.add(option)
        return Response(CommissionSerializer(commission).data)

    def delete(self, request, commission_id, option_id, *args, **kwargs):
        commission = get_object_or_404(Commission, id=commission_id)
        option = get_object_or_404(CommissionOption, id=option_id)
        commission.options.remove(option)
        return Response(CommissionSerializer(commission).data)


# get all commission options or make a new one
class CommissionOptionView(generics.GenericAPIView, mixins.ListModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CommissionOptionSerializer

    # filter by commission or by order, otherwise return all options
    def get_queryset(self):
        queryset = CommissionOption.objects.all()
        commission_id = self.request.query_params.get("commission_id", None)
        order_id = self.request.query_params.get("order_id", None)
        if commission_id is not None:
            queryset = queryset.filter(commission=commission_id)
        if order_id is not None:
            queryset = queryset.filter(order_id=order_id)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request=request, *args, **kwargs)

    def post(self, request):
        data = request.data
        serializer = CommissionOptionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommissionOptionDetailView(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CommissionOptionSerializer
    queryset = CommissionOption.objects.all()
    lookup_field = "pk"

    # updates can be partial
    def put(self, request, *args, **kwargs):
        return self.partial_update(request=request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request=request, *args, **kwargs)

    def get(self, request, pk):
        return self.retrieve(request=request, pk=pk)


class CommissionVisualView(generics.GenericAPIView, mixins.ListModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CommissionVisualSerializer

    def get_queryset(self):
        queryset = CommissionVisual.objects.all()
        commission_id = self.request.query_params.get("commission_id", None)
        group_id = self.request.query_params.get("group_id", None)
        if commission_id is not None:
            queryset = queryset.filter(commission=commission_id)
        if group_id is not None:
            queryset = queryset.filter(group_identifier=group_id)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request=request, *args, **kwargs)

    def post(self, request):
        data = request.data
        serializer = CommissionVisualSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommissionVisualDetailView(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CommissionVisualSerializer
    queryset = CommissionVisual.objects.all()
    lookup_field = "pk"

    def perform_destroy(self, instance):
        del_group = self.request.query_params.get("group", None)
        if del_group is not None:
            instance.delete_group()
        return super().perform_destroy(instance)

    # updates can be partial
    def put(self, request, *args, **kwargs):
        return self.partial_update(request=request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request=request, *args, **kwargs)

    def get(self, request, pk):
        return self.retrieve(request=request, pk=pk)


class CommissionCategoryView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CommissionCategorySerializer

    def get_queryset(self):
        queryset = CommissionCategory.objects.all()
        commission_id = self.request.query_params.get("commission_id", None)
        if commission_id is not None:
            queryset = queryset.filter(commission=commission_id)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request=request, *args, **kwargs)

    def post(self, request,  *args, **kwargs):
        return self.create(request=request, *args, **kwargs)


class CommissionCategoryDetailView(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CommissionCategorySerializer
    lookup_field = "pk"
    queryset = CommissionCategory.objects.all()

    def put(self, request, *args, **kwargs):
        return self.partial_update(request=request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request=request, *args, **kwargs)

    def get(self, request, pk):
        return self.retrieve(request=request, pk=pk)


class CommissionAddRemoveCategory(APIView):
    # add or remove a category from a commission
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, commission_id, category_id, *args, **kwargs):
        commission = get_object_or_404(Commission, id=commission_id)
        category = get_object_or_404(CommissionCategory, id=category_id)
        commission.categories.add(category)
        return Response(CommissionSerializer(commission).data)

    def delete(self, request, commission_id, category_id, *args, **kwargs):
        commission = get_object_or_404(Commission, id=commission_id)
        category = get_object_or_404(CommissionCategory, id=category_id)
        commission.categories.remove(category)
        return Response(CommissionSerializer(commission).data)


class CommissionOrderView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommissionOrderSerializer

    def get_queryset(self):
        # filter by commission
        queryset = CommissionOrder.objects.all()
        commission_id = self.request.query_params.get("commission_id", None)
        status = self.request.query_params.get("status", None)
        customer_name = self.request.query_params.get("customer_name", None)
        email = self.request.query_params.get("email", None)
        completed = self.request.query_params.get("completed", None)

        if commission_id is not None:
            queryset = queryset.filter(commission=commission_id)
        if status is not None:
            queryset = queryset.filter(statuses=status)
        if customer_name is not None:
            queryset = queryset.filter(customer__name__icontains=customer_name)
        if email is not None:
            queryset = queryset.filter(email__icontains=email)
        if completed is not None:
            queryset = queryset.filter(completed=completed)
        return queryset

    def perform_create(self, serializer):
        model = serializer.save()
        model.calculate_subtotal()

    def get(self, request, *args, **kwargs):
        return self.list(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request=request, *args, **kwargs)


class CommissionOrderDetailView(generics.APIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommissionOrderSerializer
    queryset = CommissionOrder.objects.all()
    lookup_field = 'pk'

    def perform_update(self, serializer):
        model = serializer.save()
        model.calculate_subtotal()

    def put(self, request, *args, **kwargs):
        return self.partial_update(request=request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request=request, *args, **kwargs)

    def get(self, request, pk):
        return self.retrieve(request=request, pk=pk)


class CommissionStatusView(generics.APIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommissionStatusSerializer

    def get_queryset(self):
        # filter by commissionorder
        queryset = CommissionStatus.objects.all()
        order = self.request.query_params.get("order", None)
        if order is not None:
            queryset = queryset.filter(commission_order=order)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request=request, *args, **kwargs)


class CommissionStatusDetailView(generics.APIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommissionStatusSerializer
    lookup_field = 'pk'
    queryset = CommissionStatus.objects.all()

    def get(self, request, pk):
        return self.retrieve(request=request, pk=pk)

    def put(self, request, pk):
        return self.partial_update(request=request, pk=pk)

    def delete(self, request, pk):
        return self.destroy(request=request, pk=pk)


class OrderAddRemoveStatus(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id, status_id, *args, **kwargs):
        order = get_object_or_404(CommissionOrder, id=order_id)
        status = get_object_or_404(CommissionStatus, id=status_id)
        order.statuses.add(status)
        return Response(CommissionOrderSerializer(order).data)

    def delete(self, request, order_id, status_id, *args, **kwargs):
        order = get_object_or_404(CommissionOrder, id=order_id)
        status = get_object_or_404(CommissionStatus, id=status_id)
        order.statuses.remove(status)
        return Response(CommissionOrderSerializer(order).data)


class CharacterReferenceView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CharacterReferenceSerializer

    def get_queryset(self):
        queryset = CharacterReference.objects.all()
        order_id = self.request.query_params.get("order_id", None)
        character_name = self.request.query_params.get("character_name", None)
        if order_id is not None:
            queryset = queryset.filter(order=order_id)
        if character_name is not None:
            queryset = queryset.filter(
                character__name__icontains=character_name)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request=request, *args, **kwargs)


class CharacterReferenceDetailView(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CharacterReferenceSerializer
    queryset = CharacterReference.objects.all()
    lookup_field = 'pk'

    def get(self, request, pk):
        return self.retrieve(request=request, pk=pk)

    def put(self, request, pk):
        return self.partial_update(request=request, pk=pk)

    def delete(self, request, pk):
        return self.destroy(request=request, pk=pk)
