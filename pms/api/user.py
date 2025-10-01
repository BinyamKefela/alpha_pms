from django.contrib.auth.models import Permission,Group
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,DjangoModelPermissions
from rest_framework.filters import OrderingFilter,SearchFilter
from ..serializers import UserSerializer,OwnerManagerSerializer,OwnerStaffSerializer
from pms.api.custom_pagination import CustomPagination
from rest_framework.decorators import api_view,permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.exceptions import ValidationError, NotFound
from django.db.models import F, Value
from django.db.models.functions import Concat
import json
from ..models import *
from datetime import datetime
from rest_framework.permissions import AllowAny


User = get_user_model()
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
#SITE_URL = settings.SITE_URL

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,DjangoModelPermissions]
    filter_backends = [OrderingFilter,SearchFilter]
    search_fields = [field.name for field in User._meta.fields]
    ordering_fields = [field.name for field in User._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination


class UserRetrieveView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

class UserDestroyView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    lookup_field = 'id'

    def handle_exception(self, exc):
        if isinstance(exc,NotFound):
            return Response({"error":"There is no user with the given id!"},status=status.HTTP_400_BAD_REQUEST)

        return super().handle_exception(exc)

    def destroy(self, request, *args, **kwargs):
        user_to_deactivate = self.get_object()
        if not user_to_deactivate:
            return Response({"error":"There is no user with the given id!"},status=status.HTTP_404_NOT_FOUND)
        user_to_deactivate.is_active = False
        user_to_deactivate.save()
        return Response({"message":"user deactivated successfully"},status=status.HTTP_200_OK)

class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def activate_user(request,id):
    try:
        user = User.objects.get(pk=id)
    except:
        return Response({"error":"there is no user with the given id"},status=status.HTTP_404_NOT_FOUND)
    user.is_active = True
    user.save()
    return Response({"message":"user is activated successfully!"},status=status.HTTP_200_OK)

#-------------------------------------an API for assigning permissions to users, we can either remove or add permissions to users-----------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setUserPermissions(request):
    if not request.user.has_perm('pms.change_user'):
        return Response({"message":"you don't have the permission to set user's permissions"},status=status.HTTP_403_FORBIDDEN)
    user_id = request.data.get("user_id")
    permission_code_names = request.data.get("permissions") 
    if not user_id or not permission_code_names:
        return Response({"message":"please provide user_id and permissions"},status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"message":"user does not exist"},status=status.HTTP_404_NOT_FOUND)
    permissions = Permission.objects.filter(codename__in=permission_code_names)
    user.user_permissions.clear()
    user.user_permissions.set(permissions)
    return Response({"message":"permissions assigned to user succssfully!"},status=status.HTTP_200_OK)


