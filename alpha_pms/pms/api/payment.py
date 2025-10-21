from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Payment,Rent,RentCycle,Notification
from ..serializers import PaymentSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timezone,timedelta
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view,permission_classes



PAYMENT_PENDING = "pending"
PAYMENT_CANCELLED = "cancelled"
PAYMENT_COMPLETE = "payment complete"
PAYMENT_FAILED = "payment failed"

PAYMENT_METHOD_UNSET = "unset"
PAYMENT_CREATED = "unverified payment created"
PAYMENT_VERIFIED = "payment verified"

User = get_user_model()


# Most methods in this class will only be used for changing payment data irregularly without compliance
# with the payment integration gateway

class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = [field.name for field in Payment._meta.fields]
    ordering_fields = [field.name for field in Payment._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'rent_id__property_id__property_zone_id__owner_id__email': ['exact'],
        'rent_id__property_id__property_zone_id__manager_id__email': ['exact'],
        'due_date':['exact','gt','gte','lt','lte'],
        'rent_id':['exact'],
        'payment_method':['exact'],
        'status':['exact'],
    }



class PaymentUserListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [field.name for field in Payment._meta.fields]
    ordering_fields = [field.name for field in Payment._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination

    def get_queryset(self):
        id = self.kwargs.get('id')
        queryset = super().get_queryset()
        if id is not None:
            try:
               # Filter the queryset based on the primary key
               queryset = queryset.filter(user_id=User.objects.get(id=id))  # Assuming your model has an 'id' field
               return queryset
            except:
                return Response({"error":"there is no payment with the given id"},status=status.HTTP_400_BAD_REQUEST)
        else:
            # If no 'pk' is provided, return the default queryset (all objects)
            return queryset 



class PaymentRetrieveView(generics.RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class PaymentUpdateView(generics.UpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class PaymentDestroyView(generics.DestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        payment = self.get_object()
        if not payment:
            return Response({"error":"payment not found!"}, status=status.HTTP_404_NOT_FOUND)
        payment.delete()
        #payment.save()
        return Response({"message":"payment deleted successfully!"},status=status.HTTP_200_OK)


class PaymentCreateView(generics.CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]


    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()

    def perform_update(self,serializer):
        validated_data = serializer.validated_data
        validated_data['updated_at'] = datetime.datetime.now()
        serializer.save()



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def make_payment(request):
    rent_id = request.data.get("rent_id")
    cycle_ids = request.data.get('cycle_ids')
    payment_method = request.data.get("payment_method")
    transaction_id = request.data.get("transaction_id")

    rent = Rent.objects.get(id=rent_id)
    unpaid_cycles = RentCycle.objects.filter(id__in=cycle_ids,rent=rent,is_paid=False)

    total = sum([c.amount_due for c in unpaid_cycles])

    payment = Payment.objects.create(
        rent_id = rent,
        user_id = request.user,
        amount = total,
        due_date = datetime.datetime.now(),
        status = PAYMENT_PENDING,
        payment_method = payment_method,
        transaction_id = transaction_id,
        created_at = datetime.datetime.now()
    )

    for cycle in unpaid_cycles:
        #cycle.is_paid = True
        cycle.payment = payment
        cycle.save()
    try:   
        user_email = User.objects.get(pk=payment.user_id.pk).email
    except:
        return Response({"errror":"there is no user with the given user id"},status=status.HTTP_400_BAD_REQUEST)

    notification = Notification()
    notification.user_id = request.user
    notification.notification_type = PAYMENT_CREATED
    notification.message = f"A new payment by tenant {user_email} was made on {payment.created_at}"
    notification.is_read=False
    notification.payment_id = payment
    notification.created_at = datetime.datetime.now() 
    notification.save()

    

    return Response({"message":f"Paid {len(unpaid_cycles)} cycle(s)", "total_paid": total},status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([])
def approve_payment(request):
    if not request.user.has_perm('pms.change_payment'):
        return Response({"error":"unauthorized access"},status=status.HTTP_403_FORBIDDEN)
    payment_id = request.data.get("payment_id")
    
    payment = Payment.objects.get(id=payment_id)
    unpaid_cycles = RentCycle.objects.filter(payment=payment,is_paid=False)
    payment.status = PAYMENT_COMPLETE
    payment.save()

    total = sum([c.amount_due for c in unpaid_cycles])
    for cycle in unpaid_cycles:
        cycle.is_paid = True
        cycle.payment = payment
        cycle.save()
    
    try:   
        user_email = User.objects.get(pk=payment.user_id.id).email
    except:
        return Response({"errror":"there is no user with the given user id"},status=status.HTTP_400_BAD_REQUEST)

    notification = Notification()
    notification.user_id = request.user
    notification.notification_type = PAYMENT_CREATED
    notification.message = f"A payment by tenant {user_email} with transaction id {payment.transaction_id} was verified successfully!"
    notification.is_read=False
    notification.payment_id = payment
    notification.created_at = datetime.datetime.now() 
    notification.save()

    return Response({"message":f"payment via {payment.payment_method} with transaction id {payment.transaction_id} approved successfully"},
                    status=status.HTTP_200_OK)


    