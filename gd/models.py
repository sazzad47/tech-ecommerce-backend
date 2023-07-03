from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from users.models import User
from djmoney.models.fields import MoneyField
from djmoney.contrib.exchange.models import convert_money
from djmoney.money import Money
from decimal import Decimal


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
    total_tips = MoneyField(
        decimal_places=2,
        max_digits=20,
        default=0,
        default_currency='USD',
        null= True
    )
    fixed_tip = MoneyField(
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
    identification_card = models.FileField(null=True, blank=True, upload_to='post_documents/')
    certificate_from_city_council = models.FileField(null=True, blank=True, upload_to='post_documents/')
    medical_report = models.FileField(null=True, blank=True, upload_to='post_documents/')
    permission_letter = models.FileField(null=True, blank=True, upload_to='post_documents/')
    test_results = models.FileField(null=True, blank=True, upload_to='post_documents/')
    name_of_employment = models.CharField(max_length=255, null=True, blank=True)
    photo = models.FileField(null=True, blank=True, upload_to='post_documents/')
    other_documents = models.FileField(null=True, blank=True, upload_to='post_documents/')
    title = models.CharField(max_length=255, null=True, blank=True)
    live_description = models.FileField(null=True, blank=True, upload_to='post_documents/')
    written_description = models.TextField()
    time_limit = models.CharField(max_length=255, null=True, blank=True)
    fixed_time = models.DateTimeField(null=True, blank=True)
    donation_needed = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='pending')
    suggested_donations = models.JSONField(blank=True, null=True)
    suggested_tips = models.JSONField(blank=True, null=True)

class Tip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    amount = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='USD',
        max_digits=11,
    )
    is_hidden = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Convert the amount to USD
        amount_usd = convert_money(Money(self.amount.amount, self.amount.currency), 'USD')
        print(amount_usd.amount)
        # Update total_tips for the post
        post = self.post
        previous_total_tips = post.total_tips or 0  # Get the previous total_tips or default to 0
        post.total_tips = previous_total_tips.amount + amount_usd.amount
        post.save()
      

class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    amount = MoneyField(
        decimal_places=2,
        default=0,
        default_currency='USD',
        max_digits=11,
    )
    is_hidden = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Convert the amount to USD
        amount_usd = convert_money(Money(self.amount.amount, self.amount.currency), 'USD')
        print(amount_usd.amount)
        # Update total_donations for the post
        post = self.post
        previous_total_donations = post.total_donations or 0  # Get the previous total_donations or default to 0
        post.total_donations = previous_total_donations.amount + amount_usd.amount
        post.save()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.user.first_name} on post {self.post.application_for}"

