from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Rent,Property,Notification
from ..serializers import RentSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework import status
from rest_framework.response import Response
from .property import PROPERTY_AVAILABLE,PROPERTY_UNDER_MAINTENANCE,PROPERTY_RENT
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view,permission_classes



RENT_ACTIVE = "active"
RENT_TERMINATED = "terminated"

RENT_MONTHLY_CYCLE = "monthly"
RENT_WEEKLY_CYCLE = "weekly"
RENT_QUARTERLY_CYCLE = "quarterly"
RENT_YEARLY_CYCLE = "yearly"

class RentListView(generics.ListAPIView):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = ['status','payment_cycle']
    ordering_fields = [field.name for field in Rent._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'property_id__property_zone_id__owner_id__email': ['exact'],
        'property_id__property_zone_id__manager_id__email': ['exact'],
        'user_id__email':['exact'],
        'user_id':['exact'],
    }

    def get_queryset(self):
        start_date_min = self.request.GET.get('start_date_min',None)
        start_date_max = self.request.GET.get('start_date_max',None)
        end_date_min = self.request.GET.get('end_date_min',None)
        end_date_max = self.request.GET.get("end_date_max",None)
        queryset =  super().get_queryset()

        if start_date_min:
            start_date = datetime.datetime.strptime(start_date_min,"%Y-%m-%d")
            queryset = queryset.filter(start_date__gte=start_date)
        if start_date_max:
            start_date_max = datetime.datetime.strptime(start_date_max,"%Y-%m-%d")
            start_date_max = datetime.datetime.combine(start_date_max,datetime.datetime.max.time())
            queryset = queryset.filter(start_date__lte=start_date_max)
        if end_date_min:
            end_date_min = datetime.datetime.strptime(end_date_min,"%Y-%m-%d")
            queryset = queryset.filter(end_date__gte=end_date_min) 
        if end_date_max:
            end_date_max = datetime.datetime.strptime(end_date_max,"%Y-%m-%d")
            end_date_max = datetime.datetime.combine(end_date_max,datetime.datetime.max.time())
            queryset = queryset.filter(end_date__lte=end_date_max)

        return queryset


class RentRetrieveView(generics.RetrieveAPIView):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class RentUpdateView(generics.UpdateAPIView):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        validate_data = serializer.validated_data
        validate_data["updated_at"] = datetime.datetime.now()
        serializer.save()
        #return super().update(request, *args, **kwargs)


class RentDestroyView(generics.DestroyAPIView):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        rent = self.get_object()
        if not Rent:
            return Response({"error":"Rent not found!"}, status=status.HTTP_404_NOT_FOUND)
        rent.status = RENT_TERMINATED
        try:
            property = Property.objects.get(id=rent.property_id,status=PROPERTY_AVAILABLE)
            property.updated_at = datetime.datetime.now()
        except:
            return Response({"error":"there is no property associated with this rent!"})
        rent.delete()
        #Rent.save()
        return Response({"message":"Rent deleted successfully!"},status=status.HTTP_200_OK)


class RentCreateView(generics.CreateAPIView):
    queryset = Rent.objects.all()
    serializer_class = RentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        try:
            property_status = Property.objects.get(id=int(self.request.data.get("property_id"))).status
        except:
            return Response({"error":"There is no property with the given property id"},status.HTTP_404_NOT_FOUND)
        if property_status == "rent" or property_status == "under_maintenance":
            return Response({"error":"This property is not available for rent!"},status=status.HTTP_400_BAD_REQUEST)
        try:
            property = Property.objects.get(pk=int(self.request.data.get("property_id")))
            property.status = PROPERTY_RENT
            property.save()
        except:
            return Response({"error":"the property is either under maintenace or already rent"},status=status.HTTP_400_BAD_REQUEST)
        rent = serializer.save(status=RENT_ACTIVE)

        notification = Notification()
        notification.user_id = self.request.user
        notification.notification_type = "rent_created"
        notification.message = "A new rent created for user "+str(rent.user_id.email)
        notification.is_read=False
        notification.rent_id = rent
        notification.created_at = datetime.datetime.now() 
        notification.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


        ''' def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        try:
            property_status = Property.objects.get(pk=validated_data['property_id']).status
        except:
            return Response({"error":"There is no property with the given property id"},status.HTTP_404_NOT_FOUND)
        if property_status == "rent" or property_status == "under_maintenance":
            return Response({"error":"This property is not available for rent!"},status=status.HTTP_400_BAD_REQUEST)
        try:
            property = Property.objects.get(pk=validated_data['property_id'])
            property.status = "rent"
            property.save()
        except:
            return Response({"error":"there is no property with the given property id"},status=status.HTTP_400_BAD_REQUEST)
        serializer.save()'''

    def perform_update(self,serializer):
        validated_data = serializer.validated_data
        validated_data['updated_at'] = datetime.datetime.now()
        serializer.save()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_staff_rents(request):
    staff = request.user
    from ..models import OwnerManager
    manager_emails = OwnerManager.objects.filter(owner=staff).values_list('manager__email',flat=True)
    rents = Rent.objects.filter(property_id__property_zone_id__manager_id__email__in=manager_emails)
    paginator = CustomPagination()
    paginated_rents = paginator.paginate_queryset(rents, request)
    serializer = RentSerializer(paginated_rents, many=True)
    return paginator.get_paginated_response(serializer.data)
    #return Response({}RentSerializer(rents,many=True).data)    