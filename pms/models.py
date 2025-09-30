from django.db import models
from django.contrib.auth.models import  AbstractUser,AbstractBaseUser,BaseUserManager,PermissionsMixin,Group
from django.conf import settings
from django.contrib.auth import get_user_model
from django.conf import settings
# Create your models here.



from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone
import os
from django.core.exceptions import ValidationError

from auditlog.registry import auditlog
from datetime import timedelta
import uuid



def validate_uploaded_image_extension(value):
    valid_extensions = ['.png','.jpg','.jpeg','.PNG','.JPG','.JPEG']
    ext = os.path.splitext(value.name)[1]
    if not ext in valid_extensions:
        raise ValidationError('Unsupported filed extension')
        

def get_upload_path(instance,filename):
    ext = filename.split('.')[-1]
    new_file_name = "profiles/"+f'{instance.id}.{ext}'
    return new_file_name


# Custom manager for user model
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    


class CustomUser(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30,null=True)
    middle_name = models.CharField(max_length=30,null=True)
    last_name = models.CharField(max_length=30,null=True)
    phone_number = models.CharField(max_length=100,null=True)
    address = models.CharField(max_length=100,null=True)
    profile_picture = models.FileField(upload_to=get_upload_path,validators=[validate_uploaded_image_extension],null=True,blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Make groups and user_permissions optional by adding blank=True and null=True
    groups = models.ManyToManyField(
        'auth.Group', 
        blank=True,
        null=True, 
        related_name='customuser_set', 
        related_query_name='customuser', 
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        blank=True,
        null=True, 
        related_name='customuser_set', 
        related_query_name='customuser', 
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # fields to be used when creating a superuser
    
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        db_table = "user"
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def delete(self, *args, **kwargs):
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        return super().delete(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        if self.profile_picture:
            if os.path.isfile(self.profile_picture.path):
                os.remove(self.profile_picture.path)
        return super().save(*args, **kwargs)

User = settings.AUTH_USER_MODEL


auditlog.register(CustomUser)

class OwnerManager(models.Model):
    owner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="owner_manager")
    manager = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="manager_manager")
    property_zone = models.ForeignKey("PropertyZone",on_delete=models.SET_NULL,null=True,related_name="property_zone_manager")


class OwnerStaff(models.Model):
    owner = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="owner_staff")
    staff = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="staff_owner")
    property_zone = models.ForeignKey("PropertyZone",on_delete=models.SET_NULL,null=True,related_name="property_zone_staff")


class PropertyZone(models.Model):
    owner_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="property_owner_id")
    manager_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="property_manager_id")
    name = models.CharField(max_length=100,null=False,unique=True)
    address = models.CharField(max_length=100,null=False)
    city = models.CharField(max_length=100,null=False)
    state = models.CharField(max_length=100,null=False)
    created_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        db_table = "property_zone"

def get_property_zone_upload_path(instance,filename):
    ext = filename.split('.')[-1]
    new_file_name = "property_zone/"+f'{filename}'
    return new_file_name


class PropertyZonePicture(models.Model):
    property_zone_id = models.ForeignKey(PropertyZone,on_delete=models.SET_NULL,null=True,related_name="property_pictures")
    description = models.CharField(max_length=200,null=True)
    property_image = models.FileField(upload_to=get_property_zone_upload_path,validators=[validate_uploaded_image_extension],null=True,blank=True)

    class Meta:
        db_table = "property_zone_picture"
        
    def delete(self, *args, **kwargs):
        if self.property_image:
            if os.path.isfile(self.property_image.path):
                os.remove(self.property_image.path)
        return super().delete(*args, **kwargs)


class Property(models.Model):
    property_zone_id= models.ForeignKey(PropertyZone,on_delete=models.SET_NULL,null=True,related_name="property_zone_id")
    owner_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="owner_id")
    manager_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="manager_id")
    property_type = models.CharField(max_length=100,null=True)
    name = models.CharField(max_length=100,null=False,blank=False)
    address = models.CharField(max_length=100,null=False)
    city = models.CharField(max_length=100,null=False)
    state = models.CharField(max_length=100,null=False)
    zip_code = models.CharField(max_length=100,null=False)
    price = models.FloatField(null=False)
    bed_rooms = models.IntegerField(null=True,blank=True)
    bath_rooms = models.IntegerField(null=True,blank=True)
    rent = models.IntegerField(null=True)
    status = models.CharField(max_length=100,null=False)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "property"
        unique_together = ['name','property_zone_id']


auditlog.register(Property)     
        


def get_property_upload_path(instance,filename):
    ext = filename.split('.')[-1]
    new_file_name = "property/"+f'{filename}'
    return new_file_name

def get_upload_path(instance,filename):
    ext = filename.split('.')[-1]
    new_file_name = "profiles/"+f'{instance.id}.{ext}'
    return new_file_name


