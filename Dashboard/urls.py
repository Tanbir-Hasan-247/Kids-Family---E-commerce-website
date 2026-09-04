from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/notifications/count/', views.notifications_count, name='notifications_count'),

    path('dashboard/products/', views.product_list_admin, name='product_list_admin'),
    path('dashboard/products/add/', views.product_create_admin, name='product_create_admin'),
    path('dashboard/products/<int:pk>/edit/', views.product_edit_admin, name='product_edit_admin'),
    path('dashboard/products/<int:pk>/delete/', views.product_delete_admin, name='product_delete_admin'),

    path('dashboard/orders/', views.order_list_admin, name='order_list_admin'),
    path('dashboard/orders/<str:order_number>/', views.order_detail_admin, name='order_detail_admin'),
]
