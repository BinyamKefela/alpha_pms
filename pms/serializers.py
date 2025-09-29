from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User,Group,Permission,ContentType
from django.contrib.auth import get_user_model,authenticate
from rest_framework import serializers
from .models import *

User = get_user_model()

#this is a class used to customize the JWT token obtaining since we need to send the permission list to the user
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    username_field = "email"
    
    def validate(self, attrs):
        credentials={
            "email":attrs.get("email"),
            "password":attrs.get("password")
        }
    
        data = super().validate(attrs)
        user = authenticate(email=attrs['email'],password=attrs['password'])
        if user and not user.is_active:
            raise serializers.ValidationError({"error":"user is banned from the system"})
           
    

        user = authenticate(**credentials)
        
        if user is None:
            raise serializers.ValidationError({"error":"invalid credentials"})
        
        #lets add permissions to the token payload
        #permissions = user.get_all_permissions()
        data = super().validate(attrs)
        data['permissions'] = list(user.get_all_permissions())
        data['groups'] = list(user.groups.values_list('name',flat=True))
        data['email'] = user.email
        data['id'] = user.id
        data['is_superuser'] = user.is_superuser
        return data
    
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    user_permissions = serializers.SlugRelatedField(slug_field="codename",queryset=Permission.objects.all(),many=True,required=False)
    groups = serializers.SlugRelatedField(slug_field="name",queryset=Group.objects.all(),many=True,required=False)
    class Meta:
        model = User
        fields = "__all__"

    def validate(self, data):
        if self.instance is None and "password" not in data:
            raise serializers.ValidationError({"password":"This field is required when creating a new user!"})
        return data

    def create(self, validated_data):
        password = validated_data.pop("password",None)
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop("password",None)
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        """Ensure superusers receive all permissions."""
        representation = super().to_representation(instance)

        if instance.is_superuser:
            # Get all permission codenames for superusers
            all_permissions = Permission.objects.values_list("codename", flat=True)
            representation["user_permissions"] = list(all_permissions)
        else:
            # Regular users: only show explicitly assigned permissions
            representation["user_permissions"] = list(instance.user_permissions.values_list("codename", flat=True))

        return representation
    
class GroupSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(slug_field="codename",queryset=Permission.objects.all(),many=True,required=False)

    class Meta:
        model = Group
        fields = "__all__"


class PermissionSerializer(serializers.ModelSerializer):
    content_type = serializers.PrimaryKeyRelatedField(write_only=True,queryset=ContentType.objects.all())
    class Meta:
        model = Permission
        fields = "__all__"
    





class PropertyPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyPicture
        fields = "__all__"


class PropertySerializer(serializers.ModelSerializer):
    property_pictures = PropertyPictureSerializer(many=True,read_only=True)
    class Meta:
        model = Property
        fields = "__all__"

class RentSerializer(serializers.ModelSerializer):
    property_id = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all(),many=False,required=False)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),many=False,required=False)
    class Meta:
        model = Rent
        fields = "__all__"

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['property_id'] = PropertySerializer( instance.property_id).data
        representation['user_id'] = UserSerializer(instance.user_id).data
        return representation

class RentPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentPicture
        fields = "__all__"

class MaintenanceRequestSerializerGet(serializers.ModelSerializer):
    user_id = UserSerializer()
    property_id = PropertySerializer()
    class Meta:
        model = MaintenanceRequest
        fields = "__all__"

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    status = serializers.CharField(required=False)
    class Meta:
        model = MaintenanceRequest
        fields = "__all__"

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = "__all__"

class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPayment
        fields = "__all__"

class PropertyZoneSaleSerializer(serializers.ModelSerializer):
    #property_id = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all(),many=False,required=False)
    #user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(),many=False,required=False)
    class Meta:
        model = PropertyZoneSale
        fields = "__all__"
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        #representation['buyer'] = UserSerializer(instance.buyer).data
        #representation['seller'] = UserSerializer(instance.seller).data
        representation['property_id'] = PropertySerializer(instance.property_id).data
        representation['property_zone_id'] = PropertyZoneSerializer(instance.property_zone_id).data
        return representation

from rest_framework import serializers

class PropertyZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyZone
        fields = '__all__'


from rest_framework import serializers

class SalesPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesPayment
        fields = '__all__'

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'

class OwnerManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerManager
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['owner'] = UserSerializer(instance.owner).data
        representation['manager'] = UserSerializer(instance.manager).data
        representation['property_zone'] = PropertyZoneSerializer(instance.property_zone).data
        return representation
    

class OwnerManagerSerializerGet(serializers.ModelSerializer):
    

    class Meta:
        model = OwnerManager
        fields = '__all__'
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['owner'] = UserSerializer(instance.owner).data
        representation['manager'] = UserSerializer(instance.manager).data
        representation['property_zone'] = PropertyZoneSerializer(instance.property_zone).data
        return representation
    

class OwnerStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = OwnerManager
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['owner'] = UserSerializer(instance.owner).data
        representation['staff'] = UserSerializer(instance.staff).data
        representation['property_zone'] = PropertyZoneSerializer(instance.property_zone).data
        return representation


class OwnerStaffSerializerGet(serializers.ModelSerializer):
    

    class Meta:
        model = OwnerStaff
        fields = '__all__'
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['owner'] = UserSerializer(instance.owner).data
        representation['staff'] = UserSerializer(instance.staff).data
        representation['property_zone'] = PropertyZoneSerializer(instance.property_zone).data
        return representation


class RentCycleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentCycle
        fields = "__all__"

    def to_representation(self, instance):
        representation =  super().to_representation(instance)
        representation['payment'] = PaymentSerializer(instance.payment).data
        representation['rent'] =RentSerializer(instance.rent).data
        return representation


class BrokerProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrokerProfile
        fields = "__all__"


class CommissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Commission
        fields = "__all__"

class PropertyZonePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyZonePicture
        fields = "__all__"


from rest_framework import serializers
from .models import CoworkingSpace, WorkSpaceRental, RentalPayment


class CoworkingSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoworkingSpace
        fields = "__all__"


class WorkSpaceRentalSerializer(serializers.ModelSerializer):
    #space_name = serializers.ReadOnlyField(source="space.name")
    #renter = serializers.SerializerMethodField()

    class Meta:
        model = WorkSpaceRental
        fields = "__all__"
        read_only_fields = ("next_due_date",)

    def get_renter(self, obj):
        if obj.user:
            return obj.user.email
        return obj.guest_name or "Guest"
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.user:
            representation['user'] = UserSerializer(instance.user).data
        representation['space'] = CoworkingSpaceSerializer(instance.space).data
        return representation


class RentalPaymentSerializer(serializers.ModelSerializer):
    rental_info = serializers.ReadOnlyField(source="rental.space.name")

    class Meta:
        model = RentalPayment
        fields = "__all__"
        read_only_fields = ("paid_at",)

class RentCommissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = RentCommission
        fields = "__all__"

class SAASTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SAASTransaction
        fields = "__all__"

class BrokerTransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = BrokerTransaction
        fields = "__all__"


