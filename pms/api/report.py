from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Report
from ..serializers import ReportSerializer
from pms.api.custom_pagination import CustomPagination
import datetime


class ReportListView(generics.ListAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [field.name for field in Report._meta.fields]
    ordering_fields = [field.name for field in Report._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination


class ReportRetrieveView(generics.RetrieveAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ReportUpdateView(generics.UpdateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class ReportDestroyView(generics.DestroyAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'
    
    def destroy(self, request, *args, **kwargs):
        report = self.get_object()
        if not report:
            return Response({"error":"report not found!"}, status=status.HTTP_404_NOT_FOUND)
        report.delete()
        #report.save()
        return Response({"message":"report deleted successfully!"},status=status.HTTP_200_OK)


class ReportCreateView(generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    
    