class PropertyPicture(models.Model):
    property_id = models.ForeignKey(Property,on_delete=models.SET_NULL,null=True,related_name="property_pictures")
    description = models.CharField(max_length=200,null=True)
    property_image = models.FileField(upload_to=get_property_upload_path,validators=[validate_uploaded_image_extension],null=True,blank=True)

    class Meta:
        db_table = "property_picture"
        
    def delete(self, *args, **kwargs):
        if self.property_image:
            if os.path.isfile(self.property_image.path):
                os.remove(self.property_image.path)
        return super().delete(*args, **kwargs)
    

auditlog.register(PropertyPicture)

class Rent(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    property_id = models.ForeignKey(Property,on_delete=models.SET_NULL,null=True,related_name="rents")
    rent_type = models.CharField(max_length=100)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=True)
    payment_cycle = models.CharField(max_length=100)
    rent_amount = models.FloatField(null=False)
    deposit_amount = models.FloatField(null=False)
    broker = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="rent_broker")
    status = models.CharField(max_length=100,null=False)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "rent"

auditlog.register(Rent)

def get_rent_upload_path(instance,filename):
    ext = filename.split('.')[-1]
    new_file_name = "rent/"+filename
    return new_file_name

class RentPicture(models.Model):
    rent_id = models.ForeignKey(Rent,on_delete=models.SET_NULL,null=True)
    description = models.CharField(max_length=200,null=True)
    rent_image = models.FileField(models.FileField(upload_to=get_rent_upload_path,validators=[validate_uploaded_image_extension],null=True,blank=True))

    class Meta:
        db_table = "rent_picture"

    def delete(self, *args, **kwargs):
        if self.rent_image:
            if os.path.isfile(self.rent_image.path):
                os.remove(self.rent_image.path)
        return super().delete(*args, **kwargs)


auditlog.register(RentPicture)

class Payment(models.Model):
    rent_id = models.ForeignKey(Rent,on_delete=models.SET_NULL,null=True)
    user_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    amount = models.FloatField(null=True)
    due_date = models.DateTimeField(null=True)
    status = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "payment"

auditlog.register(Payment)


class MaintenanceRequest(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    property_id = models.ForeignKey(Property,on_delete=models.SET_NULL,null=True)
    description = models.CharField(max_length=200,null=True)
    status = models.CharField(max_length=100)
    requested_at = models.DateTimeField(null=True)
    resolved_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "maintenance_request"

auditlog.register(MaintenanceRequest)


class Report(models.Model):
    property_id = models.ForeignKey(Property,on_delete=models.SET_NULL,null=True)
    report_type = models.CharField(max_length=100)
    generated_by = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    report_data = models.CharField(max_length=900)
    created_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "report"

auditlog.register(Report)

class Notification(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    notification_type = models.CharField(max_length=100,choices=(("maintenance_request_created","maintenance request created"),
                                                                 ("maintenance_request_resolved","maintenance request resolved"),
                                                                 ("rent_over_due","rent over due"),
                                                                 ("payment_complete","payment complete")))
    maintenance_request_id = models.ForeignKey(MaintenanceRequest,on_delete=models.SET_NULL,null=True)
    payment_id = models.ForeignKey(Payment,on_delete=models.SET_NULL,null=True)
    rent_id = models.ForeignKey(Rent,on_delete=models.SET_NULL,null=True)
    message = models.CharField(max_length=200,null=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=False)
    read_at = models.DateTimeField(null=True)



class Subscription(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    plan_name = models.CharField(max_length=100,null=False)
    billing_cycle = models.CharField(max_length=100,null=False)
    price = models.FloatField(null=False)
    start_date = models.DateTimeField(null=False)
    end_date = models.DateTimeField(null=False)
    status = models.CharField(max_length=100,null=False)
    created_at = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)



class SubscriptionPayment(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    subscription_id = models.ForeignKey(Subscription,on_delete=models.SET_NULL,null=True)
    payment_method = models.CharField(max_length=100,null=False)
    amount = models.FloatField(null=False)
    status = models.CharField(max_length=100,null=False)
    paid_at = models.DateTimeField(null=True,blank=True)
    transaction_id = models.CharField(max_length=100,null=False)
    created_at = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = ["transaction_id"]



class RentCycle(models.Model):
    rent = models.ForeignKey("Rent", on_delete=models.CASCADE, related_name="cycles")
    cycle_start = models.DateField()
    cycle_end = models.DateField()
    is_paid = models.BooleanField(default=False)
    amount_due = models.FloatField()
    payment = models.ForeignKey("Payment", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.rent} - {self.cycle_start} to {self.cycle_end}"



class NotificationUser(models.Model):
    user_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    notification_id = models.ForeignKey(Notification,on_delete=models.SET_NULL,null=True)



class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification for {self.user.email}"



class EmailResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)
       


class Plan(models.Model):
    name = models.CharField(max_length=100,null=False,blank=False,unique=True)
    max_locations = models.IntegerField(null=False)
    max_staff = models.IntegerField(null=True)
    max_users = models.IntegerField(null=False)
    max_kds = models.IntegerField(null=False)
    kds_enabled = models.BooleanField(default=False)
    price = models.IntegerField(null=False)
    billing_cycle = models.CharField(max_length=100,choices=(('daily','daily'),('weekly','weekly'),
                                                             ('monthly','monthly'),('quarterly','quarterly'),
                                                             ('yearly','yearly')))
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)



class PropertyZoneSale(models.Model):
    PROPERTY_SALE_STATUS_CHOICES = [("pending","pending"),
                                    ("complete","complete"),
                                    ("cancelled","cancelled")]
    #seller = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="property_sale_seller")
    #buyer = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="property_sale_buyer")
    property_zone_id = models.ForeignKey(PropertyZone,on_delete=models.SET_NULL,null=True)
    property_id = models.ForeignKey(Property,on_delete=models.SET_NULL,null=True,blank=True)
    broker = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="property_sale_broker")
    listing_price = models.IntegerField(null= False)
    selling_price = models.IntegerField(null=True,blank=True)
    status = models.CharField(max_length=100,choices=PROPERTY_SALE_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class SalesPayment(models.Model):
    SALES_PAYMENT_CHOICES= [('pending','pending'),('complete','complete'),('cancelled','cancelled')]
    property_zone_sale_id = models.ForeignKey(PropertyZoneSale,on_delete=models.SET_NULL,null=True,blank=True)
    buyer_id = models.ForeignKey(User,on_delete=models.SET_NULL,null=True)
    amount = models.FloatField(null=True)
    due_date = models.DateTimeField(null=True,blank=True)
    status = models.CharField(max_length=100,choices=SALES_PAYMENT_CHOICES)
    payment_method = models.CharField(max_length=100,null=True,blank=True)
    transaction_id = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "sale_payment"


class Commission(models.Model):
    property_sale = models.ForeignKey(SalesPayment,on_delete=models.CASCADE)
    saas_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    broker_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class RentCommission(models.Model):
    rent = models.ForeignKey(Rent,on_delete=models.SET_NULL,null=True,blank=True)
    saas_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    broker_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BrokerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="broker_profile")
    license_number = models.CharField(max_length=100)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.02)
    wallet = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta
