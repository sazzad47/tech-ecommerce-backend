from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    advance_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    advance_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', blank=True)
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
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_intent_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Transaction #{self.pk} - User: {self.user.email}"

