from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('favorites/', views.favorites_view, name='favorites_view'),
    path('favorites/mini/', views.favorites_mini_view, name='favorites_mini'),
    path('favorites/toggle/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
]