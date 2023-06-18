from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CommissionSerializer, CommissionCategorySerializer, CommissionVisualSerializer, CommissionOptionSerializer, CommissionOrderSerializer, CommissionStatusSerializer, CharacterReferenceSerializer, AnonymousCharacterReferenceSerializer, AnonymousOrderSerializer
from rest_framework import generics, mixins, status, permissions, request
from customAuth.backends import JWTAuthentication, PermanentTokenAuthentication
from .models import Commission, CommissionCategory, CommissionVisual, CommissionOption, CommissionOrder, CommissionStatus, CharacterReference
import traceback

# TODO: ensure there are not multiple matching exlcusive_with options for a single commission?

# get all commissions or create a new one


class CommissionView(generics.GenericAPIView, mixins.ListModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CommissionSerializer

    def get_queryset(self):
        # fileter by category
        queryset = Commission.objects.all()
        category = self.request.query_params.get('category', None)
        abdl = self.request.query_params.get('abdl', None)
        adult = self.request.query_params.get('adult', None)
        available = self.request.query_params.get('available', None)
        visible = self.request.query_params.get('available', None)
        if category is not None:
            queryset = queryset.filter(cagtegories=category)
        if abdl is not None:
            queryset = queryset.filter(abdl=abdl)
        if adult is not None:
            queryset = queryset.filter(adult=adult)
        if available is not None:
            queryset = queryset.filter(available=available)
        if visible is not None:
            queryset = queryset.filter(visible=visible)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request=request, *args, **kwargs)

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

    def get(self, request, commission_id, option_id, *args, **kwargs):
        option = get_object_or_404(CommissionOption, id=option_id)
        return Response({"option": CommissionOptionSerializer(option, context={'request': request}).data, "commissions": CommissionSerializer(Commission.objects.filter(options=option), many=True, context={'request': request}).data})

    def post(self, request, commission_id, option_id, *args, **kwargs):
        commission = get_object_or_404(Commission, id=commission_id)
        initial_count_of_options = len(commission.options)
        option = get_object_or_404(CommissionOption, id=option_id)
        commission.options.add(option)
        if initial_count_of_options < len(commission.options):
            return Response(CommissionSerializer(commission, context={'request': request}).data)
        else:
            return Response({'error': "commission options did not increase. Failed to add option "+option_id+" to commission "+commission_id})

    def delete(self, request, commission_id, option_id, *args, **kwargs):
        commission = get_object_or_404(Commission, id=commission_id)
        initial_count_of_options = len(commission.options)

        option = get_object_or_404(CommissionOption, id=option_id)
        commission.options.remove(option)
        if initial_count_of_options < len(commission.options):

            return Response(CommissionSerializer(commission, context={'request': request}).data)
        else:
            return Response({'error': "commission options did not decrease. Failed to remove option "+option_id+" from commission "+commission_id})


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
        exclusive_with = self.request.query_params.get("exclusive_with", None)
        required = self.request.query_params.get("required", None)
        abdl = self.request.query_params.get('abdl', None)
        adult = self.request.query_params.get('adult', None)
        if commission_id is not None:
            queryset = queryset.filter(commission=commission_id)
        if order_id is not None:
            queryset = queryset.filter(order_id=order_id)
        if exclusive_with is not None:
            queryset = queryset.filter(exclusive_with=exclusive_with)
        if required is not None:
            queryset = queryset.filter(required=required)
        if abdl is not None:
            queryset = queryset.filter(abdl=abdl)
        if adult is not None:
            queryset = queryset.filter(adult=adult)
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
        abdl = self.request.query_params.get('abdl', None)
        adult = self.request.query_params.get('adult', None)
        size = self.request.query_params.get('size', None)
        is_video = self.request.query_params.get('is_video', None)
        if commission_id is not None:
            queryset = queryset.filter(commission=commission_id)
        if group_id is not None:
            queryset = queryset.filter(group_identifier=group_id)
        if abdl is not None:
            queryset = queryset.filter(abdl=abdl)
        if adult is not None:
            queryset = queryset.filter(adult=adult)
        if size is not None:
            # size is not part of the model, but instead appended as _256 or _512 to the file name
            # filtering the queryset by visual (which is a file name) ending with the size
            # note that the only available options will be 256, 512, 1024 etc. up to the original size of the image.
            queryset = queryset.filter(visual__icontains="_"+size)
        if is_video is not None:
            queryset = queryset.filter(is_video=is_video)
        return queryset

    def delete(self, request, *args, **kwargs):
        group_id = request.query_params.get("group_id", None)
        if group_id is not None:
            try:
                queryset = self.get_queryset()
                query = queryset.filter(group_identifier=group_id)
                for item in query:
                    item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                # print stacktrace to console
                print(traceback.format_exc())
                return Response("Could not delete group " + group_id, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response("No group id provided", status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        return self.list(request=request, *args, **kwargs)

    def post(self, request):
        data = request.data
        serializer = CommissionVisualSerializer(
            data=data,  context={"request": request})
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
        abdl = self.request.query_params.get('abdl', None)
        adult = self.request.query_params.get('adult', None)
        if commission_id is not None:
            queryset = queryset.filter(commission=commission_id)
        if abdl is not None:
            queryset = queryset.filter(abdl=abdl)
        if adult is not None:
            queryset = queryset.filter(adult=adult)
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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, commission_id, category_id, *args, **kwargs):
        category = get_object_or_404(CommissionCategory, id=category_id)
        return Response({"category": CommissionCategorySerializer(category, context={"request": request}).data, "commissions":  CommissionSerializer(Commission.objects.filter(categories=category), context={"request": request}, many=True).data})

    def post(self, request, commission_id, category_id, *args, **kwargs):
        commission = get_object_or_404(Commission, id=commission_id)
        category = get_object_or_404(CommissionCategory, id=category_id)
        commission.categories.add(category)
        return Response(CommissionSerializer(commission, context={"request": request}).data)

    def delete(self, request, commission_id, category_id, *args, **kwargs):
        commission = get_object_or_404(Commission, id=commission_id)
        category = get_object_or_404(CommissionCategory, id=category_id)
        commission.categories.remove(category)
        return Response(CommissionSerializer(commission, context={"request": request}).data)


# --------------------- ORDERS ----------------------------------------------------------------------


class CommissionOrderView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):

    authentication_classes = [JWTAuthentication, PermanentTokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommissionOrderSerializer

    def get_queryset(self):
        queryset = CommissionOrder.objects.all()
        commission_id = self.request.query_params.get("commission_id", None)
        status = self.request.query_params.get("status", None)
        customer_name = self.request.query_params.get("customer_name", None)
        email = self.request.query_params.get("email", None)
        completed = self.request.query_params.get("completed", None)
        abdl = self.request.query_params.get('abdl', None)
        adult = self.request.query_params.get('adult', None)

        if commission_id is not None:
            queryset = queryset.filter(commission=commission_id)
        if status is not None:
            queryset = queryset.filter(statuses=status)
        if customer_name is not None:
            queryset = queryset.filter(customer_name__icontains=customer_name)
        if email is not None:
            queryset = queryset.filter(email__icontains=email)
        if completed is not None:
            queryset = queryset.filter(completed=completed)
        if abdl is not None:
            queryset = queryset.filter(abdl=abdl)
        if adult is not None:
            queryset = queryset.filter(adult=adult)
        return queryset

    def perform_create(self, serializer):
        model = serializer.save()
        model.calculate_subtotal()

    def get(self, request, *args, **kwargs):

        if not request.user.is_anonymous:
            return self.list(request=request, *args, **kwargs)
        else:
            # return just basic info for anonymous users
            queryset = self.get_queryset()
            serializer = AnonymousOrderSerializer(
                queryset, many=True, context={'request': request})
            return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        return self.create(request=request, *args, **kwargs)


class CommissionOrderDetailView(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):

    authentication_classes = [JWTAuthentication, PermanentTokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommissionOrderSerializer
    queryset = CommissionOrder.objects.all()
    lookup_field = 'pk'

    def perform_update(self, serializer):
        serializer.save()
        instance = self.get_object()
        instance.calculate_subtotal()

    def put(self, request, *args, **kwargs):
        return self.partial_update(request=request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request=request, *args, **kwargs)

    def get(self, request, pk):
        if not request.user.is_anonymous:
            return self.retrieve(request=request, pk=pk)
        else:
            # return just basic info for anonymous users
            ord = get_object_or_404(CommissionOrder, id=pk)
            serializer = AnonymousOrderSerializer(
                ord, context={'request': request})
            return Response(serializer.data)


class CommissionStatusView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = CommissionStatusSerializer

    def get_queryset(self):
        # filter by commissionorder
        queryset = CommissionStatus.objects.all()
        order = self.request.query_params.get("order", None)
        status = self.request.query_params.get("status", None)
        if order is not None:
            queryset = queryset.filter(commission_order=order)
        if order is not None:
            queryset = queryset.filter(status__icontains=status)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request=request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request=request, *args, **kwargs)


class CommissionStatusDetailView(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
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
    authentication_classes = [JWTAuthentication, PermanentTokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, order_id, status_id, *args, **kwargs):
        order = get_object_or_404(CommissionOrder, id=order_id)
        status = get_object_or_404(CommissionStatus, id=status_id)
        order.statuses.add(status)
        return Response(CommissionOrderSerializer(order, context={'request': request}).data)

    def delete(self, request, order_id, status_id, *args, **kwargs):
        order = get_object_or_404(CommissionOrder, id=order_id)
        status = get_object_or_404(CommissionStatus, id=status_id)
        order.statuses.remove(status)
        return Response(CommissionOrderSerializer(order, context={'request': request}).data)


class CharacterReferenceView(generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin):
    authentication_classes = [JWTAuthentication, PermanentTokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CharacterReferenceSerializer

    def get_queryset(self):
        queryset = CharacterReference.objects.all()
        order_id = self.request.query_params.get("order_id", None)
        character_name = self.request.query_params.get("character_name", None)
        abdl = self.request.query_params.get('abdl', None)
        adult = self.request.query_params.get('adult', None)
        if order_id is not None:
            queryset = queryset.filter(order=order_id)
        if character_name is not None:
            queryset = queryset.filter(
                character_name__icontains=character_name)
        if abdl is not None:
            queryset = queryset.filter(abdl=abdl)
        if adult is not None:
            queryset = queryset.filter(adult=adult)
        return queryset

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous:
            return self.list(request=request, *args, **kwargs)
        else:
            # return just basic info for anonymous users
            queryset = self.get_queryset()
            return Response(AnonymousCharacterReferenceSerializer(queryset, many=True, context={'request': request}).data)

    def post(self, request, *args, **kwargs):
        return self.create(request=request, *args, **kwargs)


class CharacterReferenceDetailView(generics.GenericAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = CharacterReferenceSerializer
    queryset = CharacterReference.objects.all()
    lookup_field = 'pk'

    def get(self, request, pk):
        if not request.user.is_anonymous:
            return self.retrieve(request=request, pk=pk)
        else:
            # return just basic info for anonymous users
            ref = get_object_or_404(CharacterReference, id=pk)
            return Response(AnonymousCharacterReferenceSerializer(ref, context={'request': request}).data)

    def put(self, request, pk):
        return self.partial_update(request=request, pk=pk)

    def delete(self, request, pk):
        return self.destroy(request=request, pk=pk)


class OrderAddRemoveOption(APIView):
    authentication_classes = [JWTAuthentication, PermanentTokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # these actions should probably only be allowed to be performed by the sveltekit server via permanent token
    def post(self, request, order_id, option_id, *args, **kwargs):
        order = get_object_or_404(CommissionOrder, id=order_id)
        option = get_object_or_404(CommissionOption, id=option_id)
        order.selected_options.add(option)
        order.calculate_subtotal()
        return Response(CommissionOrderSerializer(order).data)

    def delete(self, request, order_id, option_id, *args, **kwargs):
        order = get_object_or_404(CommissionOrder, id=order_id)
        option = get_object_or_404(CommissionOption, id=option_id)
        order.selected_options.remove(option)
        order.calculate_subtotal()
        return Response(CommissionOrderSerializer(order).data)


class CommissionToggleFeatured(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    lookup_field = 'pk'

    def put(self, request, pk):
        com = get_object_or_404(Commission, id=pk)
        com.toggle_featured()
        return Response(CommissionSerializer(com, context={'request': request}).data)


class CommissionToggleVisibility(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    lookup_field = 'pk'

    def put(self, request, pk):
        com = get_object_or_404(Commission, id=pk)
        com.toggle_visibility()
        return Response(CommissionSerializer(com, context={'request': request}).data)


class CommissionToggleAvailability(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    lookup_field = 'pk'

    def put(self, request, pk):
        com = get_object_or_404(Commission, id=pk)
        com.toggle_availability()
        return Response(CommissionSerializer(com, context={'request': request}).data)


class CommissionIncrementViewCount(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication, PermanentTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    lookup_field = 'pk'

    def put(self, request, pk):
        com = get_object_or_404(Commission, id=pk)
        com.increment_view_count()
        return Response(CommissionSerializer(com, context={'request': request}).data)
