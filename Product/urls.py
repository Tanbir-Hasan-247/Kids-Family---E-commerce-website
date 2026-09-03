from django.urls import path
from . import views
from kids_family.views import filter_products_ajax

app_name = "store"  # apnar app er nam diben

urlpatterns = [
    path("products/", views.product_list_view, name="product_list"),
    path(
        "category/<slug:category_slug>/",
        views.product_list_view,
        name="category_products",
    ),
    path("search/", views.product_list_view, name="search"),
    # Product Detail (Using slug for clean URL)
    path("product/<int:pk>/", views.product_detail_view, name="product_detail"),
    # AJAX Endpoint (Using ID/PK)
    path("product/<int:pk>/variant/", views.get_variant_data, name="get_variant"),
    path('ajax/filter-products/', filter_products_ajax, name='filter_products_all'),
    path('ajax/filter-products/<slug:slug>/', filter_products_ajax, name='filter_products'),
    path("add/", views.add_product),
]
