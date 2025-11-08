from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import OwnerStaff
from ..serializers import OwnerStaffSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import ForeignKey



User = get_user_model()


class OwnerStaffListView(generics.ListAPIView):
    queryset = OwnerStaff.objects.all()
    serializer_class = OwnerStaffSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    filterset_fields = {'owner__id': ['exact'],
                        'staff__id': ['exact'],
                        'property_zone__id': ['exact'],
                        'created_at':['exact','gt','gte','lt','lte'],}
    search_fields = [field.name for field in OwnerStaff._meta.fields if not isinstance(field, ForeignKey)] 
    ordering_fields = [field.name for field in OwnerStaff._meta.fields if not isinstance(field, ForeignKey)]
    ordering = ['id']
    pagination_class = CustomPagination



class OwnerStaffRetrieveView(generics.RetrieveAPIView):
    queryset = OwnerStaff.objects.all()
    serializer_class = OwnerStaffSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class OwnerStaffUpdateView(generics.UpdateAPIView):
    queryset = OwnerStaff.objects.all()
    serializer_class = OwnerStaffSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class OwnerStaffDestroyView(generics.DestroyAPIView):
    queryset = OwnerStaff.objects.all()
    serializer_class = OwnerStaffSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        OwnerStaff = self.get_object()
        if not OwnerStaff:
            return Response({"error":"OwnerStaff not found!"}, status=status.HTTP_404_NOT_FOUND)
        OwnerStaff.delete()
        #OwnerStaff_payment.save()
        return Response({"message":"OwnerStaff deleted successfully!"},status=status.HTTP_200_OK)


class OwnerStaffCreateView(generics.CreateAPIView):
    queryset = OwnerStaff.objects.all()
    serializer_class = OwnerStaffSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]