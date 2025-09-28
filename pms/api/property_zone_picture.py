from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import PropertyZonePicture
from ..serializers import PropertyZonePictureSerializer
from pms.api.custom_pagination import CustomPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend



class PropertyZonePictureListView(generics.ListAPIView):
    queryset = PropertyZonePicture.objects.all()
    serializer_class = PropertyZonePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = [field.name for field in PropertyZonePicture._meta.fields]
    ordering_fields = [field.name for field in PropertyZonePicture._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'property_zone_id__id'
    }


class PropertyZonePictureRetrieveView(generics.RetrieveAPIView):
    queryset = PropertyZonePicture.objects.all()
    serializer_class = PropertyZonePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class PropertyZonePictureUpdateView(generics.UpdateAPIView):
    queryset = PropertyZonePicture.objects.all()
    serializer_class = PropertyZonePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class PropertyZonePictureDestroyView(generics.DestroyAPIView):
    queryset = PropertyZonePicture.objects.all()
    serializer_class = PropertyZonePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        PropertyZone_picture = self.get_object()
        if not PropertyZone_picture:
            return Response({"error":"PropertyZone picture not found!"}, status=status.HTTP_404_NOT_FOUND)
        PropertyZone_picture.delete()
        #PropertyZone_picture.save()
        return Response({"message":"PropertyZone picture deleted successfully!"},status=status.HTTP_200_OK)


class PropertyZonePictureCreateView(generics.CreateAPIView):
    queryset = PropertyZonePicture.objects.all()
    serializer_class = PropertyZonePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    