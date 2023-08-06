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
    GetPostsByStatusView,
    create_donations_withdrawal_request,
    update_donations_withdrawal_request,
    delete_donations_withdrawal_request,
    get_donations_withdrawal_requests,
    create_tips_withdrawal_request,
    update_tips_withdrawal_request,
    delete_tips_withdrawal_request,
    get_tips_withdrawal_requests,
    AllDonationsView,
    DeleteDonationView,
    AllTipsView,
    DeleteTipView,
    GetDonationsWithdrawalRequestByStatusView,
    DonationsWithdrawalRequestViewSet,
    TipsWithdrawalRequestViewSet,
    GetTipsWithdrawalRequestByStatusView,
    CompanyViewSet, FooterPageViewSet, SocialLinkViewSet, GlobalLocationViewSet, PaymentOptionViewSet
)

# Create a router and register the viewsets
router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register(r'company', CompanyViewSet)
router.register(r'global-location', GlobalLocationViewSet)
router.register(r'social-link', SocialLinkViewSet)
router.register(r'payment-option', PaymentOptionViewSet)
router.register(r'footer-page', FooterPageViewSet)
router.register(r'admin-donationsWithdrawalRequests', DonationsWithdrawalRequestViewSet)
router.register(r'admin-tipsWithdrawalRequests', TipsWithdrawalRequestViewSet)



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
    path('donations/all/', AllDonationsView, name='user_all_donations'),
    path('donations/<int:donation_id>/delete/', DeleteDonationView, name='donations_delete'),
    path('tips/all/', AllTipsView, name='user_all_tips'),
    path('tips/<int:tip_id>/delete/', DeleteTipView, name='tips_delete'),
    path('tips/', UserTipsView, name='user_tips'),
    path('user-posts/', PostListView.as_view(), name='user-post-list'),
    path('user-posts/edit/<int:pk>/', PostUpdateView.as_view(), name='user-post-update'),
    path('user-posts/<int:pk>/', PostDetailView.as_view(), name='user-post-detail'),
    path('admin-posts/<str:status>/', GetPostsByStatusView.as_view(), name='admin_all_posts'),
    path('donations-withdrawal/create/', create_donations_withdrawal_request, name='create_donations_withdrawal_request'),
    path('donations-withdrawal/update/<int:withdrawal_request_id>/', update_donations_withdrawal_request, name='update_donations_withdrawal_request'),
    path('donations-withdrawal/delete/<int:withdrawal_request_id>/', delete_donations_withdrawal_request, name='delete_donations_withdrawal_request'),
    path('donations-withdrawal/requests/', get_donations_withdrawal_requests, name='get_donations_withdrawal_requests'),
    path('donations-withdrawal/<str:status>/', GetDonationsWithdrawalRequestByStatusView.as_view(), name='admin_donations-withdrawal-status'),
    path('tips-withdrawal/<str:status>/', GetTipsWithdrawalRequestByStatusView.as_view(), name='admin_tips-withdrawal-status'),
    path('tips-withdrawal/create/', create_tips_withdrawal_request, name='create_tips_withdrawal_request'),
    path('tips-withdrawal/update/<int:withdrawal_request_id>/', update_tips_withdrawal_request, name='update_tips_withdrawal_request'),
    path('tips-withdrawal/delete/<int:withdrawal_request_id>/', delete_tips_withdrawal_request, name='delete_tips_withdrawal_request'),
    path('tips-withdrawal/requests/', get_tips_withdrawal_requests, name='get_tips_withdrawal_requests'),
    
]