#-------------------------------------an API for assigning groups to users, we can either remove or add groups to users-----------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def setUserGroups(request):
    if (not request.user.has_perm('pms.change_user')) and (not request.user.has_perm('pms.change_customuser')):
        return Response({"message":"you don't have the permission to set user's groups"},status=status.HTTP_403_FORBIDDEN)
    user_id = request.data.get("user_id")
    group_names = request.data.get("groups") 
    if not user_id or not group_names:
        return Response({"message":"please provide user_id and permissions"},status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(id=user_id)
    except Group.DoesNotExist:
        return Response({"message":"User does not exist"},status=status.HTTP_404_NOT_FOUND)
    groups = Group.objects.filter(name__in=group_names)
    if not groups:
        return Response({"message":"group not found!"},status=status.HTTP_404_NOT_FOUND)
    user.groups.clear()
    user.groups.set(groups)
    return Response({"message":"groups assigned to user succssfully!"},status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def send_password_reset_email(request):
    email = request.data.get("email")
    if not email:
        return Response({"error":"please provide email!"},status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error":"there is no user with the provided email"},status=status.HTTP_404_NOT_FOUND)
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    current_site = get_current_site(request)
    dummy_site = "http://localhost:3000/en/reset-password?" + f'{token}'
    reset_link = f"https://{current_site.domain}/reset-password/{token}"
    
    # Correct HTML message body with proper structure
    html_message = f'''
    <html>
      <body>
        <p>Hello,</p>
        <p>Click this link {dummy_site} to reset your password.</p>
        <p>Best regards,<br>Phoenixopia PMS</p>
      </body>
    </html>
    '''
    
    # Send email with both plain text and HTML content
    send_mail(
        subject="Password reset request",
        message=f"Click the link below to reset your password:\n\n{dummy_site}",  # Plain text version
        html_message=html_message,  # HTML version
        from_email="ketsebaotertumo@gmail.com",
        recipient_list=[email],
        fail_silently=False
    )


    return Response({"message":"password reset email was sent successfully"},status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request,token):
    acces_token = AccessToken(token)
    try:
        user = User.objects.get(id=acces_token["user_id"])
    except User.DoesNotExist:
        return Response({"error":"Invalid or expired token"},status=status.HTTP_400_BAD_REQUEST)
    new_password = request.data.get("password")
    user.set_password(new_password)
    user.save()

    return Response({"message":"password reset successfully!"},status=status.HTTP_200_OK)
 

@api_view(["POST"])
@permission_classes([AllowAny])
def get_user_profile(request):
    access_token = AccessToken((request.data.get("access_token")))
    try:
        user = User.objects.get(id=access_token['user_id'])
    except User.DoesNotExist:
        return Response({"error": "Invalid or expired token"},status=status.HTTP_400_BAD_REQUEST)
    return Response({"user_id":user.pk,"first_name":user.first_name,"middle_name":user.middle_name,
                     "last_name":user.last_name,"email":user.email,"user_permissions":user.get_all_permissions(),
                     "groups":user.groups.values_list('name',flat=True),"profile_picture":user.profile_picture.url},status=status.HTTP_200_OK)



@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_user(request,id):
    if not request.user.has_perm("change_user"):
        return Response({"message":"Unauthorized accesss!"},status=status.HTTP_401_UNAUTHORIZED)
    try:
        user = User.objects.get(id=id)
    except:
        return Response({"error":"user with the given id does not exist!"},status=status.HTTP_400_BAD_REQUEST)
    user_permissions = request.data.get("user_permissions",[])
    user_groups = request.data.get("groups",[])
    first_name = request.data.get("first_name")
    middle_name = request.data.get("middle_name")
    last_name = request.data.get("last_name")
    address = request.data.get("address")
    phone_number = request.data.get("phone_number")
    #is_active = request.data.get("is_get")
    is_superuser = request.data.get("is_superuser")
    profile_picture = request.FILES.get("profile_picture")

    if user_permissions:
        permissions = Permission.objects.filter(codename__in=user_permissions)
        user.user_permissions.clear()
        user.user_permissions.set( permissions)
    if user_groups:
        groups = Group.objects.filter(name__in=user_groups)
        user.groups.clear()
        user.groups.set(groups)
    if first_name:
        user.first_name = first_name
    if middle_name:
        user.middle_name = middle_name
    if last_name:
        user.last_name = last_name
    if address:
        user.address = address
    if phone_number:
        user.phone_number = phone_number
    if is_superuser:
        user.is_superuser = is_superuser
    if profile_picture:
        user.profile_picture = profile_picture

    user.save()

    return Response({"message":"successfully updated user!"},status=status.HTTP_200_OK)





class GetTenats(generics.ListAPIView):
    queryset = User.objects.filter(groups__name="tenant")
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated,DjangoModelPermissions]
    filter_backends = [OrderingFilter,SearchFilter]
    search_fields = [field.name for field in User._meta.fields]
    ordering_fields = [field.name for field in User._meta.fields]
    ordering = ['id']
    pagination_class = CustomPagination




@api_view()
@permission_classes([IsAuthenticated])
def get_owners(request):
    owners = User.objects.filter(groups__name="owner")
        
    # Concatenate first_name and middle_name (if middle_name exists) into one field
    owners_data = owners.annotate(full_name=Concat(F('first_name'), Value(' '), F('middle_name'),Value(' '),F('last_name'))).values("id", "full_name")
    
    # Return the response with the data
    return Response({"owners": owners_data}, status=status.HTTP_200_OK)
       
@api_view()
@permission_classes([IsAuthenticated])
def get_managers(request):
    managers = User.objects.filter(groups__name="manager")
        
    # Concatenate first_name and middle_name (if middle_name exists) into one field
    managers_data = managers.annotate(full_name=Concat(F('first_name'), Value(' '), F('middle_name'),Value(' '),F('last_name'))).values("id", "full_name")
    
    # Return the response with the data
    return Response({"managers": managers_data}, status=status.HTTP_200_OK)

@api_view()
@permission_classes([IsAuthenticated])
def get_tenants(request):
    tenants = User.objects.filter(groups__name="tenant")
        
    # Concatenate first_name and middle_name (if middle_name exists) into one field
    tenants_data = tenants.annotate(full_name=Concat(F('first_name'), Value(' '), F('middle_name'),Value(' '),F('last_name'))).values("id", "full_name")
    
    # Return the response with the data
    return Response({"tenants": tenants_data}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up(request):
        if User.objects.filter(email=request.data.get("email")).count()>0:
            return Response({"error":"This email already exists in the system"},status=status.HTTP_403_FORBIDDEN)
        serializer = UserSerializer(data=request.data)
    #if serializer.is_valid():
        #if the user already signed up but didn't verify his account, delete verfication UUID's
        if User.objects.filter(email=request.data.get("email"),is_active=False).count() > 0:
            EmailVerification.objects.filter(user=User.objects.filter(email=request.data.get("email"),is_active=False).first()).delete()
            verification = EmailVerification.objects.create(user=User.objects.filter(email=request.data.get("email"),is_active=False).first())
        
        #if the user hasn't signed up, create him first
        else:
            if User.objects.filter(email=request.data.get("email")).count() > 0:
                return Response({"error":"This email already exists in the system"},status=status.HTTP_403_FORBIDDEN)
            user = User()
            user.email = request.data.get("email")
            user.is_active=False
            
            
            if request.data.get("phone_number"):
               user.phone_number = request.data.get("phone_number")
            if request.data.get("first_name"):
               user.first_name = request.data.get("first_name")
            if request.data.get("middle_name"):
               user.middle_name = request.data.get("middle_name")
            if request.data.get("last_name"):
               user.last_name = request.data.get("last_name")
            user.set_password(request.data.get("password"))
            user.save()
            user.groups.set(Group.objects.filter(name="owner"))
            try:
               
               '''owner = Owner()
               owner.company_name = request.data.get("company_name")
               owner.status = "active"
               owner.company_owner = user
               owner.plan = Plan.objects.get(id=request.data.get("plan"))
               owner.company_address = request.data.get("company_address")
               owner.company_email = user.email
               owner.created_at = datetime.datetime.now()
               owner.save()'''
               if not request.data.get("is_manager") and not request.data.get("is_staff"):
                    subscription = Subscription()
                    subscription.plan_name = Plan.objects.get(id=request.data.get("plan")).name
                    subscription.start_date = request.data.get("start_date")
                    subscription.status = "pending"
                    subscription.created_at = datetime.now()
                    subscription.user_id = user
                    subscription.price = Plan.objects.get(id=request.data.get("plan")).price
                    subscription.start_date = request.data.get("start_date")
                    subscription.end_date = request.data.get("end_date")
                    subscription.save()

                    notifiction = Notification()
                    notifiction.user = user
                    notifiction.notification_type = "subscription created"
                    #notifiction.payment = instance
                    notifiction.message = "a new subscription made by user "+str(user.email)
                    notifiction.is_read = False
                    notifiction.created_at = datetime.now()
                    notifiction.save()
            except Exception as e:
                return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
            user.save()

            if request.data.get("is_manager"):
                try:
                  
                  user.groups.set(Group.objects.filter(name="manager"))
                  owner_manger = OwnerManager()
                  owner_manger.owner = request.user
                  owner_manger.manager = user
                  owner_manger.save()
                except User.DoesNotExist:
                    return Response({"error":"owner with the given id does not exist"},status=status.HTTP_404_NOT_FOUND)
                
            if request.data.get("is_staff"):
                try:
                   user.groups.set(Group.objects.filter(name="staff"))
                   owner_staff = OwnerStaff()
                   owner_staff.owner = request.user
                   owner_staff.staff = user
                   owner_staff.save()
                except User.DoesNotExist:
                    return Response({"error":"owner with the given id does not exist"},status=status.HTTP_404_NOT_FOUND)
            
            #if serializer.is_valid():
            #    user = serializer.save(is_active=False)  # Initially set user as inactive
            verification = EmailVerification.objects.create(user=user)
        from urllib.parse import urljoin
        current_site = request.build_absolute_uri('/')
        mail_subject = 'Verify your email address'
        relative_link = "api/verify-email/"+str(verification.token)#reverse('verify_email', kwargs={'token': str(verification.token)})
        absolute_url = urljoin(current_site,relative_link) #f'{current_site}{relative_link}'  # Adjust protocol if needed
        message = f'Hi ,\n\nPlease click on the link below to verify your email address and complete your signup:\n\n{absolute_url}'
        send_mail(mail_subject, message, EMAIL_HOST_USER, [request.data.get("email")])
        return Response({'message': 'Registration successful. Please check your email to verify your account.',"user":UserSerializer(user).data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@permission_classes(['add_user'])
def create_manager(request):
    if not request.user.has_perm('add_user'):
        return Response({"message":"you don't have the permission to create a user"},status=status.HTTP_403_FORBIDDEN)
    if not request.user.groups.filter(name="owner").exists():
        return Response({"message":"you must be an owner to create a new manager"},status=status.HTTP_403_FORBIDDEN)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.groups.set(Group.objects.filter(name="manager"))
        owner_manager_serializer = OwnerManagerSerializer(data={
            "owner": request.user.id,
            "manager": user.id,
            "property_zone": request.data.get("property_zone")
        })
        if owner_manager_serializer.is_valid():
            owner_manager_serializer.save()
        else:
            return Response(owner_manager_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"manager created successfully!"},status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_manager(request, id):
    if not request.user.has_perm('delete_user'):
        return Response({"message":"you don't have the permission to delete a user"},status=status.HTTP_403_FORBIDDEN)
    try:
        manager = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({"message":"manager does not exist"},status=status.HTTP_404_NOT_FOUND)
    
    if not manager.groups.filter(name="manager").exists():
        return Response({"message":"the user is not a manager"},status=status.HTTP_400_BAD_REQUEST)

    manager.delete()
    OwnerManager.objects.filter(manager=manager).delete()
    return Response({"message":"manager deleted successfully!"},status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_manager(request, id):
    if not request.user.has_perm('change_user'):
        return Response({"message":"you don't have the permission to update a user"},status=status.HTTP_403_FORBIDDEN)
    try:
        manager = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({"message":"manager does not exist"},status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(manager, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"manager updated successfully!"},status=status.HTTP_200_OK)
    
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_managers(request):
    if not request.user.has_perm('view_user'):
        return Response({"message":"you don't have the permission to view users"}, status=status.HTTP_403_FORBIDDEN)
    
    managers = User.objects.filter(groups__name="manager")
    paginator = CustomPagination()
    paginated_managers = paginator.paginate_queryset(managers, request)
    serializer = UserSerializer(paginated_managers, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_manager(request, id):
    if not request.user.has_perm('view_user'):
        return Response({"message":"you don't have the permission to view users"},status=status.HTTP_403_FORBIDDEN)
    
    try:
        manager = User.objects.get(id=id, groups__name="manager")
    except User.DoesNotExist:
        return Response({"message":"manager does not exist"},status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializer(manager)
    return Response(serializer.data, status=status.HTTP_200_OK)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_staff(request):
    if not request.user.has_perm('pms.add_user'):
        return Response({"message":"you don't have the permission to create a user"},status=status.HTTP_403_FORBIDDEN)
    if not request.user.groups.filter(name="owner").exists():
        return Response({"message":"you must be an owner to create a new staff"},status=status.HTTP_403_FORBIDDEN)
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.groups.set(Group.objects.filter(name="staff"))
        owner_staff_serializer = OwnerStaffSerializer(data={
            "owner": request.user.id,
            "staff": user.id,
            "property_zone": request.data.get("property_zone")
        })
        if owner_staff_serializer.is_valid():
            owner_staff_serializer.save()
        else:
            return Response(owner_staff_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"staff created successfully!"},status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_staff(request, id):
    if not request.user.has_perm('pms.delete_user'):
        return Response({"message":"you don't have the permission to delete a user"},status=status.HTTP_403_FORBIDDEN)
    try:
        staff = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({"message":"staff does not exist"},status=status.HTTP_404_NOT_FOUND)
    
    if not staff.groups.filter(name="staff").exists():
        return Response({"message":"the user is not a manager"},status=status.HTTP_400_BAD_REQUEST)

    staff.delete()
    OwnerStaff.objects.filter(staff=staff).delete()
    return Response({"message":"staff deleted successfully!"},status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_staff(request, id):
    if not request.user.has_perm('pms.change_user'):
        return Response({"message":"you don't have the permission to update a user"},status=status.HTTP_403_FORBIDDEN)
    try:
        staff = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({"message":"staff does not exist"},status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(staff, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message":"staff updated successfully!"},status=status.HTTP_200_OK)
    
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_staffs(request):
    if not request.user.has_perm('pms.view_user'):
        return Response({"message":"you don't have the permission to view users"}, status=status.HTTP_403_FORBIDDEN)
    
    managers = User.objects.filter(groups__name="staff")
    paginator = CustomPagination()
    paginated_managers = paginator.paginate_queryset(managers, request)
    serializer = UserSerializer(paginated_managers, many=True)
    return paginator.get_paginated_response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_staff(request, id):
    if not request.user.has_perm('view_user'):
        return Response({"message":"you don't have the permission to view users"},status=status.HTTP_403_FORBIDDEN)
    
    try:
        staff = User.objects.get(id=id, groups__name="staff")
    except User.DoesNotExist:
        return Response({"message":"staff does not exist"},status=status.HTTP_404_NOT_FOUND)
    
    serializer = UserSerializer(staff)
    return Response(serializer.data, status=status.HTTP_200_OK)




    