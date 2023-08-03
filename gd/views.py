from rest_framework import viewsets
from .models import Post, Tip, Donation, Comment, DonationsWithdrawalRequest, TipsWithdrawalRequest
from .serializers import PostSerializer, PostListSerializer, DonationsWithdrawalRequestSerializer, PostItemSerializer, TipSerializer, DonorSerializer, CommentSerializer, TipsWithdrawalRequestSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from .utils import get_post_countries
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import generics, permissions
import stripe
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djmoney.money import Money
from django.db.models import F
from rest_framework.generics import RetrieveAPIView
from djmoney.contrib.exchange.models import convert_money
from app.settings import BASE_CLIENT_URL

class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status='Approved').filter(donation_needed__gt=F('total_donations')).order_by('-created_at')
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
    
class CompletedPostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status='Approved').filter(donation_needed=F('total_donations')).order_by('-created_at')
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

        return queryset.filter(status='Approved').filter(donation_needed=F('total_donations'))
    
class SinglePostView(RetrieveAPIView):
    queryset = Post.objects.filter(status='Approved', donation_needed=F('total_donations'))
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


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
        company_tips_amount = request.data.get('company_tips_amount')  
        volunteer_tips_amount = request.data.get('volunteer_tips_amount')  
        comment = request.data.get('comment')  
        is_hidden = request.data.get('is_hidden')  
        user_id = request.user.id         
        amount = (int(donation_amount) + int(company_tips_amount) + int(volunteer_tips_amount)) * 100

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
                    'company_tips_amount': company_tips_amount,
                    'volunteer_tips_amount': volunteer_tips_amount,
                    'currency': currency,
                    'comment': comment,
                    'user_id': user_id,
                    'is_hidden': is_hidden
                },
                mode='payment',
                success_url=BASE_CLIENT_URL +'/gd/causes/donation-message?success=true',
                cancel_url=BASE_CLIENT_URL + '/gd/causes/donate' + post.id,
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
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET_GD
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
        user = post.user

        # Create a donation record
        currency = session['metadata']['currency']
        donation_amount = session['metadata']['donation_amount']
        donation_amount_money = Money(donation_amount, currency)
        amount_usd = convert_money(donation_amount_money, 'USD')
        company_tips_amount = session['metadata']['company_tips_amount']
        volunteer_tips_amount = session['metadata']['volunteer_tips_amount']
        volunteer_tips_money = Money(volunteer_tips_amount, currency)
        volunteer_tips_usd = convert_money(volunteer_tips_money, 'USD')
        user_id = session['metadata']['user_id']
        is_hidden = session['metadata']['is_hidden']

        # Print session data
        print('Session Data:')
        session_json = json.dumps(session, indent=4)
        print(session_json)

        if volunteer_tips_amount:
            user.tips += volunteer_tips_usd

        user.funds += amount_usd
        user.save()
        
        Donation.objects.create(
            user_id=user_id,
            post=post,
            amount=Money(donation_amount, currency),
            is_hidden=is_hidden
            
        )

        # Add tips to the post
        company_tips = session['metadata'].get('company_tips_amount')
        volunteer_tips = session['metadata'].get('volunteer_tips_amount')
        if company_tips or volunteer_tips:
            Tip.objects.create(
                user_id=user_id,
                post=post,
                company_tips=Money(company_tips_amount, currency),
                volunteer_tips=Money(volunteer_tips_amount, currency),
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
        top_donors = Donation.objects.filter(post=post, is_hidden=False).order_by('-amount')[:5]
        donor_serializer = DonorSerializer(top_donors, many=True)

        return Response({
            'comments': comment_serializer.data,
            'top_donors': donor_serializer.data
        })

@api_view(['GET'])
def UserDonationsView(request):
    user = request.user
    transactions = Donation.objects.filter(user=user)
    serializer = DonorSerializer(transactions, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def UserTipsView(request):
    user = request.user
    tips = Tip.objects.filter(user=user)
    serializer = TipSerializer(tips, many=True)
    return Response(serializer.data)

class PostListView(generics.ListAPIView):
    serializer_class = PostListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Post.objects.filter(user=user)

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class PostUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_donations_withdrawal_request(request):
    serializer = DonationsWithdrawalRequestSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        amount = serializer.validated_data.get('amount')
        user = request.user

        # Update user's pending_withdrawal_donations field
        user.pending_withdrawal_donations += amount
        user.save()

        # Set the user field of the withdrawal request
        serializer.validated_data['user'] = user

        serializer.save()

        return Response({'message': 'Withdrawal request created successfully'})
    return Response(serializer.errors, status=400)

# View for updating an existing withdrawal request
@api_view(['PUT'])
def update_donations_withdrawal_request(request, withdrawal_request_id):
    withdrawal_request = get_object_or_404(DonationsWithdrawalRequest, pk=withdrawal_request_id)
    serializer = DonationsWithdrawalRequestSerializer(instance=withdrawal_request, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Withdrawal request updated successfully'})
    return Response(serializer.errors, status=400)

# View for deleting an existing withdrawal request
@api_view(['DELETE'])
def delete_donations_withdrawal_request(request, withdrawal_request_id):
    withdrawal_request = get_object_or_404(DonationsWithdrawalRequest, pk=withdrawal_request_id)
    withdrawal_request.delete()
    return Response({'message': 'Withdrawal request deleted successfully'})

# View for getting all withdrawal requests
@api_view(['GET'])
def get_donations_withdrawal_requests(request):
    withdrawal_requests = DonationsWithdrawalRequest.objects.all()
    serializer = DonationsWithdrawalRequestSerializer(withdrawal_requests, many=True)
    return Response({'withdrawal_requests': serializer.data})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_tips_withdrawal_request(request):
    serializer = TipsWithdrawalRequestSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        amount = serializer.validated_data.get('amount')
        user = request.user

        # Update user's pending_withdrawal_tips field
        user.pending_withdrawal_tips += amount
        user.save()

        # Set the user field of the withdrawal request
        serializer.validated_data['user'] = user

        serializer.save()

        return Response({'message': 'Withdrawal request created successfully'})
    return Response(serializer.errors, status=400)

# View for updating an existing withdrawal request
@api_view(['PUT'])
def update_tips_withdrawal_request(request, withdrawal_request_id):
    withdrawal_request = get_object_or_404(TipsWithdrawalRequest, pk=withdrawal_request_id)
    serializer = TipsWithdrawalRequestSerializer(instance=withdrawal_request, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Withdrawal request updated successfully'})
    return Response(serializer.errors, status=400)

# View for deleting an existing withdrawal request
@api_view(['DELETE'])
def delete_tips_withdrawal_request(request, withdrawal_request_id):
    withdrawal_request = get_object_or_404(TipsWithdrawalRequest, pk=withdrawal_request_id)
    withdrawal_request.delete()
    return Response({'message': 'Withdrawal request deleted successfully'})

# View for getting all withdrawal requests
@api_view(['GET'])
def get_tips_withdrawal_requests(request):
    withdrawal_requests = TipsWithdrawalRequest.objects.all()
    serializer = TipsWithdrawalRequestSerializer(withdrawal_requests, many=True)
    return Response({'withdrawal_requests': serializer.data})

# class VolunteerListCreateView(generics.ListCreateAPIView):
#     queryset = Volunteer.objects.all()
#     serializer_class = VolunteerSerializer

# class VolunteerDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Volunteer.objects.all()
#     serializer_class = VolunteerSerializer

# class VolunteerQueryView(generics.ListAPIView):
#     serializer_class = VolunteerSerializer

#     def get_queryset(self):
#         country = self.request.query_params.get('country', None)
#         state = self.request.query_params.get('state', None)
#         city = self.request.query_params.get('city', None)

#         queryset = Volunteer.objects.all()

#         if country:
#             queryset = queryset.filter(country=country)
#         if state:
#             queryset = queryset.filter(state=state)
#         if city:
#             queryset = queryset.filter(city=city)

#         return queryset