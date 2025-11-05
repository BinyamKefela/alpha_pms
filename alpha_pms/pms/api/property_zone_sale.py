from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import PropertyZone, PropertyZoneSale,Property,Notification
from ..serializers import PropertyZoneSaleSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework import status
from rest_framework.response import Response
from .property import PROPERTY_AVAILABLE,PROPERTY_UNDER_MAINTENANCE
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import ForeignKey

from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction




PropertyZoneSale_ACTIVE = "active"
PropertyZoneSale_TERMINATED = "terminated"

PropertyZoneSale_MONTHLY_CYCLE = "monthly"
PropertyZoneSale_WEEKLY_CYCLE = "weekly"
PropertyZoneSale_QUARTERLY_CYCLE = "quarterly"
PropertyZoneSale_YEARLY_CYCLE = "yearly"

class PropertyZoneSaleListView(generics.ListAPIView):
    queryset = PropertyZoneSale.objects.all()
    serializer_class = PropertyZoneSaleSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    filterset_fields = {'broker__id': ['exact'],
                        #'buyer__id': ['exact'],
                        'property_id__id':['exact'],
                        'property_zone_id__id':['exact'],
                        'property_id__property_zone_id__id':['exact'],
                        'property_id__owner_id__id':['exact'],
                        'property_id__manager_id__id':['exact'],
                        'status':['exact'],}

    search_fields = [field.name for field in PropertyZoneSale._meta.fields if not isinstance(field, ForeignKey)] 
    ordering_fields = [field.name for field in PropertyZoneSale._meta.fields if not isinstance(field, ForeignKey)]
    ordering = ['id']
    pagination_class = CustomPagination

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


class PropertyZoneSaleRetrieveView(generics.RetrieveAPIView):
    queryset = PropertyZoneSale.objects.all()
    serializer_class = PropertyZoneSaleSerializer
    permission_classes = []
    lookup_field = 'id'


class PropertyZoneSaleUpdateView(generics.UpdateAPIView):
    queryset = PropertyZoneSale.objects.all()
    serializer_class = PropertyZoneSaleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        validate_data = serializer.validated_data
        validate_data["updated_at"] = datetime.datetime.now()
        serializer.save()
        return super().update(request, *args, **kwargs)


class PropertyZoneSaleDestroyView(generics.DestroyAPIView):
    queryset = PropertyZoneSale.objects.all()
    serializer_class = PropertyZoneSaleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        PropertyZoneSale = self.get_object()
        if not PropertyZoneSale:
            return Response({"error":"property sale not found!"}, status=status.HTTP_404_NOT_FOUND)
        PropertyZoneSale.status = PropertyZoneSale_TERMINATED
        try:
            property = Property.objects.get(id=PropertyZoneSale.property_id,status=PROPERTY_AVAILABLE)
            property.updated_at = datetime.datetime.now()
        except:
            return Response({"error":"there is no property associated with this property sale!"})
        PropertyZoneSale.delete()
        #PropertyZoneSale.save()
        return Response({"message":"property sale deleted successfully!"},status=status.HTTP_200_OK)


class PropertyZoneSaleCreateView(generics.CreateAPIView):
    queryset = PropertyZoneSale.objects.all()
    serializer_class = PropertyZoneSaleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]



@api_view(['POST'])
@permission_classes([AllowAny])
def sell_property(request):
    with transaction.atomic():
      if request.data.get("property_id") is None and request.data.get("property_zone_id") is None:
            return Response({"error":"please provide either property id or property zone id"},status=status.HTTP_400_BAD_REQUEST)
      serializer = PropertyZoneSaleSerializer(data=request.data)
      if serializer.is_valid():
          validated_data = serializer.validated_data
          validated_data['created_at'] = datetime.datetime.now()
          '''try:
              property_status = Property.objects.get(id=int(request.data.get("property_id"))).status
          except:
              return Response({"error":"There is no property with the given property id"},status.HTTP_404_NOT_FOUND)'''
          try:
              if request.data.get("property_id"):
                  property = Property.objects.get(pk=int(request.data.get("property_id")))
                  property.owner_id = request.data.get("buyer_id")
                  property.save()
              elif request.data.get("property_zone_id"):
                  property_zone = PropertyZone.objects.get(pk=int(request.data.get("property_zone_id")))
                  property_zone.owner_id = request.data.get("buyer_id")
                  property_zone.save()
              
          except:
              if request.data.get("property_id"):
                  return Response({"error":"there is no property with the given property id"},status=status.HTTP_400_BAD_REQUEST)
              return Response({"error":"there is no property with the given property zone id"},status=status.HTTP_400_BAD_REQUEST)
          property_zone_sale = serializer.save(status=PropertyZoneSale.PROPERTY_SALE_STATUS_CHOICES[1][0])
          if request.data.get("broker_id"):
              property_zone_sale.broker = request.data.get("broker_id")
              property_zone_sale.save()
          property_zone_sale.selling_price = request.data.get("selling_price")
          from ..models import SAASTransaction,BrokerTransaction,Commission
          Commission = Commission.objects.first()
          saas_commission_rate = Commission.saas_commission if Commission else 0.00
          saas_transaction = SAASTransaction.objects.create(
              user_id=request.user.id,
              property_sale_id=property_zone_sale.id,
              amount=property_zone_sale.selling_price * saas_commission_rate / 100,
              created_at=datetime.datetime.now()
          )
          broker_commission_rate = Commission.broker_commission if Commission else 0.00
          if property_zone_sale.broker:
              broker_transaction = BrokerTransaction.objects.create(
                  broker_id=property_zone_sale.broker.id,
                  property_sale_id=property_zone_sale.id,
                  amount=property_zone_sale.selling_price * broker_commission_rate / 100,
                  created_at=datetime.datetime.now()
              )
          

          notification = Notification()
          notification.user_id = request.user
          notification.notification_type = "PropertyZoneSale_created"
          notification.message = "A new property sale created for user "+str(PropertyZoneSale.seller.email)
          notification.is_read=False
          notification.property_sale_id = PropertyZoneSale
          notification.created_at = datetime.datetime.now() 
          notification.save()

          return Response(serializer.data, status=status.HTTP_201_CREATED)
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_property_sale_listing(request):
    property_id = request.data.get("property_id")
    #buyer_id = request.data.get("buyer_id")
    property_zone_id = request.data.get("property_zone_id")
    #broker = request.data.get("broker_id")
    listing_price = request.data.get("listing_price")

    if not (property_id or property_zone_id):
        return Response({"error":"please provide either property or property zone to be sold"},status=status.HTTP_400_BAD_REQUEST)
    
    if not listing_price:
        return Response({"error":"please provide listing price"},status=status.HTTP_400_BAD_REQUEST)
    
    property_zone_sale = PropertyZoneSale()
    if property_id:
        property_zone_sale.property_id = property_id
    else:
        property_zone_sale.property_zone_id = property_zone_id
    property_zone_sale.listing_price = listing_price
    property_zone_sale.status = PropertyZoneSale.PROPERTY_SALE_STATUS_CHOICES[0]
    
    property_zone_sale.save()
    return Response({"message":"successfully created sales listing"},status=status.HTTP_201_CREATED)



    




    