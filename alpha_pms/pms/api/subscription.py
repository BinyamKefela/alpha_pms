from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..models import Subscription
from ..serializers import SubscriptionSerializer
from pms.api.custom_pagination import CustomPagination
import datetime
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import ForeignKey
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status


class SubscriptionListView(generics.ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    filter_backends = [DjangoFilterBackend,SearchFilter, OrderingFilter]
    search_fields = [field.name for field in Subscription._meta.fields if not isinstance(field, ForeignKey)]
    ordering_fields = [field.name for field in Subscription._meta.fields if not isinstance(field, ForeignKey)]
    filterset_fields = {'user_id': ['exact'],}
    ordering = ['id']
    pagination_class = CustomPagination
    filterset_fields = {
        'user_id__email':['exact'],
        'user_id__id':['exact'],
        'start_date':['exact','gt','gte','lt','lte'],
        'end_date':['exact','gt','gte','lt','lte'],
        'status':['exact'],
    }


class SubscriptionRetrieveView(generics.RetrieveAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SubscriptionUpdateView(generics.UpdateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'


class SubscriptionDestroyView(generics.DestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field ='id'

    def destroy(self, request, *args, **kwargs):
        subscription = self.get_object()
        if not subscription:
            return Response({"error":"subscription not found!"}, status=status.HTTP_404_NOT_FOUND)
        Subscription.delete()
        #Subscription.save()
        return Response({"message":"subscription deleted successfully!"},status=status.HTTP_200_OK)



class SubscriptionCreateView(generics.CreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [AllowAny]


    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        validated_data['created_at'] = datetime.datetime.now()
        serializer.save()


@api_view(['POST'])
@permission_classes([AllowAny])
def update_subscription_plan(request):
    subscription_id = request.data.get('subscription_id')
    new_status = request.data.get('status')
    plan_name = request.data.get('plan_name')

    try:
        subscription = Subscription.objects.get(id=subscription_id)
        subscription.status = new_status
        subscription.plan_name = plan_name
        subscription.save()
        return Response({'message': 'Subscription status updated successfully.'}, status=status.HTTP_200_OK)
    except Subscription.DoesNotExist:
        return Response({'error': 'Subscription not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)