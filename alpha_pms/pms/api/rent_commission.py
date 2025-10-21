from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import RentCommission
from ..serializers import RentCommissionSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class RentCommissionListView(generics.ListAPIView):
    queryset = RentCommission.objects.all()
    serializer_class = RentCommissionSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = [field.name for field in RentCommission._meta.fields]
    ordering_fields = [field.name for field in RentCommission._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        #'rent_property_zone_sale_id__id':['exact'],
        'rent__property_id__id':['exact'],
        'rent__property_id__property_zone_id__id':['exact'],
        #'property_sale__property_zone_sale_id__property_zone_id__id':['exact'],
        #'property_sale__property_zone_sale_id__property_zone_id__owner_id__id':['exact'],
        #'property_sale__property_zone_sale_id__property_zone_id__owner_id__email':['exact'],
        #'property_zone_sale_id__seller__id':['exact'],
        #'property_sale__status':['exact'],
        #'property_sale__payment_method':['exact'],
        #'property_sale__transaction_id':['exact'],
        #'property_sale__buyer_id__email':['exact'],
        #'property_sale__buyer_id__id':['exact'],
        #'property_sale__property_zone_sale_id__id':['exact'],
    }



class RentCommissionRetrieveView(generics.RetrieveAPIView):
    queryset = RentCommission.objects.all()
    serializer_class = RentCommissionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class RentCommissionUpdateView(generics.UpdateAPIView):
    queryset = RentCommission.objects.all()
    serializer_class = RentCommissionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class RentCommissionDestroyView(generics.DestroyAPIView):
    queryset = RentCommission.objects.all()
    serializer_class = RentCommissionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        RentCommission = self.get_object()
        if not RentCommission:
            return Response({"error":"RentCommission not found!"}, status=status.HTTP_404_NOT_FOUND)
        RentCommission.delete()
        #RentCommission_payment.save()
        return Response({"message":"RentCommission deleted successfully!"},status=status.HTTP_200_OK)


class RentCommissionCreateView(generics.CreateAPIView):
    queryset = RentCommission.objects.all()
    serializer_class = RentCommissionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]