from dateutil.relativedelta import relativedelta  # pip install python-dateutil

User = get_user_model()


class CoworkingSpace(models.Model):
    zone = models.ForeignKey(PropertyZone, on_delete=models.CASCADE, related_name="coworking_spaces")
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    capacity = models.IntegerField()

    price_daily = models.DecimalField(max_digits=10, decimal_places=2)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    price_quarterly = models.DecimalField(max_digits=10, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.location}"
    class Meta:
        unique_together = ('name','zone')


class WorkSpaceRental(models.Model):
    CYCLE_CHOICES = [
        ("daily", "Daily"),
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("yearly", "Yearly"),
    ]

    # either link to a registered user OR store guest info
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="workspace_rentals")
    guest_name = models.CharField(max_length=255, blank=True, null=True)
    guest_email = models.EmailField(blank=True, null=True)
    guest_phone = models.CharField(max_length=20, blank=True, null=True)

    space = models.ForeignKey(CoworkingSpace, on_delete=models.CASCADE, related_name="rentals")
    cycle = models.CharField(max_length=20, choices=CYCLE_CHOICES)

    start_date = models.DateField()
    next_due_date = models.DateField(blank=True, null=True)  # not full end date
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Set the next due date (not the full end date)."""
        if self.start_date and self.cycle:
            if not self.next_due_date:
                if self.cycle == "daily":
                    self.next_due_date = self.start_date + timedelta(days=1)
                elif self.cycle == "monthly":
                    self.next_due_date = self.start_date + relativedelta(months=1)
                elif self.cycle == "quarterly":
                    self.next_due_date = self.start_date + relativedelta(months=3)
                elif self.cycle == "yearly":
                    self.next_due_date = self.start_date + relativedelta(years=1)
        super().save(*args, **kwargs)

    def __str__(self):
        renter = self.user.email if self.user else self.guest_name or "Guest"
        return f"{renter} - {self.space.name} ({self.cycle})"


class RentalPayment(models.Model):
    RENTAL_SPACE_STATUS_CHOICES = [("pending","pending"),
                                    ("complete","complete"),
                                    ("cancelled","cancelled")]
    rental = models.ForeignKey(WorkSpaceRental, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=100,choices=RENTAL_SPACE_STATUS_CHOICES)
    payment_method = models.CharField(max_length=100)
    transaction_id = models.CharField(max_length=100,null=True,blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    cycle_start = models.DateField()
    cycle_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for {self.rental} ({self.amount})"


class SAASTransaction(models.Model):
    SAAS_TRANSACTION_TYPE_CHOICE = [('sales commission','sales commission'),
                                    ('rent commission','rent commission')]
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=200,choices=SAAS_TRANSACTION_TYPE_CHOICE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BrokerTransaction(models.Model):
     BROKER_TRANSACTION_TYPE_CHOICE = [('sales commission','sales commission'),
                                    ('rent commission','rent commission')]
     amount = models.DecimalField(max_digits=12, decimal_places=2)
     transaction_type = models.CharField(max_length=200,choices=BROKER_TRANSACTION_TYPE_CHOICE)
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)


   
