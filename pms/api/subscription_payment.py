from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import SubscriptionPayment
from ..serializers import SubscriptionPaymentSerializer
from pms.api.custom_pagination import CustomPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import ForeignKey
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


class SubscriptionPaymentListView(generics.ListAPIView):
    queryset = SubscriptionPayment.objects.all()
    serializer_class = SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter,DjangoFilterBackend]
    search_fields = [field.name for field in SubscriptionPayment._meta.fields if not isinstance(field, ForeignKey)]
    ordering_fields = [field.name for field in SubscriptionPayment._meta.fields if not isinstance(field, ForeignKey)]
    ordering = ['id']
    filterset_fields = {'subscription_id': ['exact'],
                        'user_id': ['exact'],
                        'paid_at':['exact','gt','gte','lt','lte'],}
    pagination_class = CustomPagination


class SubscriptionPaymentRetrieveView(generics.RetrieveAPIView):
    queryset = SubscriptionPayment.objects.all()
    serializer_class = SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SubscriptionPaymentUpdateView(generics.UpdateAPIView):
    queryset = SubscriptionPayment.objects.all()
    serializer_class = SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SubscriptionPaymentDestroyView(generics.DestroyAPIView):
    queryset = SubscriptionPayment.objects.all()
    serializer_class = SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        subscription_ayment = self.get_object()
        if not subscription_payment:
            return Response({"error":"subscription payment not found!"}, status=status.HTTP_404_NOT_FOUND)
        subscription_payment.delete()
        #subscription_payment.save()
        return Response({"message":"subscription payment deleted successfully!"},status=status.HTTP_200_OK)



class SubscriptionPaymentCreateView(generics.CreateAPIView):
    queryset = SubscriptionPayment.objects.all()
    serializer_class = SubscriptionPaymentSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    