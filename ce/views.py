from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializers import OrderSerializer, ProductSerializer, TemplateSerializer, DesignSerializer, FooterPageSerializer, PaymentOptionSerializer, SocialLinkSerializer, GlobalLocationSerializer, CompanySerializer, SecuritySerializer, OrderListSerializer, OrderItemSerializer, TransactionSerializer, ServiceSerializer
from .models import Order, Design, Template, Transaction, Security, Company, Service, Product, GlobalLocation, SocialLink, PaymentOption, FooterPage
from django.views.decorators.csrf import csrf_exempt
import stripe
from utils import Util
from django.conf import settings
from rest_framework.views import APIView
from django.http import HttpResponse
from utils import Util
from rest_framework import viewsets
from rest_framework.decorators import api_view
from app.settings import BASE_CLIENT_URL
from rest_framework import status

class DesignViewSet(viewsets.ModelViewSet):
    queryset = Design.objects.all()
    serializer_class = DesignSerializer

class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer

class SecurityViewSet(viewsets.ModelViewSet):
    queryset = Security.objects.all()
    serializer_class = SecuritySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class FooterPageViewSet(viewsets.ModelViewSet):
    queryset = FooterPage.objects.all()
    serializer_class = FooterPageSerializer

class GlobalLocationViewSet(viewsets.ModelViewSet):
    queryset = GlobalLocation.objects.all()
    serializer_class = GlobalLocationSerializer
    
class SocialLinkViewSet(viewsets.ModelViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer

class PaymentOptionViewSet(viewsets.ModelViewSet):
    queryset = PaymentOption.objects.all()
    serializer_class = PaymentOptionSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class GetOrdersByStatusView(generics.ListAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        status = self.kwargs.get('status')
        if status is not None and status.lower() != 'any':
            return Order.objects.filter(status__iexact=status)
        else:
            return Order.objects.all()

class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        self.send_order_received_email(order)
    
    def send_order_received_email(self, order):
        subject = "Order Received"
        body = f"Dear {order.user.first_name},\n\nThank you for placing an order with us. Your order with ID #{order.pk} ({order.title}) has been received by our team. We will review your order and provide you with further details soon.\n\nWe appreciate your patience, and if you have any questions, feel free to reach out to us. Thank you for choosing our services!\n\nBest regards,\nSazzad Hossen"
        html_body = f"<p>Dear {order.user.first_name},</p><p>Thank you for placing an order with us. Your order with ID #{order.pk} ({order.title}) has been received by our team. We will review your order and provide you with further details soon.</p><p>We appreciate your patience, and if you have any questions, feel free to reach out to us. Thank you for choosing our services!</p><p>Best regards,<br>Sazzad Hossen</p>"
        to_email = order.user.email
       

        data = {
            'subject': subject,
            'body': body,
            'html_body': html_body,
            'to_email': to_email,
        }

        Util.send_email(data)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)

class OrderDetailView(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class OrderUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

class PaymentIntentCreateView(APIView):
    def post(self, request, *args, **kwargs):
        prod_id=self.kwargs["pk"]
        try:
            product=Order.objects.get(id=prod_id)
            if product.total_paid <= 0:
                amount = int(product.advance_price) * 100
            else:
                amount = int((product.total_price - product.total_paid) * 100)
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price_data': {
                            'currency':'usd',
                             'unit_amount':amount,
                             'product_data':{
                                 'name':product.title,

                             }
                        },
                        'quantity': 1,
                    },
                ],
                metadata={
                    "product_id":product.id
                },
                mode='payment',
                success_url=BASE_CLIENT_URL +'/ce/orders/payment?success=true',
                cancel_url=BASE_CLIENT_URL + '/ce/profile/orders/' + product.id,
            )
            return Response({'checkout_url': checkout_session.url})
        except Exception as e:
            return Response({'msg':'something went wrong while creating stripe session','error':str(e)}, status=500)



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET_CE
        )
    except ValueError as e:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        print(session)
        prod_id=session['metadata']['product_id']
        product=Order.objects.get(id=prod_id)

        amount_total =session['amount_total'] / 100     
        product.total_paid += int(amount_total)
        product.save()

        if product.total_paid >= product.total_price:
            product.status = 'Completed'
            product.save()
        elif product.total_paid < product.total_price:
            product.status = 'Processing'
            product.save()

        Transaction.objects.create(
            user=product.user,
            order=product,
            amount=amount_total,
            payment_id=session['id'],
            status='Completed'
        )
        

        #sending confimation mail
        subject = "Payment Received"
        message = f"Dear {product.first_name},<br><br>" \
                      f"Your payment for order {prod_id} has been received.<br><br>" \
                      f"Order Details:<br><br>"\
                      f"ID: {prod_id}<br>"\
                      f"Title: {product.title}<br>"\
                      f"Total Price: {product.total_price}<br>"\
                      f"Total Paid: {product.total_paid}<br>"\
                      f"Status: {product.status}<br><br>"\
                      f"If you have any questions or need further assistance, please don't hesitate to contact us.<br><br>"\
                      f"Best regards,<br>"\
                      f"Sazzad Hossen"
        data = {
                'subject': subject,
                'body': '',
                'html_body': message,
                'to_email': product.email
            }
        Util.send_email(data)
       
    # Passed signature verification
    return HttpResponse(status=200)

@api_view(['GET'])
def UserTransactionsView(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user)
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def AllTransactionsView(request):
    transactions = Transaction.objects.all()
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
def DeleteTransactionView(request, transaction_id):
    try:
        transaction = Transaction.objects.get(id=transaction_id)
    except Transaction.DoesNotExist:
        return Response({'message': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        transaction.delete()
        return Response({'message': 'Transaction deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'message': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)
