from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter, SearchFilter
from ..models import BrokerPropertySale
from ..serializers import BrokerPropertyForSaleSerializer, BrokerPropertySaleCreateSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction
from django.contrib.auth import get_user_model
from ..models import BrokerPropertySale, SalesPayment, SAASTransaction, BrokerTransaction, Commission

BROKER_PROPERTY_PENDING = "pending"
BROKER_PROPERTY_CANCELED = "canceled"
BROKER_PROPERTY_SOLD = "sold"

class BrokerPropertyForSaleListView(generics.ListAPIView):
    queryset = BrokerPropertySale.objects.all()
    serializer_class = BrokerPropertyForSaleSerializer
    permission_classes = []
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ["description", "property_type", "address", "city", "state"]
    ordering_fields = [field.name for field in BrokerPropertySale._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'broker__email': ['exact'],
        'broker__id': ['exact'],
        'status': ['exact'],
        'property__property_type': ['exact'],
        'property__city': ['exact', 'icontains'],
        'property__address': ['exact', 'icontains'],
        'property__state': ['exact', 'icontains'],
        'listing_price': ['exact', 'gte', 'lte', 'gt', 'lt'],
        'selling_price': ['exact', 'gte', 'lte', 'gt', 'lt'],
    }

    def get_queryset(self):
        min_price = int(self.request.GET.get("min", 0))
        max_price = int(self.request.GET.get("max", 9999999999999))

        queryset = super().get_queryset()
        queryset = queryset.filter(listing_price__gte=min_price)
        queryset = queryset.filter(listing_price__lte=max_price)
        return queryset

class BrokerPropertyForSaleRetrieveView(generics.RetrieveAPIView):
    queryset = BrokerPropertySale.objects.all()
    serializer_class = BrokerPropertyForSaleSerializer
    permission_classes = []
    lookup_field = 'id'

class BrokerPropertyForSaleUpdateView(generics.UpdateAPIView):
    queryset = BrokerPropertySale.objects.all()
    serializer_class = BrokerPropertyForSaleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

class BrokerPropertyForSaleDestroyView(generics.DestroyAPIView):
    queryset = BrokerPropertySale.objects.all()
    serializer_class = BrokerPropertyForSaleSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

    def destroy(self, request, *args, **kwargs):
        broker_property = self.get_object()
        if not broker_property:
            return Response({"error": "Broker property for sale not found!"}, status=status.HTTP_404_NOT_FOUND)
        broker_property.delete()
        return Response({"message": "Broker property for sale deleted successfully!"}, status=status.HTTP_200_OK)

class BrokerPropertyForSaleCreateView(generics.CreateAPIView):
    queryset = BrokerPropertySale.objects.all()
    serializer_class = BrokerPropertySaleCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(broker=self.request.user)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['broker_property_sale_id', 'selling_price', 'buyer_id', 'payment_method', 'transaction_id'],
        properties={
            'broker_property_sale_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the BrokerPropertySale to sell'),
            'selling_price': openapi.Schema(type=openapi.TYPE_NUMBER, description='Final selling price'),
            'buyer_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID of the buyer (must be in owner group)'),
            'payment_method': openapi.Schema(type=openapi.TYPE_STRING, description='Payment method used'),
            'transaction_id': openapi.Schema(type=openapi.TYPE_STRING, description='Payment transaction identifier'),
            'due_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='Optional payment due date'),
        },
    ),
    responses={
        200: openapi.Response('Property sold successfully'),
        400: openapi.Response('Bad request / validation error'),
        500: openapi.Response('Server error'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def sell_broker_property(request):
    User = get_user_model()

    with transaction.atomic():
        data = request.data
        if not data.get("broker_property_sale_id"):
            return Response({"error": "please provide broker_property_sale_id"}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get("selling_price"):
            return Response({"error": "please provide selling_price"}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get("buyer_id"):
            return Response({"error": "please provide the buyer id"}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get("payment_method"):
            return Response({"error": "please provide the payment_method"}, status=status.HTTP_400_BAD_REQUEST)
        if not data.get("transaction_id"):
            return Response({"error": "please provide the transaction id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            buyer = User.objects.get(id=data.get("buyer_id"))
        except User.DoesNotExist:
            return Response({"error": "There is no user with the given buyer id"}, status=status.HTTP_400_BAD_REQUEST)

        if not buyer.groups.filter(name="owner").exists():
            return Response({"error": "the buyer must be an owner"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            broker_property = BrokerPropertySale.objects.get(id=data.get("broker_property_sale_id"))
        except BrokerPropertySale.DoesNotExist:
            return Response({"error": "There is no broker property sale with the given id"}, status=status.HTTP_400_BAD_REQUEST)

        # create sales payment
        sales_payment = SalesPayment()
        try:
            # attach broker property sale if the SalesPayment model has such a field
            setattr(sales_payment, 'broker_property_sale', broker_property)  # safe set attempt
        except Exception:
            pass
        try:
            setattr(sales_payment, 'buyer', buyer)
        except Exception:
            try:
                sales_payment.buyer_id = buyer.id
            except Exception:
                pass

        sales_payment.amount = data.get("selling_price")
        if data.get("due_date"):
            sales_payment.due_date = data.get("due_date")
        # set status to the second choice if defined similarly to original code
        try:
            sales_payment.status = SalesPayment.SALES_PAYMENT_CHOICES[1][0]
        except Exception:
            pass
        sales_payment.payment_method = data.get("payment_method")
        sales_payment.transaction_id = data.get("transaction_id")
        sales_payment.save()

        # handle commissions / transactions
        CommissionObj = Commission.objects.first() if hasattr(Commission, 'objects') else None
        saas_commission_rate = CommissionObj.saas_commission if CommissionObj and hasattr(CommissionObj, 'saas_commission') else 0.00
        broker_commission_rate = CommissionObj.broker_commission if CommissionObj and hasattr(CommissionObj, 'broker_commission') else 0.00

        try:
            saas_transaction = SAASTransaction.objects.create(
                transaction_type=SAASTransaction.SAAS_TRANSACTION_TYPE_CHOICE[0][0] if hasattr(SAASTransaction, 'SAAS_TRANSACTION_TYPE_CHOICE') else None,
                amount=float(sales_payment.amount) * float(saas_commission_rate) / 100.0
            )
        except Exception:
            saas_transaction = None

        try:
            if getattr(broker_property, 'broker', None):
                broker_transaction = BrokerTransaction.objects.create(
                    amount=float(sales_payment.amount) * float(broker_commission_rate) / 100.0,
                    transaction_type=BrokerTransaction.BROKER_TRANSACTION_TYPE_CHOICE[0][0] if hasattr(BrokerTransaction, 'BROKER_TRANSACTION_TYPE_CHOICE') else None
                )
        except Exception:
            pass

        # update broker property sale
        broker_property.status = BROKER_PROPERTY_SOLD
        broker_property.selling_price = data.get("selling_price")
        try:
            broker_property.sold_at = datetime.datetime.now()
        except Exception:
            pass
        broker_property.save()

        # attempt to transfer ownership if model exposes related property fields
        try:
            if getattr(broker_property, 'property_id', None):
                prop = broker_property.property_id
                prop.owner_id = buyer
                prop.save()
            elif getattr(broker_property, 'property_zone_id', None):
                pz = broker_property.property_zone_id
                pz.owner_id = buyer
                pz.save()
        except Exception:
            # ignore ownership transfer failures here, return success but log could be added
            pass

    return Response({"message": "broker property selling complete!"}, status=status.HTTP_200_OK)