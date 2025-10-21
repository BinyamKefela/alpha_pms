from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Property
from ..serializers import PropertySerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend

PROPERTY_AVAILABLE = "available"
PROPERTY_RENT = "rent"
PROPERTY_UNDER_MAINTENANCE = "under_maintenance"

class PropertyListView(generics.ListAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = ["name","property_type","address","city","state"]
    ordering_fields = [field.name for field in Property._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'property_zone_id__name': ['exact'],
        'property_zone_id__owner_id__email':['exact'],
        'property_zone_id__manager_id__email':['exact'],
        'property_zone_id__owner_id__id':['exact'],
        'property_zone_id__manager_id__id':['exact'],
        'status':['exact'],
        'property_zone_id': ['exact'],
        'property_type': ['exact'],
    }

    def get_queryset(self):
        #min_rent = self.request.GET.get("min",None)
        #max_rent = self.request.GET.get("max",None)
        min_rent = int(self.request.GET.get("min", 0))  # Default to 1 if not provided
        max_rent = int(self.request.GET.get("max", 9999999999999))  # Default to 1 if not provided

        queryset = super().get_queryset()
       
        queryset = queryset.filter(rent__gte=min_rent)
        
        queryset = queryset.filter(rent__lte=max_rent)
        return queryset


class PropertyRetrieveView(generics.RetrieveAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class PropertyUpdateView(generics.UpdateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class PropertyDestroyView(generics.DestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        property = self.get_object()
        if not property:
            return Response({"error":"Property not found!"}, status=status.HTTP_404_NOT_FOUND)
        property.delete()
        #subscription_payment.save()
        return Response({"message":"property deleted successfully!"},status=status.HTTP_200_OK)


class PropertyCreateView(generics.CreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    def create(self, request, *args, **kwargs):
        if Property.objects.all().count() > settings.COMPANY_PRICING_PLAN:
            return Response({"error": "You’ve reached your property limit. Upgrade your plan."}, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def perform_update(self,serializer):
        validated_data = serializer.validated_data
        validated_data['updated_at'] = datetime.datetime.now()
        serializer.save()



