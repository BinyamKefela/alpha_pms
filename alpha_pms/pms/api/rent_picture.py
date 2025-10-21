from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import RentPicture
from ..serializers import RentPictureSerializer
from pms.api.custom_pagination import CustomPagination


class RentPictureListView(generics.ListAPIView):
    queryset = RentPicture.objects.all()
    serializer_class = RentPictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [field.name for field in RentPicture._meta.fields]
    ordering_fields = [field.name for field in RentPicture._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination


class RentPictureRetrieveView(generics.RetrieveAPIView):
    queryset = RentPicture.objects.all()
    serializer_class = RentPictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class RentPictureUpdateView(generics.UpdateAPIView):
    queryset = RentPicture.objects.all()
    serializer_class = RentPictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class RentPictureDestroyView(generics.DestroyAPIView):
    queryset = RentPicture.objects.all()
    serializer_class = RentPictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        rent_picture = self.get_object()
        if not rent_picture:
            return Response({"error":"Rent picture not found!"}, status=status.HTTP_404_NOT_FOUND)
        rent_picture.delete()
        #rent_picture.save()
        return Response({"message":"Rent picture deleted successfully!"},status=status.HTTP_200_OK)


class RentPictureCreateView(generics.CreateAPIView):
    queryset = RentPicture.objects.all()
    serializer_class = RentPictureSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    