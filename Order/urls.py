from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('orders/', views.order_history_view, name='order_history'),
    path('orders/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('orders/<str:order_number>/success/', views.order_success_view, name='order_success'),
    path('orders/<str:order_number>/pay/', views.payment_stub_view, name='payment_stub'),
]
