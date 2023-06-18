from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import OrderSerializer
from .forms import OrderForm
from .models import Order, Transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe


class OrderListCreateUpdateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        form = OrderForm(request.data, user=request.user)  # Use request.data instead of request.POST
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            form.save_m2m()
            serializer = OrderSerializer(order)  # Serialize the created order
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderUpdateView(generics.UpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Exclude read-only fields if the user is not staff
        if not request.user.is_staff:
            serializer.validated_data.pop('total_price', None)
            serializer.validated_data.pop('advance_price', None)
            serializer.validated_data.pop('advance_percentage', None)
            serializer.validated_data.pop('status', None)
            serializer.validated_data.pop('design_file', None)

        self.perform_update(serializer)
        return Response(serializer.data)
    

@csrf_exempt
def create_payment_intent(request):
    # Retrieve order details and calculate payment amount
    order_id = request.POST.get('order_id')
    order = Order.objects.get(pk=order_id)
    payment_amount = order.total_price

    # Create a Payment Intent
    intent = stripe.PaymentIntent.create(
        amount=int(payment_amount * 100),  # Stripe requires amount in cents
        currency='usd',
    )

    # Create a Transaction
    transaction = Transaction.objects.create(
        user=request.user,
        order=order,
        amount=payment_amount,
        payment_intent_id=intent.id,
    )

    # Return the Payment Intent client secret and Transaction ID to the frontend
    return JsonResponse({
        'clientSecret': intent.client_secret,
        'transactionId': transaction.id,
    })

@csrf_exempt
def confirm_payment(request):
    # Retrieve Payment Intent ID from the request
    payment_intent_id = request.POST.get('payment_intent_id')

    # Retrieve the Transaction associated with the Payment Intent
    transaction = Transaction.objects.get(payment_intent_id=payment_intent_id)

    # Confirm the Payment Intent using the Stripe library
    intent = stripe.PaymentIntent.confirm(payment_intent_id)

    # Handle the payment success or failure
    if intent.status == 'succeeded':
        # Update order status to 'completed' or handle as needed
        transaction.order.status = 'completed'
        transaction.order.save()
        success_message = 'Payment succeeded. Order completed.'
        return JsonResponse({'success': True, 'message': success_message})
    else:
        # Handle payment failure or update order status accordingly
        transaction.order.status = 'cancelled'
        transaction.order.save()
        failure_message = 'Payment failed. Order cancelled.'
        return JsonResponse({'success': False, 'message': failure_message})
