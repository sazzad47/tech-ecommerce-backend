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
    order_file = models.FileField(upload_to='orders/', null=True)
    order_description = models.TextField(null=True)
    delivery_date = models.DateField(null=True)
    demo = models.JSONField(blank=True, null=True)
    additional_file = models.FileField(upload_to='orders/', blank=True, null=True)
    title = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    advance_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    advance_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', blank=True)
    design_file = models.FileField(upload_to='designs/', blank=True, null=True)

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

