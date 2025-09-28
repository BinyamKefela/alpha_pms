from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Notification
from ..serializers import NotificationSerializer
from pms.api.custom_pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend

MAINTENANCE_REQUEST_CREATED = "maintenance_request_created"
MAINTENANCE_REQUEST_RESOLVED = "maintenance_request_resolved"
MAINTENANCE_REQUEST_TERMINATED = 'maintenance_request_terminated'
RENT_CREATRD = "rent_created"
RENT_DUE_DATE = "rent_due_date"
RENT_TERMINATED = "rent_terminated"


class NotificationListView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [field.name for field in Notification._meta.fields]
    ordering_fields = [field.name for field in Notification._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'maintenance_request_id__property_id__property_zone_id__owner_id__email': ['exact'],
        'maintenance_request_id__property_id__property_zone_id__manager_id__email': ['exact'],
        'payment_id__property_id__property_zone_id__owner_id__email': ['exact'],
        'payment_id__property_id__property_zone_id__manager_id__email': ['exact'],
        'rent_id__property_id__property_zone_id__owner_id__email': ['exact'],
        'rent_id__property_id__property_zone_id__manager_id__email': ['exact'],
    }


class UnreadNotificationListView(generics.ListAPIView):
    queryset = Notification.objects.filter(is_read=False)
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [field.name for field in Notification._meta.fields]
    ordering_fields = [field.name for field in Notification._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination



class NotificationRetrieveView(generics.RetrieveAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class NotificationUpdateView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class NotificationDestroyView(generics.DestroyAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        notification = self.get_object()
        if not notification:
            return Response({"error":"notification not found!"}, status=status.HTTP_404_NOT_FOUND)
        notification.delete()
        #notification.save()
        return Response({"message":"notification deleted successfully!"},status=status.HTTP_200_OK)



class NotificationCreateView(generics.CreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    