from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ('user',)  # Exclude the 'user' field from the serializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user
        if not user.is_staff:
            self.fields['total_price'].read_only = True
            self.fields['advance_price'].read_only = True
            self.fields['advance_percentage'].read_only = True
            self.fields['status'].read_only = True
            self.fields['design_file'].read_only = True
