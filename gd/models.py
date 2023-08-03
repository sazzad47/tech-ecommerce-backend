from django.db import models
from django.conf import settings
from django.utils import timezone
from users.models import User
from djmoney.models.fields import MoneyField
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money


class Post(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    tips = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Tip', related_name='post_tips')
    raised = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Donation', related_name='post_donations')
    comments = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Comment', related_name='post_comments')
    total_donations = MoneyField(
        decimal_places=2,
        max_digits=20,
        default=0,
        default_currency='USD',
        null= True
    )
    total_company_tips = MoneyField(
        decimal_places=2,
        max_digits=20,
        default=0,
        default_currency='USD',
        null= True
    )
    total_volunteer_tips = MoneyField(
        decimal_places=2,
        max_digits=20,
        default=0,
        default_currency='USD',
        null= True
    )
    application_for = models.CharField(max_length=255, null=True, blank=True)
    mode = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    fathers_name = models.CharField(max_length=255, null=True, blank=True)
    mothers_name = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    province = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    zip = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    marital_status = models.CharField(max_length=255, null=True, blank=True)
    specific_marital_status = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=255, null=True, blank=True)
    specific_sex = models.CharField(max_length=255, null=True, blank=True)
    blood_group = models.CharField(max_length=255, null=True, blank=True)
    occupation = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    identification_card = models.CharField(max_length=10000, null=True, blank=True)
    certificate_from_city_council = models.CharField(max_length=10000, null=True, blank=True)
    medical_report = models.CharField(max_length=10000, null=True, blank=True)
    permission_letter = models.CharField(max_length=10000, null=True, blank=True)
    test_results = models.CharField(max_length=10000, null=True, blank=True)
    name_of_employment = models.CharField(max_length=255, null=True, blank=True)
    credential_photos =  models.JSONField(blank=True, null=True)
    other_documents = models.CharField(max_length=10000, null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    photo = models.CharField(max_length=10000, null=True, blank=True)
    live_description = models.CharField(max_length=10000, null=True, blank=True)
    written_description = models.TextField()
    time_limit = models.CharField(max_length=255, null=True, blank=True)
    fixed_time = models.DateTimeField(null=True, blank=True)
    donation_needed = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='pending')
    suggested_donations = models.JSONField(blank=True, null=True)
    suggested_company_tips = models.JSONField(blank=True, null=True)
    suggested_volunteer_tips = models.JSONField(blank=True, null=True)

class Tip(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    company_tips = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='USD',
        max_digits=11,
    )
    volunteer_tips = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='USD',
        max_digits=11,
    )
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Convert the amount to USD
        company_tips_usd = convert_money(self.company_tips, 'USD')
        volunteer_tips_usd = convert_money(self.volunteer_tips, 'USD')
        print(company_tips_usd.amount)
        self.company_tips = company_tips_usd
        self.volunteer_tips = volunteer_tips_usd

        super().save(*args, **kwargs)

        # Update total_tips for the post
        post = self.post
        previous_total_company_tips = post.total_company_tips.amount if post.total_company_tips else 0
        previous_total_volunteer_tips = post.total_volunteer_tips.amount if post.total_volunteer_tips else 0
        post.total_company_tips = Money(previous_total_company_tips + company_tips_usd.amount, 'USD')
        post.total_volunteer_tips = Money(previous_total_volunteer_tips + volunteer_tips_usd.amount, 'USD')
        post.save()

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def avatar(self):
        return self.user.avatar

class Donation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    amount = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='USD',
        max_digits=11,
    )
    is_hidden = models.BooleanField(default=False)
    created_at = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Convert the amount to USD
        amount_usd = convert_money(self.amount, 'USD')
        print(amount_usd.amount)
        self.amount = amount_usd

        super().save(*args, **kwargs)

        # Update total_donations for the post
        post = self.post
        previous_total_donations = post.total_donations.amount if post.total_donations else 0
        post.total_donations = Money(previous_total_donations + amount_usd.amount, 'USD')
        post.save()

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def avatar(self):
        return self.user.avatar
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)
   

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def avatar(self):
        return self.user.avatar
    
class DonationsWithdrawalRequest(models.Model):
    # Choices for the status field
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    account_number = models.CharField(max_length=100, null=True)
    bank_name = models.CharField(max_length=100, blank=True, default="")
    routing_number = models.CharField(max_length=100, blank=True, default="")
    other_information = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    def __str__(self):
        return f"Withdrawal Request #{self.pk}: {self.amount} {self.status}"
    
class TipsWithdrawalRequest(models.Model):
    # Choices for the status field
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    account_number = models.CharField(max_length=100, null=True)
    bank_name = models.CharField(max_length=100, blank=True, default="")
    routing_number = models.CharField(max_length=100, blank=True, default="")
    other_information = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )

    def __str__(self):
        return f"Withdrawal Request #{self.pk}: {self.amount} {self.status}"
    
