from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet,
    CompletedPostViewSet,
    get_post_countries_view,
    DonationIntentCreateView,
    stripe_webhook,
    PostDetailsAPIView,
    SinglePostView,
    UserDonationsView,
    UserTipsView,
    PostListView,
    PostUpdateView,
    PostDetailView,
    create_donations_withdrawal_request,
    update_donations_withdrawal_request,
    delete_donations_withdrawal_request,
    get_donations_withdrawal_requests,
    create_tips_withdrawal_request,
    update_tips_withdrawal_request,
    delete_tips_withdrawal_request,
    get_tips_withdrawal_requests,
)

# Create a router and register the viewsets
router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')


urlpatterns = [
    # Other URL patterns for your project
    
    # Include the router URLs
    path('', include(router.urls)),
    path('completed-posts/', CompletedPostViewSet.as_view({'get': 'list'}), name='completed-post-list'),
    path('single-post/<int:pk>/', SinglePostView.as_view(), name='single-post'),
    path('post-countries/', get_post_countries_view, name='post-countries'),
    path('create-donation/<int:pk>/', DonationIntentCreateView.as_view(), name='create-donation'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
    path('donors-comments/<int:post_id>/', PostDetailsAPIView.as_view(), name='donors-comments'),
    path('donations/', UserDonationsView, name='user_donations'),
    path('tips/', UserTipsView, name='user_tips'),
    path('user-posts/', PostListView.as_view(), name='user-post-list'),
    path('user-posts/edit/<int:pk>/', PostUpdateView.as_view(), name='user-post-update'),
    path('user-posts/<int:pk>/', PostDetailView.as_view(), name='user-post-detail'),
    path('donations-withdrawal/create/', create_donations_withdrawal_request, name='create_donations_withdrawal_request'),
    path('donations-withdrawal/update/<int:withdrawal_request_id>/', update_donations_withdrawal_request, name='update_donations_withdrawal_request'),
    path('donations-withdrawal/delete/<int:withdrawal_request_id>/', delete_donations_withdrawal_request, name='delete_donations_withdrawal_request'),
    path('donations-withdrawal/requests/', get_donations_withdrawal_requests, name='get_donations_withdrawal_requests'),
    path('tips-withdrawal/create/', create_tips_withdrawal_request, name='create_tips_withdrawal_request'),
    path('tips-withdrawal/update/<int:withdrawal_request_id>/', update_tips_withdrawal_request, name='update_tips_withdrawal_request'),
    path('tips-withdrawal/delete/<int:withdrawal_request_id>/', delete_tips_withdrawal_request, name='delete_tips_withdrawal_request'),
    path('tips-withdrawal/requests/', get_tips_withdrawal_requests, name='get_tips_withdrawal_requests'),
]
