from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import SalesPaymentPicture
from ..serializers import SalesPaymentPictureSerializer
from pms.api.custom_pagination import CustomPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend



class SalesPaymentPictureListView(generics.ListAPIView):
    queryset = SalesPaymentPicture.objects.all()
    serializer_class = SalesPaymentPictureSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = [field.name for field in SalesPaymentPicture._meta.fields]
    ordering_fields = [field.name for field in SalesPaymentPicture._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'sales_payment__property_zone_id__id'
        'sales_payment__property_zone_sale_id__id':['exact'],
        'sales_payment__property_zone_sale_id__property_id__id':['exact'],
        'sales_payment__property_zone_sale_id__property_zone_id__id':['exact'],
        'sales_payment__property_zone_sale_id__property_zone_id__owner_id__id':['exact'],
        'sales_payment__property_zone_sale_id__property_zone_id__owner_id__email':['exact'],
        #'property_zone_sale_id__seller__id':['exact'],
        'sales_payment__status':['exact'],
        'sales_payment__payment_method':['exact'],
        'sales_payment__transaction_id':['exact'],
        'sales_payment__buyer_id__email':['exact'],
        'sales_payment__buyer_id__id':['exact'],
        'sales_payment__property_zone_sale_id__id':['exact'],
        'sales_payment__due_date':['exact','gt','gte','lt','lte'],
        'sales_payment__status':['exact'],
    }


class SalesPaymentPictureRetrieveView(generics.RetrieveAPIView):
    queryset = SalesPaymentPicture.objects.all()
    serializer_class = SalesPaymentPictureSerializer
    permission_classes = []
    lookup_field = 'id'


class SalesPaymentPictureUpdateView(generics.UpdateAPIView):
    queryset = SalesPaymentPicture.objects.all()
    serializer_class = SalesPaymentPictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SalesPaymentPictureDestroyView(generics.DestroyAPIView):
    queryset = SalesPaymentPicture.objects.all()
    serializer_class = SalesPaymentPictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        SalesPayment_picture = self.get_object()
        if not SalesPayment_picture:
            return Response({"error":"SalesPayment picture not found!"}, status=status.HTTP_404_NOT_FOUND)
        SalesPayment_picture.delete()
        #SalesPayment_picture.save()
        return Response({"message":"SalesPayment picture deleted successfully!"},status=status.HTTP_200_OK)


class SalesPaymentPictureCreateView(generics.CreateAPIView):
    queryset = SalesPaymentPicture.objects.all()
    serializer_class = SalesPaymentPictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    