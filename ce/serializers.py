from rest_framework import serializers
from .models import Order
from .models import Transaction

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ('date', 'total_price', 'advance_percentage', 'advance_price', 'total_paid', 'status', 'design_file')
        read_only_fields = ('user',)

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    
class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'title', 'date', 'status']

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        exclude = ('user', )

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

        

