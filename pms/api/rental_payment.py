from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import RentalPayment
from ..serializers import RentalPaymentSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class RentalPaymentListView(generics.ListAPIView):
    queryset = RentalPayment.objects.all()
    serializer_class = RentalPaymentSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = [field.name for field in RentalPayment._meta.fields]
    ordering_fields = [field.name for field in RentalPayment._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'rental__space__zone__owner_id__email': ['exact'],
        'rental__id':['exact'],
        'rental__space__zone__owner_id__id': ['exact'],
        'rental__space__zone__manager_id__email': ['exact'],
        'rental__space__zone__manager_id__id': ['exact'],
        'rental__space__id': ['exact'],
        'rental__guest_email': ['exact'],
        'rental__start_date': ['exact','gt','gte','lt','lte'],
        'rental__next_due_date': ['exact','gt','gte','lt','lte'],
        'paid_at': ['exact','gt','gte','lt','lte'],
        'cycle_start': ['exact','gt','gte','lt','lte'],
        'cycle_end': ['exact','gt','gte','lt','lte'],
        'status':['exact'],
    }
    



class RentalPaymentRetrieveView(generics.RetrieveAPIView):
    queryset = RentalPayment.objects.all()
    serializer_class = RentalPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class RentalPaymentUpdateView(generics.UpdateAPIView):
    queryset = RentalPayment.objects.all()
    serializer_class = RentalPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class RentalPaymentDestroyView(generics.DestroyAPIView):
    queryset = RentalPayment.objects.all()
    serializer_class = RentalPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        RentalPayment = self.get_object()
        if not RentalPayment:
            return Response({"error":"RentalPayment not found!"}, status=status.HTTP_404_NOT_FOUND)
        RentalPayment.delete()
        #RentalPayment_payment.save()
        return Response({"message":"RentalPayment deleted successfully!"},status=status.HTTP_200_OK)


class RentalPaymentCreateView(generics.CreateAPIView):
    queryset = RentalPayment.objects.all()
    serializer_class = RentalPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]