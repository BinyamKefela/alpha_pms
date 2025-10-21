from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import BrokerTransaction
from ..serializers import BrokerTransactionSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class BrokerTransactionListView(generics.ListAPIView):
    queryset = BrokerTransaction.objects.all()
    serializer_class = BrokerTransactionSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = {
        'transaction_type':['exact'],
        #'user__id':['exact'],
        #'user__email':['exact'],
        #'user__first_name':['exact'],
        #'user__middle_name':['exact'],
        #'user__last_name':['exact'],

    }
    search_fields = [field.name for field in BrokerTransaction._meta.fields]
    ordering_fields = [field.name for field in BrokerTransaction._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination



class BrokerTransactionRetrieveView(generics.RetrieveAPIView):
    queryset = BrokerTransaction.objects.all()
    serializer_class = BrokerTransactionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class BrokerTransactionUpdateView(generics.UpdateAPIView):
    queryset = BrokerTransaction.objects.all()
    serializer_class = BrokerTransactionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class BrokerTransactionDestroyView(generics.DestroyAPIView):
    queryset = BrokerTransaction.objects.all()
    serializer_class = BrokerTransactionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        BrokerTransaction = self.get_object()
        if not BrokerTransaction:
            return Response({"error":"BrokerTransaction not found!"}, status=status.HTTP_404_NOT_FOUND)
        BrokerTransaction.delete()
        #BrokerTransaction_payment.save()
        return Response({"message":"BrokerTransaction deleted successfully!"},status=status.HTTP_200_OK)


class BrokerTransactionCreateView(generics.CreateAPIView):
    queryset = BrokerTransaction.objects.all()
    serializer_class = BrokerTransactionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]