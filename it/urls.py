from django.urls import path, include
from it.views import OrderListCreateUpdateView, OrderUpdateView

urlpatterns = [
    path('orders/', OrderListCreateUpdateView.as_view(), name='order-list-create'),
    path('orders/<int:pk>/', OrderUpdateView.as_view(), name='order-update'),
]
