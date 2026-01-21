from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import WorkSpaceRental,CoworkingSpace
from ..serializers import WorkSpaceRentalSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend



User = get_user_model()


class WorkSpaceRentalListView(generics.ListAPIView):
    queryset = WorkSpaceRental.objects.all()
    serializer_class = WorkSpaceRentalSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = [field.name for field in WorkSpaceRental._meta.fields]
    ordering_fields = [field.name for field in WorkSpaceRental._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'space__zone__owner_id__email': ['exact'],
        'space__zone__owner_id__id': ['exact'],
        'space__zone__manager_id__email': ['exact'],
        'space__zone__manager_id__id': ['exact'],
        'space__id': ['exact'],
        'guest_email': ['exact'],
        'start_date': ['exact','gt','gte','lt','lte'],
        'next_due_date': ['exact','gt','gte','lt','lte'],
        'status':['exact'],
        'user__email':['exact'],
        'user__id':['exact']
    }



class WorkSpaceRentalRetrieveView(generics.RetrieveAPIView):
    queryset = WorkSpaceRental.objects.all()
    serializer_class = WorkSpaceRentalSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class WorkSpaceRentalUpdateView(generics.UpdateAPIView):
    queryset = WorkSpaceRental.objects.all()
    serializer_class = WorkSpaceRentalSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class WorkSpaceRentalDestroyView(generics.DestroyAPIView):
    queryset = WorkSpaceRental.objects.all()
    serializer_class = WorkSpaceRentalSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        WorkSpaceRental = self.get_object()
        if not WorkSpaceRental:
            return Response({"error":"WorkSpaceRental not found!"}, status=status.HTTP_404_NOT_FOUND)
        WorkSpaceRental.delete()
        #WorkSpaceRental_payment.save()
        return Response({"message":"WorkSpaceRental deleted successfully!"},status=status.HTTP_200_OK)


class WorkSpaceRentalCreateView(generics.CreateAPIView):
    queryset = WorkSpaceRental.objects.all()
    serializer_class = WorkSpaceRentalSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def create(self, request, *args, **kwargs):
        space_id = request.data.get('space')
        try:
            space = CoworkingSpace.objects.get(id=space_id)
            if space.capacity< WorkSpaceRental.objects.filter(is_active=True,space=space).count():
                return Response({"error":"There is no free space in the given workspace"},status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error":"there is no coworking space with the given coworking space id"},status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)