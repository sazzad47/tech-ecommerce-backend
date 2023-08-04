from django.urls import path, include
from .views import CompanyViewSet, SecurityViewSet, OrderCreateView, OrderUpdateView, OrderDetailView, OrderListView, PaymentIntentCreateView, stripe_webhook, UserTransactionsView 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'security', SecurityViewSet)
router.register(r'company', CompanyViewSet)

urlpatterns = [
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/edit/<int:pk>/', OrderUpdateView.as_view(), name='order-update'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('create-payment/<int:pk>/', PaymentIntentCreateView.as_view(), name='create-payment'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
    path('transactions/', UserTransactionsView, name='user_transactions'),
    path('', include(router.urls)),
]
