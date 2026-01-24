from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import CoworkingSpacePicture
from ..serializers import CoworkingSpacePictureSerializer
from pms.api.custom_pagination import CustomPagination
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend



class CoworkingSpacePictureListView(generics.ListAPIView):
    queryset = CoworkingSpacePicture.objects.all()
    serializer_class = CoworkingSpacePictureSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = [field.name for field in CoworkingSpacePicture._meta.fields]
    ordering_fields = [field.name for field in CoworkingSpacePicture._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'CoworkingSpace_id__id'
    }


class CoworkingSpacePictureRetrieveView(generics.RetrieveAPIView):
    queryset = CoworkingSpacePicture.objects.all()
    serializer_class = CoworkingSpacePictureSerializer
    permission_classes = []
    lookup_field = 'id'


class CoworkingSpacePictureUpdateView(generics.UpdateAPIView):
    queryset = CoworkingSpacePicture.objects.all()
    serializer_class = CoworkingSpacePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class CoworkingSpacePictureDestroyView(generics.DestroyAPIView):
    queryset = CoworkingSpacePicture.objects.all()
    serializer_class = CoworkingSpacePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        CoworkingSpace_picture = self.get_object()
        if not CoworkingSpace_picture:
            return Response({"error":"CoworkingSpace picture not found!"}, status=status.HTTP_404_NOT_FOUND)
        CoworkingSpace_picture.delete()
        #CoworkingSpace_picture.save()
        return Response({"message":"CoworkingSpace picture deleted successfully!"},status=status.HTTP_200_OK)


class CoworkingSpacePictureCreateView(generics.CreateAPIView):
    queryset = CoworkingSpacePicture.objects.all()
    serializer_class = CoworkingSpacePictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    
    