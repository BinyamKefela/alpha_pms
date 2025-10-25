from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from django.conf import settings
import datetime

from ..models import PropertyZone
from ..serializers import PropertyZoneSerializer
from pms.api.custom_pagination import CustomPagination
from django_filters.rest_framework import DjangoFilterBackend


class PropertyZoneListView(generics.ListAPIView):
    queryset = PropertyZone.objects.all()
    serializer_class = PropertyZoneSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = ["name", "address", "city", "state"]
    ordering_fields = [field.name for field in PropertyZone._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'owner_id__email': ['exact'],
        'manager_id__email': ['exact'],
        'name':['exact','icontains'],
    }

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset


class PropertyZoneRetrieveView(generics.RetrieveAPIView):
    queryset = PropertyZone.objects.all()
    serializer_class = PropertyZoneSerializer
    permission_classes = []
    lookup_field = 'id'


class PropertyZoneUpdateView(generics.UpdateAPIView):
    queryset = PropertyZone.objects.all()
    serializer_class = PropertyZoneSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        validated_data['updated_at'] = datetime.datetime.now()
        serializer.save()


class PropertyZoneDestroyView(generics.DestroyAPIView):
    queryset = PropertyZone.objects.all()
    serializer_class = PropertyZoneSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        zone = self.get_object()
        if not zone:
            return Response({"error": "Property zone not found!"}, status=status.HTTP_404_NOT_FOUND)
        zone.delete()
        return Response({"message": "Property zone deleted successfully!"}, status=status.HTTP_200_OK)


class PropertyZoneCreateView(generics.CreateAPIView):
    queryset = PropertyZone.objects.all()
    serializer_class = PropertyZoneSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    def create(self, request, *args, **kwargs):
        if PropertyZone.objects.count() >= settings.COMPANY_PRICING_PLAN:
            return Response({"error": "You’ve reached your zone limit. Upgrade your plan."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)
