from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import PropertyPicture
from ..serializers import PropertyPictureSerializer
from pms.api.custom_pagination import CustomPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend



class PropertyPictureListView(generics.ListAPIView):
    queryset = PropertyPicture.objects.all()
    serializer_class = PropertyPictureSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = [field.name for field in PropertyPicture._meta.fields]
    ordering_fields = [field.name for field in PropertyPicture._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'property_id__id'
    }


class PropertyPictureRetrieveView(generics.RetrieveAPIView):
    queryset = PropertyPicture.objects.all()
    serializer_class = PropertyPictureSerializer
    permission_classes = []
    lookup_field = 'id'


class PropertyPictureUpdateView(generics.UpdateAPIView):
    queryset = PropertyPicture.objects.all()
    serializer_class = PropertyPictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class PropertyPictureDestroyView(generics.DestroyAPIView):
    queryset = PropertyPicture.objects.all()
    serializer_class = PropertyPictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        property_picture = self.get_object()
        if not property_picture:
            return Response({"error":"property picture not found!"}, status=status.HTTP_404_NOT_FOUND)
        property_picture.delete()
        #property_picture.save()
        return Response({"message":"property picture deleted successfully!"},status=status.HTTP_200_OK)


class PropertyPictureCreateView(generics.CreateAPIView):
    queryset = PropertyPicture.objects.all()
    serializer_class = PropertyPictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    