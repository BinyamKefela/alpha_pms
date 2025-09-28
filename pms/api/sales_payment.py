from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
import datetime
from django_filters.rest_framework import DjangoFilterBackend



from ..models import SalesPayment,BrokerProfile,Commission
from ..serializers import SalesPaymentSerializer
from pms.api.custom_pagination import CustomPagination


class SalesPaymentListView(generics.ListAPIView):
    queryset = SalesPayment.objects.all()
    serializer_class = SalesPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions,]
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = [
        "status",
        "payment_method",
        "transaction_id",
        "buyer_id__username",
        "property_sale_id__id",
    ]
    filterset_fields = {
        'property_zone_sale_id__id':['exact'],
        'property_zone_sale_id__property_id__id':['exact'],
        'property_zone_sale_id__property_zone_id__id':['exact'],
        'property_zone_sale_id__property_zone_id__owner_id__id':['exact'],
        'property_zone_sale_id__property_zone_id__owner_id__email':['exact'],
        #'property_zone_sale_id__seller__id':['exact'],
        'status':['exact'],
        'payment_method':['exact'],
        'transaction_id':['exact'],
        'buyer_id__email':['exact'],
        'buyer_id__id':['exact'],
        'property_zone_sale_id__id':['exact'],
                        }
    ordering_fields = [field.name for field in SalesPayment._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

    def get_queryset(self):
        return super().get_queryset()


class SalesPaymentRetrieveView(generics.RetrieveAPIView):
    queryset = SalesPayment.objects.all()
    serializer_class = SalesPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SalesPaymentUpdateView(generics.UpdateAPIView):
    queryset = SalesPayment.objects.all()
    serializer_class = SalesPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        validated_data['updated_at'] = datetime.datetime.now()
        serializer.save()


class SalesPaymentDestroyView(generics.DestroyAPIView):
    queryset = SalesPayment.objects.all()
    serializer_class = SalesPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        payment = self.get_object()
        if not payment:
            return Response({"error": "Sales payment not found!"}, status=status.HTTP_404_NOT_FOUND)
        payment.delete()
        return Response({"message": "Sales payment deleted successfully!"}, status=status.HTTP_200_OK)


import datetime
from decimal import Decimal
from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions


class SalesPaymentCreateView(generics.CreateAPIView):
    queryset = SalesPayment.objects.all()
    serializer_class = SalesPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    @transaction.atomic
    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data["created_at"] = datetime.datetime.now()

        payment = serializer.save()

        # Only process ownership transfer if payment is complete
        if payment.status == "complete" and payment.property_zone_sale_id:
            sale = payment.property_zone_sale_id
            buyer = payment.buyer_id

            if buyer:
                if sale.property_id:  # single property sale
                    property_obj = sale.property_id
                    property_obj.owner_id = buyer
                    property_obj.save(update_fields=["owner_id"])
                else:  # whole zone sale
                    zone = sale.property_zone_id
                    zone.owner_id = buyer
                    zone.save(update_fields=["owner_id"])
                    # Optionally transfer all properties in that zone
                    # Property.objects.filter(property_zone_id=zone).update(owner_id=buyer)

            # ---- Commission Handling ----
            if sale.broker:  
                try:
                    broker_profile = sale.broker.broker_profile
                except BrokerProfile.DoesNotExist:
                    broker_profile = None

                if broker_profile:
                    # Commission calculation
                    broker_rate = broker_profile.commission_rate or Decimal("0.02")
                    broker_commission = Decimal(payment.amount) * broker_rate
                    saas_commission = Decimal(payment.amount) * Decimal("0.02")
                    total_commission = broker_commission + saas_commission

                    # Create commission record
                    Commission.objects.create(
                        property_sale=payment,
                        saas_commission=saas_commission,
                        broker_commission=broker_commission,
                        total_commission=total_commission,
                    )

                    # Add to broker wallet
                    broker_profile.wallet += broker_commission
                    broker_profile.save(update_fields=["wallet"])
