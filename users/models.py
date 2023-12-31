from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils import timezone
from django.db.models import JSONField
from djmoney.models.fields import MoneyField
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money

# Custom User Manager
class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password=None):
        """
        Creates and saves a User with the given email, first_name, last_name, and password.
        """
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None):
        """
        Creates and saves a superuser with the given email, first_name, last_name, and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user

# Custom User Model
class User(AbstractBaseUser):
    created_at = models.DateTimeField(default=timezone.now)
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    otp = models.IntegerField(null=True,blank=True)
    activation_key = models.CharField(max_length=150,blank=True,null=True)
    first_name = models.CharField(max_length=200, default='Default First Name', blank=True, null=True)
    last_name = models.CharField(max_length=200, default='Default Last Name', blank=True, null=True)
    intro = models.CharField(max_length=200, blank=True, null=True)
    billing_address = models.OneToOneField('BillingAddress', on_delete=models.SET_NULL, null=True, related_name='user_billing', blank=True)
    volunteer_information = models.OneToOneField('Volunteer', on_delete=models.SET_NULL, null=True, related_name='user_volunteer', blank=True)
    place_of_birth = models.CharField(max_length=100, blank=True)
    current_location = models.CharField(max_length=100, blank=True)
    education = JSONField(blank=True, null=True)
    profession = JSONField(blank=True, null=True)
    expertise = models.CharField(max_length=100, blank=True)
    biography = models.TextField(blank=True, null=True)
    social_links = JSONField(blank=True, null=True)
    avatar = models.CharField(max_length=10000, blank=True, null=True)
    funds = MoneyField(
        decimal_places=2,
        max_digits=20,
        default=0,
        default_currency='USD',
        null= True
    )
    pending_withdrawal_donations = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        null=True
    )
    pending_withdrawal_tips = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=0,
        null=True
    )
    tips = MoneyField(
        decimal_places=2,
        max_digits=20,
        default=0,
        default_currency='USD',
        null= True
    )
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_volunteer = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

class BillingAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    def __str__(self):
        return f"Billing Address for {self.user.email}"
    
class Volunteer(models.Model):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    fathers_name = models.CharField(max_length=255, null=True, blank=True)
    mothers_name = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    marital_status = models.CharField(max_length=50, null=True, blank=True)
    specific_marital_status = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.CharField(max_length=100, null=True, blank=True)
    sex = models.CharField(max_length=10, null=True, blank=True)
    specific_sex = models.CharField(max_length=100, null=True, blank=True)
    blood_group = models.CharField(max_length=10, null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    identification_card = models.CharField(max_length=10000, null=True, blank=True)
    photo = models.CharField(max_length=10000, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"