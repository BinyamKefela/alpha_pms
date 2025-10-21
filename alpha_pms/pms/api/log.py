from rest_framework.generics import ListAPIView
from auditlog.models import LogEntry
from ..serializers import LogEntrySerializer
from pms.api.custom_pagination import CustomPagination
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter

class LogEntryListAPIView(ListAPIView):
    queryset = LogEntry.objects.select_related('actor').all().order_by('-timestamp')
    serializer_class = LogEntrySerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [field.name for field in LogEntry._meta.fields]
    ordering_fields = [field.name for field in LogEntry._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

