from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import CoworkingSpace
from ..serializers import CoworkingSpaceSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class CoworkingSpaceListView(generics.ListAPIView):
    queryset = CoworkingSpace.objects.all()
    serializer_class = CoworkingSpaceSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = [field.name for field in CoworkingSpace._meta.fields]
    ordering_fields = [field.name for field in CoworkingSpace._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'zone__owner_id__email': ['exact'],
        'zone__owner_id__id': ['exact'],
        'zone__manager_id__email': ['exact'],
        'zone__manager_id__id': ['exact'],
        'zone__id': ['exact'],
    }



class CoworkingSpaceRetrieveView(generics.RetrieveAPIView):
    queryset = CoworkingSpace.objects.all()
    serializer_class = CoworkingSpaceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class CoworkingSpaceUpdateView(generics.UpdateAPIView):
    queryset = CoworkingSpace.objects.all()
    serializer_class = CoworkingSpaceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class CoworkingSpaceDestroyView(generics.DestroyAPIView):
    queryset = CoworkingSpace.objects.all()
    serializer_class = CoworkingSpaceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        CoworkingSpace = self.get_object()
        if not CoworkingSpace:
            return Response({"error":"CoworkingSpace not found!"}, status=status.HTTP_404_NOT_FOUND)
        CoworkingSpace.delete()
        #CoworkingSpace_payment.save()
        return Response({"message":"CoworkingSpace deleted successfully!"},status=status.HTTP_200_OK)


class CoworkingSpaceCreateView(generics.CreateAPIView):
    queryset = CoworkingSpace.objects.all()
    serializer_class = CoworkingSpaceSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]