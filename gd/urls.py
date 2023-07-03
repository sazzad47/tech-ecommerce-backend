from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet,
    TipViewSet,
    DonationViewSet,
    CommentViewSet,
    get_post_countries_view,
    DonationIntentCreateView,
    stripe_webhook,
    PostDetailsAPIView,
)

# Create a router and register the viewsets
router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('tips', TipViewSet, basename='tip')
router.register('donations', DonationViewSet, basename='donation')
router.register('comments', CommentViewSet, basename='comment')

urlpatterns = [
    # Other URL patterns for your project
    
    # Include the router URLs
    path('', include(router.urls)),
    path('post-countries/', get_post_countries_view, name='post-countries'),
    path('create-donation/<int:pk>/', DonationIntentCreateView.as_view(), name='create-donation'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
    path('donors-comments/<int:post_id>/', PostDetailsAPIView.as_view(), name='donors-comments'),
]
