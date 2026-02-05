from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import OwnerManager
from ..serializers import OwnerManagerSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import ForeignKey, Q



User = get_user_model()


class OwnerManagerListView(generics.ListAPIView):
    queryset = OwnerManager.objects.all()
    serializer_class = OwnerManagerSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = {'owner__id': ['exact'],
                        'manager__id': ['exact'],
                        'property_zone__id': ['exact'],
                        'created_at':['exact','gt','gte','lt','lte'],}
    search_fields = [field.name for field in OwnerManager._meta.fields if not isinstance(field, ForeignKey)] 
    ordering_fields = [field.name for field in OwnerManager._meta.fields if not isinstance(field, ForeignKey)]
    ordering = ['id']
    pagination_class = CustomPagination

    def get_queryset(self):
        return super().get_queryset()

    def filter_queryset(self, queryset):
        request = self.request
        user = request.user
        # If requester is an owner, remove any owner__id filter from query params
        if user.groups.filter(name="owner").exists():
            try:
                params = request._request.GET.copy()
            except Exception:
                params = request.query_params.copy()
            removed = False
            for key in ("owner__id", "owner__id[]"):
                if key in params:
                    params.pop(key, None)
                    removed = True
            if removed:
                request._request.GET = params
                # update raw query string to keep consistency
                try:
                    request._request.META['QUERY_STRING'] = params.urlencode()
                except Exception:
                    pass

        # Apply other filters normally
        queryset = super().filter_queryset(queryset)

        # Finally ensure owners only see allowed records
        if user.groups.filter(name="owner").exists():
            queryset = queryset.filter(Q(owner=user) | Q(property_zone__owner_id=user))

        return queryset



class OwnerManagerRetrieveView(generics.RetrieveAPIView):
    queryset = OwnerManager.objects.all()
    serializer_class = OwnerManagerSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class OwnerManagerUpdateView(generics.UpdateAPIView):
    queryset = OwnerManager.objects.all()
    serializer_class = OwnerManagerSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class OwnerManagerDestroyView(generics.DestroyAPIView):
    queryset = OwnerManager.objects.all()
    serializer_class = OwnerManagerSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        OwnerManager = self.get_object()
        if not OwnerManager:
            return Response({"error":"OwnerManager not found!"}, status=status.HTTP_404_NOT_FOUND)
        OwnerManager.delete()
        #OwnerManager_payment.save()
        return Response({"message":"OwnerManager deleted successfully!"},status=status.HTTP_200_OK)


class OwnerManagerCreateView(generics.CreateAPIView):
    queryset = OwnerManager.objects.all()
    serializer_class = OwnerManagerSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]