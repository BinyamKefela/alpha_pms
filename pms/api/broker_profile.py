from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import BrokerProfile
from ..serializers import BrokerProfileSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class BrokerProfileListView(generics.ListAPIView):
    queryset = BrokerProfile.objects.all()
    serializer_class = BrokerProfileSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = {
        'license_number':['exact'],
        'user__id':['exact'],
        'user__email':['exact'],
        'user__first_name':['exact'],
        'user__middle_name':['exact'],
        'user__last_name':['exact'],

    }
    search_fields = [field.name for field in BrokerProfile._meta.fields]
    ordering_fields = [field.name for field in BrokerProfile._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination



class BrokerProfileRetrieveView(generics.RetrieveAPIView):
    queryset = BrokerProfile.objects.all()
    serializer_class = BrokerProfileSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class BrokerProfileUpdateView(generics.UpdateAPIView):
    queryset = BrokerProfile.objects.all()
    serializer_class = BrokerProfileSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class BrokerProfileDestroyView(generics.DestroyAPIView):
    queryset = BrokerProfile.objects.all()
    serializer_class = BrokerProfileSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        BrokerProfile = self.get_object()
        if not BrokerProfile:
            return Response({"error":"BrokerProfile not found!"}, status=status.HTTP_404_NOT_FOUND)
        BrokerProfile.delete()
        #BrokerProfile_payment.save()
        return Response({"message":"BrokerProfile deleted successfully!"},status=status.HTTP_200_OK)


class BrokerProfileCreateView(generics.CreateAPIView):
    queryset = BrokerProfile.objects.all()
    serializer_class = BrokerProfileSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]