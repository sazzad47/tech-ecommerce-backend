from django.urls import path, include
from .views import CompanyViewSet, ServiceViewSet, DesignViewSet, TemplateViewSet, FooterPageViewSet, ProductViewSet, SocialLinkViewSet, GlobalLocationViewSet, SecurityViewSet, PaymentOptionViewSet, AllTransactionsView, DeleteTransactionView, GetOrdersByStatusView, OrderCreateView, OrderUpdateView, OrderDetailView, OrderListView, PaymentIntentCreateView, stripe_webhook, UserTransactionsView 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'security', SecurityViewSet)
router.register(r'company', CompanyViewSet)
router.register(r'service', ServiceViewSet)
router.register(r'product', ProductViewSet)
router.register(r'global-location', GlobalLocationViewSet)
router.register(r'social-link', SocialLinkViewSet)
router.register(r'payment-option', PaymentOptionViewSet)
router.register(r'footer-page', FooterPageViewSet)
router.register(r'design', DesignViewSet)
router.register(r'template', TemplateViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/edit-delete/<int:pk>/', OrderUpdateView.as_view(), name='order-update'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('create-payment/<int:pk>/', PaymentIntentCreateView.as_view(), name='create-payment'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
    path('transactions/', UserTransactionsView, name='user_transactions'),
    path('transactions/all/', AllTransactionsView, name='user_all_transactions'),
    path('transactions/<int:transaction_id>/delete/', DeleteTransactionView, name='transactions_delete'),
    path('orders/<str:status>/', GetOrdersByStatusView.as_view(), name='admin_all_orders'),
]
