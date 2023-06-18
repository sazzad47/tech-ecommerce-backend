from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models
from django.utils import timezone
from django.db.models import JSONField

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
    place_of_birth = models.CharField(max_length=100, blank=True)
    current_location = models.CharField(max_length=100, blank=True)
    education = JSONField(blank=True, null=True)
    profession = JSONField(blank=True, null=True)
    expertise = models.CharField(max_length=100, blank=True)
    biography = models.TextField(blank=True, null=True)
    social_links = JSONField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
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