from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Notification,NotificationUser
from ..serializers import NotificationSerializer
from pms.api.custom_pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model




MAINTENANCE_REQUEST_CREATED = "maintenance_request_created"
MAINTENANCE_REQUEST_RESOLVED = "maintenance_request_resolved"
MAINTENANCE_REQUEST_TERMINATED = 'maintenance_request_terminated'
RENT_CREATRD = "rent_created"
RENT_DUE_DATE = "rent_due_date"
RENT_TERMINATED = "rent_terminated"

User = get_user_model()

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
        'user_id__email':['exact'],
        #'user_id__id':['email'],
        'maintenance_request_id__property_id__property_zone_id__owner_id__email': ['exact'],
        'maintenance_request_id__property_id__property_zone_id__manager_id__email': ['exact'],
        'payment_id__rent_id__property_id__property_zone_id__owner_id__email': ['exact'],
        'payment_id__rent_id__property_id__property_zone_id__manager_id__email': ['exact'],
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



       
# an API for getting unread notifications of a specific user
class NotificationUnreadListView(generics.ListAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_fields = {
    #'name': ['exact', 'icontains'],
    #'zone__zone_owner__email':['exact'],
    'user_id__email':['exact'],
    #'is_read': ['exact']
    }
    search_fields = [field.name for field in Notification._meta.fields]
    ordering_fields = [field.name for field in Notification._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

    def get_queryset(self):
        id = self.kwargs.get('user_id')
        #zone = self.kwargs.get('zone_id')
        
        queryset = super().get_queryset()
        if id is not None:
            try:
               User.objects.get(id=id)
               # Filter the queryset based on the primary key
               linked_notification_ids = NotificationUser.objects.filter(
                    user_id=id
                    ).values_list('notification_id', flat=True)
               #queryset = queryset.filter(zone=ParkingZone.objects.filter(zone_owner=user)).exclude(id__in=NotificationUser.objects.filter(user_id=id)
                #                                              .values_list("notification_id",flat=True))  # Assuming your model has an 'id' field
               queryset = queryset.filter(user_id=id).exclude(notificationuser__user_id=id)
               return queryset
            except:
                raise NotFound(detail="There is no user with the given ID.")
        else:
            # If no 'pk' is provided, return the default queryset (all objects)
            return queryset 



