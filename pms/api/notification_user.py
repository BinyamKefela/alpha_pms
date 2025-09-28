from rest_framework.generics import ListAPIView,CreateAPIView,UpdateAPIView,DestroyAPIView
from ..models import NotificationUser
from rest_framework.permissions import IsAuthenticated,DjangoModelPermissions
from ..serializers import NotificationUserSerializer
from pms.api.custom_pagination import CustomPagination
from rest_framework.filters import OrderingFilter,SearchFilter


class NotificationUserListView(ListAPIView):
    queryset = NotificationUser.objects.all()
    serializer_class = NotificationUserSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated,DjangoModelPermissions]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [field.name for field in NotificationUser._meta.fields]
    ordering_fields = [field.name for field in NotificationUser._meta.fields]
    ordering = ['id']

    def get_queryset(self):
        id = self.kwargs.get('user_id')
        queryset = super().get_queryset()
        if id is not None:
            try:
               # Filter the queryset based on the primary key
               queryset = queryset.filter(user_id=id)  # Assuming your model has an 'id' field
               return queryset
            except:
                raise NotFound(detail="There is no notificaation with the given ID.")
        else:
            # If no 'pk' is provided, return the default queryset (all objects)
            return queryset 

class NotificationUserCreateView(CreateAPIView):
    queryset = NotificationUser.objects.all()
    serializer_class = NotificationUserSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
