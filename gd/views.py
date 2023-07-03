from rest_framework import viewsets
from .models import Post, Tip, Donation, Comment
from .serializers import PostSerializer, TipSerializer, DonorSerializer, CommentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from .utils import get_post_countries
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
import stripe
import json
from rest_framework.permissions import IsAuthenticated
from utils import Util
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djmoney.money import Money

class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status='Approved').order_by('-created_at')
    serializer_class = PostSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['category', 'country']
    search_fields = [
        '^mode', '^category', '^first_name', '^last_name',
        '^country', '^province', '^city', '^zip', '^address', '^name_of_employment', '^written_description'
    ]
    ordering_fields = ['created_at']  # Replace with your desired field for sorting
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        # Assign the logged-in user to the user field
        serializer.save(user=self.request.user)


    def get_queryset(self):
        queryset = super().get_queryset()
        emergency = self.request.query_params.get('emergency')
        if emergency == 'true':
            queryset = queryset.filter(mode='emergency')
        elif emergency == 'false':
            queryset = queryset.filter(mode='normal')

        return queryset.filter(status='Approved')
    

class TipViewSet(viewsets.ModelViewSet):
    queryset = Tip.objects.all()
    serializer_class = TipSerializer

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonorSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

def get_post_countries_view(request):
    post_countries = get_post_countries()

    # Convert the QuerySet to a list
    post_countries_list = list(post_countries)

    # Return as JSON response
    data = {'countries': post_countries_list}
    return JsonResponse(data)

class DonationIntentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        prod_id = self.kwargs["pk"]
        currency = request.data.get('currency')  
        donation_amount = request.data.get('donation_amount')  
        tips_amount = request.data.get('tips_amount')  
        comment = request.data.get('comment')  
        is_hidden = request.data.get('is_hidden')  
        user_id = request.user.id         
        amount = (int(donation_amount) + int(tips_amount)) * 100

        try:
            post = get_object_or_404(Post, id=prod_id)
            
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price_data': {
                            'currency': currency,
                            'unit_amount': amount,
                            'product_data': {
                                'name': post.title,
                            },
                        },
                        'quantity': 1,
                    },
                ],
                metadata={
                    'product_id': post.id,
                    'donation_amount': donation_amount,
                    'tips_amount': tips_amount,
                    'currency': currency,
                    'comment': comment,
                    'user_id': user_id,
                    'is_hidden': is_hidden
                },
                mode='payment',
                success_url='http://localhost:3000/it/orders/payment' + '?success=true',
                cancel_url=f"http://localhost:3000/it/profile/orders/{post.id}",
            )
            
            return Response({'checkout_url': checkout_session.url})
        
        except Exception as e:
            return Response({'msg': 'Something went wrong while creating the Stripe session', 'error': str(e)}, status=500)



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        prod_id = session['metadata']['product_id']
        post = get_object_or_404(Post, id=prod_id)

        # Create a donation record
        donation_amount = session['metadata']['donation_amount']
        tips_amount = session['metadata']['tips_amount']
        currency = session['metadata']['currency']
        user_id = session['metadata']['user_id']
        is_hidden = session['metadata']['is_hidden']

        # Print session data
        print('Session Data:')
        session_json = json.dumps(session, indent=4)
        print(session_json)

        Donation.objects.create(
            user_id=user_id,
            post=post,
            amount=Money(donation_amount, currency),
            is_hidden=is_hidden
            
        )

        # Add tips to the post
        tips = session['metadata'].get('tips_amount')
        if tips:
            Tip.objects.create(
                user_id=user_id,
                post=post,
                amount=Money(tips_amount, currency),
                is_hidden=is_hidden
            )

        # Add comment to the post
        comment = session['metadata'].get('comment')
        if comment:
            Comment.objects.create(
                user_id=user_id,
                post=post,
                content=comment,
                is_hidden=is_hidden
            )

    # Passed signature verification
    return HttpResponse(status=200)

class PostDetailsAPIView(APIView):
    def get(self, request, post_id):
        post = Post.objects.get(pk=post_id)

        # Get all comments for the post
        comments = Comment.objects.filter(post=post, is_hidden=False)
        comment_serializer = CommentSerializer(comments, many=True)

        # Get top 10 donors for the post
        top_donors = Donation.objects.filter(post=post, is_hidden=False).order_by('-amount')[:10]
        donor_serializer = DonorSerializer(top_donors, many=True)

        return Response({
            'comments': comment_serializer.data,
            'top_donors': donor_serializer.data
        })

@api_view(['GET'])
def UserTransactionsView(request):
    user = request.user
    transactions = Donation.objects.filter(user=user)
    serializer = DonorSerializer(transactions, many=True)
    return Response(serializer.data)
