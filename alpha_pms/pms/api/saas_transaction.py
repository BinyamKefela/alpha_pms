from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import SAASTransaction
from ..serializers import SAASTransactionSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class SAASTransactionListView(generics.ListAPIView):
    queryset = SAASTransaction.objects.all()
    serializer_class = SAASTransactionSerializer
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
    search_fields = [field.name for field in SAASTransaction._meta.fields]
    ordering_fields = [field.name for field in SAASTransaction._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination



class SAASTransactionRetrieveView(generics.RetrieveAPIView):
    queryset = SAASTransaction.objects.all()
    serializer_class = SAASTransactionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SAASTransactionUpdateView(generics.UpdateAPIView):
    queryset = SAASTransaction.objects.all()
    serializer_class = SAASTransactionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SAASTransactionDestroyView(generics.DestroyAPIView):
    queryset = SAASTransaction.objects.all()
    serializer_class = SAASTransactionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        SAASTransaction = self.get_object()
        if not SAASTransaction:
            return Response({"error":"SAASTransaction not found!"}, status=status.HTTP_404_NOT_FOUND)
        SAASTransaction.delete()
        #SAASTransaction_payment.save()
        return Response({"message":"SAASTransaction deleted successfully!"},status=status.HTTP_200_OK)


class SAASTransactionCreateView(generics.CreateAPIView):
    queryset = SAASTransaction.objects.all()
    serializer_class = SAASTransactionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]