from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import MaintenanceRequest,Property,Rent,Notification
from ..serializers import MaintenanceRequestSerializer,MaintenanceRequestSerializerGet
from pms.api.custom_pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import status
import datetime
from rest_framework import serializers
from rest_framework.decorators import api_view,permission_classes
from django.db.models import Q
from .notification import MAINTENANCE_REQUEST_CREATED,MAINTENANCE_REQUEST_TERMINATED,RENT_CREATRD,RENT_DUE_DATE,RENT_TERMINATED
from django_filters.rest_framework import DjangoFilterBackend


PROPERTY_RENT = "rent"
PROPERTY_UNDER_MAINTENANCE = "under_maintenance"
PROPERTY_AVAILABLE = "available"

RENT_ACTIVE = "active"
RENT_EXPIRED = "expired"
RENT_TERMINATED = "terminated"

MAINTENANCE_REQUEST_PENDING = "pending"
MAINTENANCE_REQUEST_RESOLVED = "resolved"

class MaintenanceRequestListView(generics.ListAPIView):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializerGet
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["description"]
    ordering_fields = [field.name for field in MaintenanceRequest._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'property_id__property_zone_id__owner_id__email': ['exact'],
        'property_id__property_zone_id__manager_id__email': ['exact'],
        'property_id__owner_id__email': ['exact'],
        'property_id__manager_id__email': ['exact'],
        'requested_at':['exact','gte','lte','gt','lt'],
        'resolved_at':['exact','gte','lte','gt','lt'],
        'property_id__id':['exact'],
    }

    def get_queryset(self):
        start_date = self.request.GET.get('start_date',None)
        end_date = self.request.GET.get('end_date',None)
        queryset =  super().get_queryset()

        if start_date:
            start_date = datetime.datetime.strptime(start_date,"%Y-%m-%d")
            queryset = queryset.filter(requested_at__gte=start_date)
        if end_date:
            end_date = datetime.datetime.strptime(end_date,"%Y-%m-%d")
            end_date = datetime.datetime.combine(end_date,datetime.datetime.max.time())
            queryset = queryset.filter(requested_at__lte=end_date)

        return queryset
                                                 

        


class MaintenanceRequestRetrieveView(generics.RetrieveAPIView):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class MaintenanceRequestUpdateView(generics.UpdateAPIView):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class MaintenanceRequestDestroyView(generics.DestroyAPIView):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        maintenance_request = self.get_object()
        if not maintenance_request:
            return Response({"error":"maintenance request not found!"}, status=status.HTTP_404_NOT_FOUND)
        maintenance_request.status = MAINTENANCE_REQUEST_TERMINATED
        maintenance_request.save()
        #maintenance_request.save()
        return Response({"message":"maintenance request termnated successfully!"},status=status.HTTP_200_OK)

class MaintenanceRequestCreateView(generics.CreateAPIView):
    queryset = MaintenanceRequest.objects.all()
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def perform_create(self, serializer):
    # Save the instance first
      instance = serializer.save(requested_at=datetime.datetime.now(),status="pending")

    # Handle property status
      try:
        property_obj = Property.objects.get(id=instance.property_id.id)  # Use `.id` if it's a FK
        #if the property being asked for maintenance is already under maintenance
        if property_obj.status == PROPERTY_UNDER_MAINTENANCE:
            raise serializers.ValidationError({"error":"The property is already under maintenance"})
        property_obj.status = PROPERTY_UNDER_MAINTENANCE
        property_obj.save()
      except Property.DoesNotExist:
        raise serializers.ValidationError("No property found with the given ID")
      
      

      instance.save()  # Ensure all changes are saved

      notification = Notification()
      notification.user_id = self.request.user
      notification.notification_type = MAINTENANCE_REQUEST_CREATED
      notification.message = "A new maintenance request for property "+property_obj.name
      notification.is_read=False
      notification.maintenance_request_id = instance
      notification.created_at = datetime.datetime.now() 
      notification.save()



    


    def perform_update(self,serializer):
        validated_data = serializer.validated_data
        validated_data['resolved_at'] = datetime.datetime.now()
        serializer.save()
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resolve_maintenance_request(request):
    if not request.user.has_perm("change_maintenance_request"):
        return Response({"error":"you dont have the permission to perform this action"},status=status.HTTP_405_METHOD_NOT_ALLOWED)
    maintenance_request_id = request.data.get("id")
    try:
        maintenance_request = MaintenanceRequest.objects.get(id=maintenance_request_id,status=MAINTENANCE_REQUEST_PENDING)
        try:
            #checking whether there is a property associated with the given maintenance
            property = Property.objects.get(id=maintenance_request.property_id.pk)
        except:
            return Response({"error":"there is no property associated with the given maintenace request"}, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({"error":"there is no active maintenance request with the given id"},status=status.HTTP_404_NOT_FOUND)
    
    maintenance_request.status="resolved"
    #returning the property status to its previous status,rent or active
    property.status = PROPERTY_RENT if (Rent.objects.filter(property_id=property.id,status=RENT_ACTIVE).count()>0) else PROPERTY_AVAILABLE
    
    try:
       #first update the existing notifications read status to true
       notification = Notification.objects.get(maintenance_request_id=maintenance_request,notification_type="maintenance_request_created")
       notification.is_read=True
       notification.read_at = datetime.datetime.now()

       #crating a new notification for the resolve of the maintenance request
       new_notification = Notification()
       new_notification.user_id = request.user
       new_notification.notification_type = MAINTENANCE_REQUEST_RESOLVED
       new_notification.message = "maintenance request for "+property.name+" has been resolved successfully!"
       new_notification.is_read=False
       new_notification.maintenance_request_id = maintenance_request
       new_notification.created_at = datetime.datetime.now() 
       new_notification.save()
               
    except: 
        return Response({"error":"there was an error in resolving the maintenance request"},status=status.HTTP_400_BAD_REQUEST)
    maintenance_request.save()
    property.save()
    notification.save()
    return Response({"message":"maintenance request resolved successfully!"},status=status.HTTP_200_OK)