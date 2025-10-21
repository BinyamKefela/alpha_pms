from datetime import timedelta
from pms.models import RentCycle
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Payment,Rent,RentCycle
from ..serializers import RentCycleSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.decorators import api_view,permission_classes
from datetime import timezone,timedelta
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend


class RentCycleListView(generics.ListAPIView):
    queryset = RentCycle.objects.all()
    serializer_class = RentCycleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = [field.name for field in RentCycle._meta.fields]
    ordering_fields = [field.name for field in RentCycle._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'rent__property_id__property_zone_id__owner_id__email': ['exact'],
        'rent__property_id__property_zone_id__manager_id__email': ['exact'],
    }


class RentCycleFromRentListView(generics.ListAPIView):
    queryset = RentCycle.objects.all()
    serializer_class = RentCycleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [field.name for field in RentCycle._meta.fields]
    ordering_fields = [field.name for field in RentCycle._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

    def get_queryset(self):
        rent_id = self.kwargs.get('rent_id')
        queryset = super().get_queryset()
        if rent_id is not None:
            try:
               # Filter the queryset based on the primary key
               queryset = queryset.filter(rent_id=Rent.objects.get(id=rent_id))  # Assuming your model has an 'id' field
               return queryset
            except:
                return Response({"error":"there is no rent cycle with the given rent id"},status=status.HTTP_400_BAD_REQUEST)
        else:
            # If no 'pk' is provided, return the default queryset (all objects)
            return queryset 
        

def get_interval_days(payment_cycle):
    cycle_map = {
        "weekly": 7,
        "monthly": 30,
        "quarterly": 90,
        "yearly": 365,
    }
    return cycle_map.get(payment_cycle.lower(), 30)

#this will be called by a signal to create rent cycles when a rent is created
def generate_cycles_for_rent(rent, start_date=None, months=12):
    if not start_date:
        start_date = rent.start_date.date()

    interval_days = get_interval_days(rent.payment_cycle)
    total_days = 30 * months  # total time span to cover
    current_start = start_date
    cycles = []

    while (current_start - start_date).days < total_days:
        cycle_end = current_start + timedelta(days=interval_days)
        cycles.append(RentCycle(
            rent=rent,
            cycle_start=current_start,
            cycle_end=cycle_end,
            amount_due=rent.rent_amount,
            is_paid=False
        ))
        current_start = cycle_end

    RentCycle.objects.bulk_create(cycles)
