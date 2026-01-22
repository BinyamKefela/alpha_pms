from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter, SearchFilter
from ..models import BrokerPropertySalePicture
from ..serializers import BrokerPropertySalePictureSerializer
from pms.api.custom_pagination import CustomPagination
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend

class BrokerPropertySalePictureListView(generics.ListAPIView):
    queryset = BrokerPropertySalePicture.objects.all()
    serializer_class = BrokerPropertySalePictureSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [field.name for field in BrokerPropertySalePicture._meta.fields]
    ordering_fields = [field.name for field in BrokerPropertySalePicture._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'broker_property_sale__id': ['exact'],
    }

class BrokerPropertySalePictureRetrieveView(generics.RetrieveAPIView):
    queryset = BrokerPropertySalePicture.objects.all()
    serializer_class = BrokerPropertySalePictureSerializer
    permission_classes = []
    lookup_field = 'id'

class BrokerPropertySalePictureUpdateView(generics.UpdateAPIView):
    queryset = BrokerPropertySalePicture.objects.all()
    serializer_class = BrokerPropertySalePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

class BrokerPropertySalePictureDestroyView(generics.DestroyAPIView):
    queryset = BrokerPropertySalePicture.objects.all()
    serializer_class = BrokerPropertySalePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        broker_property_sale_picture = self.get_object()
        if not broker_property_sale_picture:
            return Response({"error": "Broker property sale picture not found!"}, status=status.HTTP_404_NOT_FOUND)
        broker_property_sale_picture.delete()
        return Response({"message": "Broker property sale picture deleted successfully!"}, status=status.HTTP_200_OK)

class BrokerPropertySalePictureCreateView(generics.CreateAPIView):
    queryset = BrokerPropertySalePicture.objects.all()
    serializer_class = BrokerPropertySalePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]