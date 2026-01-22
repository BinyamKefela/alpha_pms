from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter, SearchFilter
from ..models import BrokerPropertySaleRequest
from ..serializers import BrokerPropertySaleRequestSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend

BROKER_PROPERTY_SALE_REQUEST_PENDING = "pending"
BROKER_PROPERTY_SALE_REQUEST_APPROVED = "approved"
BROKER_PROPERTY_SALE_REQUEST_REJECTED = "rejected"

class BrokerPropertySaleRequestListView(generics.ListAPIView):
    queryset = BrokerPropertySaleRequest.objects.all()
    serializer_class = BrokerPropertySaleRequestSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["message", "status"]
    ordering_fields = [field.name for field in BrokerPropertySaleRequest._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'broker_property_sale__id': ['exact'],
        'requester__email': ['exact'],
        'requester__id': ['exact'],
        'status': ['exact'],
    }

class BrokerPropertySaleRequestRetrieveView(generics.RetrieveAPIView):
    queryset = BrokerPropertySaleRequest.objects.all()
    serializer_class = BrokerPropertySaleRequestSerializer
    permission_classes = []
    lookup_field = 'id'

class BrokerPropertySaleRequestUpdateView(generics.UpdateAPIView):
    queryset = BrokerPropertySaleRequest.objects.all()
    serializer_class = BrokerPropertySaleRequestSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

class BrokerPropertySaleRequestDestroyView(generics.DestroyAPIView):
    queryset = BrokerPropertySaleRequest.objects.all()
    serializer_class = BrokerPropertySaleRequestSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        broker_property_sale_request = self.get_object()
        if not broker_property_sale_request:
            return Response({"error": "Broker property sale request not found!"}, status=status.HTTP_404_NOT_FOUND)
        broker_property_sale_request.delete()
        return Response({"message": "Broker property sale request deleted successfully!"}, status=status.HTTP_200_OK)

class BrokerPropertySaleRequestCreateView(generics.CreateAPIView):
    queryset = BrokerPropertySaleRequest.objects.all()
    serializer_class = BrokerPropertySaleRequestSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        validated_data['updated_at'] = datetime.datetime.now()
        serializer.save()