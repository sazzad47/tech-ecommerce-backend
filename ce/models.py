from django.db import models
from django.conf import settings
from django.utils.html import format_html

class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Processing', 'Processing'),
        ('Submitted', 'Submitted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ce_orders')
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=20, null=True)
    country = models.CharField(max_length=100, null=True)
    province = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    zip = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=255, null=True)
    category = models.CharField(max_length=100, null=True)
    order_file = models.CharField(max_length=10000, null=True, blank=True)
    order_description = models.TextField(null=True)
    delivery_date = models.DateField(null=True)
    demo = models.JSONField(blank=True, null=True)
    additional_file = models.CharField(max_length=10000, null=True, blank=True)
    title = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    advance_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    advance_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', blank=True)
    design_file = models.CharField(max_length=10000, null=True, blank=True)

    def __str__(self):
        return f"Order #{self.pk} - User: {self.user.email}"

    def save(self, *args, **kwargs):
        # Calculate advance price based on total price and advance percentage
        if self.total_price and self.advance_percentage:
            self.advance_price = self.total_price * self.advance_percentage / 100

        super().save(*args, **kwargs)


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ce_transactions')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Transaction #{self.pk} - User: {self.user.email}"

class Security(models.Model):
    title = models.CharField(max_length=1000)
    short_description = models.TextField()
    keywords = models.TextField()
    content = models.TextField()

    def __str__(self):
        return self.title
    
class Design(models.Model):
    photo = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title
    
class Template(models.Model):
    cover_photo = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=100)
    price = models.CharField(max_length=100)
    short_description = models.TextField()
    photos = models.JSONField(blank=True, null=True)
    features = models.JSONField(blank=True, null=True)
    video = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
    
class Company(models.Model):
    photo = models.CharField(max_length=10000, null=True, blank=True)
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()

    def __str__(self):
        return self.name
    
class GlobalLocation(models.Model):
    country = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.country
    
class SocialLink(models.Model):
    icon = models.URLField(null=True, blank=True)
    link = models.URLField()

    def __str__(self):
        return self.link
    
class PaymentOption(models.Model):
    icon = models.URLField(null=True, blank=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Service(models.Model):
    box_title = models.CharField(max_length=100)
    box_photo = models.CharField(max_length=10000, null=True, blank=True)
    box_description = models.TextField()
    title = models.CharField(max_length=200)
    short_description = models.TextField()
    keywords = models.TextField()
    content = models.TextField()

    def __str__(self):
        return self.title
    
class FooterPage(models.Model):
    category = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    short_description = models.TextField()
    keywords = models.TextField()
    content = models.TextField()

    def __str__(self):
        return self.title

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    photo = models.URLField(null=True, blank=True)
    pdf = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name