from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,TokenVerifyView)

from pms.api.property_zone import *
from pms.api.sales_payment import *
from .api.property import *
from .api.user import *
from .api.group import *
from .api.permission import *
from .api.property_picture import *
from .api.rent import *
from .api.rent_picture import *
from .api.payment import *
from .api.maintenance_request import *
from .api.report import * 
from .api.notification import *
from .api.subscription import *
from .api.subscription_payment import *
from .api.telebirr_integration.apis import *
from .api.arifpay_integration.api import *
from .api.property_zone_sale import *
from .api.plan import *
from .api.owner_manager import *
from .api.owner_staff import *
from .api.rent_cycle import *
from .api.broker_profile import *
from .api.commission import *
from .api.property_zone_picture import *
from .api.coworkingspace import *
from .api.workspace_rental import *
from .api.rental_payment import *



urlpatterns = [
  #--------------------------------users routes-----------------------------------------------
  path("get_users", UserListView.as_view(), name="get_users"),
  path("get_user/<int:id>",UserRetrieveView.as_view(),name='get_user'),
  path("post_user",UserCreateView.as_view(),name="post_user"),
  path("old_update_user/<int:id>",UserUpdateView.as_view(),name="update_user"),
  path("deactivate_user/<int:id>",UserDestroyView.as_view(),name="delete_user"),
  path("set_user_permissions",setUserPermissions,name="set_user_permissions"),
  path("set_user_groups", setUserGroups, name="set_user_group"),
  path("send_password_reset_email",send_password_reset_email,name="send_password_reset_email"),
  path("reset_password/<str:token>",reset_password,name="reset_passord"),
  path("get_user_profile",get_user_profile,name="get_user_id"),
  path("update_user/<int:id>",update_user,name="new_update_user"),
  path("activate_user/<int:id>", activate_user, name="activate_user"),
  path("get_owners",get_owners,name="get_owners"),
  path("get_managers",get_managers,name="get_managers"),
  path("get_tenants",GetTenats.as_view(),name="get_tenants"),
  path('sign_up',sign_up, name='sign_up'),

  path('get_managers', get_managers, name='get_managers'),
  path('create_manager', create_manager, name='create_manager'),
  path('delete_manager/<int:id>', delete_manager, name='delete_manager'),
  path('update_manager/<int:id>', update_manager, name='update_manager'),


  path('get_staffs', get_staffs, name='get_staffs'),
  path('create_staff', create_staff, name='create_staff'),
  path('delete_staff/<int:id>', delete_staff, name='delete_staff'),
  path('update_staff/<int:id>', update_staff, name='update_staff'),




    #--------------------------------Groups routes----------------------------------------------
  path("get_groups", GroupListView.as_view(), name="get_groups"),
  path("get_group/<int:id>",GroupRetrieveView.as_view(),name='get_group'),
  path("post_group",GroupCreateView.as_view(),name="post_group"),
  path("update_group/<int:id>",GroupUpdateView.as_view(),name="update_group"),
  path("delete_group/<int:id>",GroupDestroyView.as_view(),name="delete_group"),
  path("set_group_permissions",setGroupPermissions,name="set_group_permissions"),
  path("get_group_permissions",getGroupPermission,name="get_group_permissions"),



    #--------------------------------Permission routes--------------------------------------------
  path("get_permissions", PermissionListView.as_view(), name="get_permissions"),
  path("get_permission/<int:id>",PermissionRetrieveView.as_view(),name='get_permission'),
  path("post_permission",PermissionCreateView.as_view(),name="post_permission"),
  path("update_permission/<int:id>",PermissionUpdateView.as_view(),name="update_permission"),
  path("delete_permission/<int:id>",PermissionDestroyView.as_view(),name="delete_permission"),


  #---------------------------------Property routes--------------------------------------------------

  path("get_properties", PropertyListView.as_view(), name="get_properties"),
  path("get_property/<int:id>",PropertyRetrieveView.as_view(),name='get_property'),
  path("post_property",PropertyCreateView.as_view(),name="post_property"),
  path("update_property/<int:id>",PropertyUpdateView.as_view(),name="update_property"),
  path("delete_property/<int:id>",PropertyDestroyView.as_view(),name="delete_property"),


  #---------------------------------Property Picture routes--------------------------------------------

  path("get_property_pictures", PropertyPictureListView.as_view(), name="get_property_pictures"),
  path("get_property_picture/<int:id>",PropertyPictureRetrieveView.as_view(),name='get_property_picture'),
  path("post_property_picture",PropertyPictureCreateView.as_view(),name="post_property_picture"),
  path("update_property_picture/<int:id>",PropertyPictureUpdateView.as_view(),name="update_property_picture"),
  path("delete_property_picture/<int:id>",PropertyPictureDestroyView.as_view(),name="delete_property_picture"),


    #---------------------------------Rent routes------------------------------------------------------

  path("get_rents", RentListView.as_view(), name="get_rents"),
  path("get_rent/<int:id>",RentRetrieveView.as_view(),name='get_rent'),
  path("post_rent",RentCreateView.as_view(),name="post_rent"),
  path("update_rent/<int:id>",RentUpdateView.as_view(),name="update_rent"),
  path("delete_rent/<int:id>",RentDestroyView.as_view(),name="delete_rent"),

  path("get_staff_rents", get_staff_rents, name="get_staff_rents"),


  #---------------------------------Rent Picture routes-------------------------------------------------

  path("get_rent_pictures", RentPictureListView.as_view(), name="get_rent_pictures"),
  path("get_rent_picture/<int:id>",RentPictureRetrieveView.as_view(),name='get_rent_picture'),
  path("post_rent_picture",RentPictureCreateView.as_view(),name="post_rent_picture"),
  path("update_rent_picture/<int:id>",RentPictureUpdateView.as_view(),name="update_rent_picture"),
  path("delete_rent_picture/<int:id>",RentPictureDestroyView.as_view(),name="delete_rent_picture"),

  #---------------------------------Rent cycle routes------------------------------------------------

  path("get_rent_cycles", RentCycleListView.as_view(), name="get_rent_cycles"),
  path("get_rent_cycles/<int:rent_id>",RentCycleFromRentListView.as_view(),name="get_rent_cycles_from_rent"),





 #---------------------------------payment routes--------------------------------------------------

  path("get_payments", PaymentListView.as_view(), name="get_payments"),
  path("get_payment/<int:id>",PaymentRetrieveView.as_view(),name='get_payment'),
  path("post_payment",PaymentCreateView.as_view(),name="post_payment"),
  path("update_payment/<int:id>",PaymentUpdateView.as_view(),name="update_payment"),
  path("delete_payment/<int:id>",PaymentDestroyView.as_view(),name="delete_payment"),
  path("make_payment", make_payment, name="make_payment"),
  path("approve_payment", approve_payment, name="approve_payments"),
  path("get_user_payments/<int:id>",PaymentUserListView.as_view(),name="get_user_payment"),


   #---------------------------------maintenance request routes--------------------------------------------------

  path("get_maintenance_requests", MaintenanceRequestListView.as_view(), name="get_maintenace_requests"),
  path("get_maintenance_request/<int:id>",MaintenanceRequestRetrieveView.as_view(),name='get_maintenance_request'),
  path("post_maintenance_request",MaintenanceRequestCreateView.as_view(),name="post_maintenance_request"),
  path("update_maintenance_request/<int:id>",MaintenanceRequestUpdateView.as_view(),name="update_maintenance_request"),
  path("delete_maintenance_request/<int:id>",MaintenanceRequestDestroyView.as_view(),name="delete_maintenance_request"),
  path("resolve_maintenance_request",resolve_maintenance_request,name="resolve_maintenance_request"),


   #---------------------------------report routes--------------------------------------------------

  path("get_reports", ReportListView.as_view(), name="get_reports"),
  path("get_report/<int:id>",ReportRetrieveView.as_view(),name='get_report'),
  path("post_report",ReportCreateView.as_view(),name="post_report"),
  path("update_report/<int:id>",ReportUpdateView.as_view(),name="update_report"),
  path("delete_report/<int:id>",ReportDestroyView.as_view(),name="delete_report"),



 #---------------------------------notification routes--------------------------------------------------

  path("get_notifications", NotificationListView.as_view(), name="get_notifications"),
  path("get_notification/<int:id>",NotificationRetrieveView.as_view(),name='get_notification'),
  path("post_notification",NotificationCreateView.as_view(),name="post_notification"),
  path("update_notification/<int:id>",NotificationUpdateView.as_view(),name="update_notification"),
  path("delete_notification/<int:id>",NotificationDestroyView.as_view(),name="delete_notification"),
  path("get_unread_notifications",UnreadNotificationListView.as_view(),name="get_unread_notifications"),



   #---------------------------------subscription routes--------------------------------------------------

  path("get_subscription", SubscriptionListView.as_view(), name="get_subscription"),
  path("get_subscription/<int:id>",SubscriptionRetrieveView.as_view(),name='get_subscription'),
  path("post_subscription",SubscriptionCreateView.as_view(),name="post_subscription"),
  path("update_subscription/<int:id>",SubscriptionUpdateView.as_view(),name="update_subscription"),
  path("delete_subscription/<int:id>",SubscriptionDestroyView.as_view(),name="delete_subscription"),
  path("update_subscription_plan",update_subscription_plan,name="update_subscription_plan"),



   #---------------------------------SubscriptionPayment routes--------------------------------------------------

  path("get_subscription_payment", SubscriptionPaymentListView.as_view(), name="get_subscription_payment"),
  path("get_subscription_payment/<int:id>",SubscriptionPaymentRetrieveView.as_view(),name='get_subscription_payment'),
  path("post_subscription_ayment",SubscriptionPaymentCreateView.as_view(),name="post_subscription_payment"),
  path("update_subscription_payment/<int:id>",SubscriptionPaymentUpdateView.as_view(),name="update_subscription_payment"),
  path("delete_subscription_payment/<int:id>",SubscriptionPaymentDestroyView.as_view(),name="delete_subscription_payment"),




  #-----------------------------------------------telebirr integration-----------------------------------------
  path("post_fabric_token",ApplyFabricTokenView.as_view(),name="post_fabric_token"),


  #----------------------------------------------Arifpay integration--------------------------------------------
  path("arif_pay_check_out",check_out,name="arif_pay_check_out"),
  path("pay_rent",pay_rent,name="pay_rent"),
  path("payment_complete",payment_complete,name="payment_complete"),



  #----------------------------------------------property zone sales-----------------------------------------
  path("get_property_zone_sales", PropertyZoneSaleListView.as_view(), name="get_property_zone_sale"),
  path("get_property_zone_sale/<int:id>",PropertyZoneSaleRetrieveView.as_view(),name='get_property_zone_sale'),
  path("post_property_zone_sale",PropertyZoneSaleCreateView.as_view(),name="post_property_zone_sale"),
  path("update_property_zone_sale/<int:id>",PropertyZoneSaleUpdateView.as_view(),name="update_property_zone_sale"),
  path("delete_property_zone_sale/<int:id>",PropertyZoneSaleDestroyView.as_view(),name="delete_property_zone_sale"),


  #----------------------------------------------property zone-----------------------------------------
   path('get_property_zones', PropertyZoneListView.as_view()),
   path('post_property_zone', PropertyZoneCreateView.as_view()),
   path('get_property_zone/<int:id>', PropertyZoneRetrieveView.as_view()),
   path('update_property_zone/<int:id>', PropertyZoneUpdateView.as_view()),
   path('delete_property_zone/<int:id>', PropertyZoneDestroyView.as_view()),


  #----------------------------------------------sales payment-----------------------------------------

   path('get_sales_payments', SalesPaymentListView.as_view()),
   path('post_sales_payment', SalesPaymentCreateView.as_view()),
   path('get_sales_payment/<int:id>', SalesPaymentRetrieveView.as_view()),
   path('update_sales_payments/<int:id>', SalesPaymentUpdateView.as_view()),
   path('delete_sales_payment/<int:id>', SalesPaymentDestroyView.as_view()),


     #---------------------------------Plan routes-------------------------------------------------------

  path('get_plans',PlanListView.as_view(),name='get_plans'),
  path('get_plan/<int:id>',PlanRetrieveView.as_view(),name='get_plan'),
  path('post_plan',PlanCreateView.as_view(),name='post_plan'),
  path('update_plan/<int:id>',PlanUpdateView.as_view(),name='update_plan'),
  path('delete_plan/<int:id>',PlanDestroyView.as_view(),name='delete_plan'),


  #---------------------------------OwnerManager routes-------------------------------------------------------
  path('get_owner_managers', OwnerManagerListView.as_view(), name='get_owner_managers'),
  path('get_owner_manager/<int:id>', OwnerManagerRetrieveView.as_view(), name='get_owner_manager'),
  path('post_owner_manager', OwnerManagerCreateView.as_view(), name='post_owner_manager'),
  path('update_owner_manager/<int:id>', OwnerManagerUpdateView.as_view(), name='update_owner_manager'),
  path('delete_owner_manager/<int:id>', OwnerManagerDestroyView.as_view(), name='delete_owner_manager'),
  path('get_owner_manager_details/<int:id>', OwnerManagerRetrieveView.as_view(), name='get_owner_manager_details'),



  #---------------------------------OwnerStaff routes-------------------------------------------------------
  path('get_owner_staffs', OwnerStaffListView.as_view(), name='get_owner_staffs'),
  path('get_owner_staff/<int:id>', OwnerStaffRetrieveView.as_view(), name='get_owner_staff'),
  path('post_owner_staff', OwnerStaffCreateView.as_view(), name='post_owner_staff'),
  path('update_owner_staff/<int:id>', OwnerStaffUpdateView.as_view(), name='update_owner_staff'),
  path('delete_owner_staff/<int:id>', OwnerStaffDestroyView.as_view(), name='delete_owner_staff'),
  path('get_owner_staff_details/<int:id>', OwnerStaffRetrieveView.as_view(), name='get_owner_staff_details'),


  #--------------------------------BrokerProfile routes-------------------------------------------------------

  path('get_broker_profiles',BrokerProfileListView.as_view(),name='get_broker_profiles'),
  path('get_broker_profile/<int:id>',BrokerProfileRetrieveView.as_view(),name='get_broker_profile'),
  path('post_broker_profile',BrokerProfileCreateView.as_view(),name='post_broker_profile'),
  path('update_broker_profile/<int:id>',BrokerProfileUpdateView.as_view(),name='update_broker_profile'),
  path('delete_broker_profile/<int:id>',BrokerProfileDestroyView.as_view(),name='delete_broker_profile'),


 #--------------------------------commission routes-------------------------------------------------------

  path('get_commissions',CommissionListView.as_view(),name='get_commissions'),
  path('get_commission/<int:id>',CommissionRetrieveView.as_view(),name='get_commission'),
  path('post_commission',CommissionCreateView.as_view(),name='post_commission'),
  path('update_commission/<int:id>',CommissionUpdateView.as_view(),name='update_commission'),
  path('delete_commission/<int:id>',CommissionDestroyView.as_view(),name='delete_commission'),

  #---------------------------------Property Zone Picture routes--------------------------------------------
  path("get_property_zone_pictures", PropertyZonePictureListView.as_view(), name="get_property_zone_pictures"),
  path("get_property_zone_picture/<int:id>",PropertyZonePictureRetrieveView.as_view(),name='get_property_zone_picture'),
  path("post_property_zone_picture",PropertyZonePictureCreateView.as_view(),name="post_property_zone_picture"),
  path("update_property_zone_picture/<int:id>",PropertyZonePictureUpdateView.as_view(),name="update_property_zone_picture"),
  path("delete_property_zone_picture/<int:id>",PropertyZonePictureDestroyView.as_view(),name="delete_property_zone_picture"),


  #---------------------------------Coworking Space routes------------------------------------------------------
  path("get_coworking_spaces", CoworkingSpaceListView.as_view(), name="get_coworking_spaces"),
  path("get_coworking_space/<int:id>",CoworkingSpaceRetrieveView.as_view(),name='get_coworking_space'),
  path("post_coworking_space",CoworkingSpaceCreateView.as_view(),name="post_coworking_space"),
  path("update_coworking_space/<int:id>",CoworkingSpaceUpdateView.as_view(),name="update_coworking_space"),
  path("delete_coworking_space/<int:id>",CoworkingSpaceDestroyView.as_view(),name="delete_coworking_space"),

  #---------------------------------Workspace Rental routes------------------------------------------------------
  path("get_workspace_rentals", WorkSpaceRentalListView.as_view(), name="get_workspace_rentals"),
  path("get_workspace_rental/<int:id>",WorkSpaceRentalRetrieveView.as_view(),name='get_workspace_rental'),
  path("post_workspace_rental",WorkSpaceRentalCreateView.as_view(),name="post_workspace_rental"),
  path("update_workspace_rental/<int:id>",WorkSpaceRentalUpdateView.as_view(),name="update_workspace_rental"),
  path("delete_workspace_rental/<int:id>",WorkSpaceRentalDestroyView.as_view(),name="delete_workspace_rental"),

  #---------------------------------Rental Payment routes-------------------------------------------------------
  path('get_rental_payments',RentalPaymentListView.as_view(),name='get_rental_payments'),
  path('get_rental_payment/<int:id>',RentalPaymentRetrieveView.as_view(),name='get_rental_payment'),
  path('post_rental_payment',RentalPaymentCreateView.as_view(),name='post_rental_payment'),
  path('update_rental_payment/<int:id>',RentalPaymentUpdateView.as_view(),name='update_rental_payment'),
  path('delete_rental_payment/<int:id>',RentalPaymentDestroyView.as_view(),name='delete_rental_payment'),
]