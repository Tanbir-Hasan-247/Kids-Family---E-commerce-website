from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('cart/', views.cart_view, name='cart_view'),
    
    # Eita update kora hoyeche (AJAX Drawer er jonno)
    path('cart/drawer/', views.cart_drawer, name='cart_drawer'),
    
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
]