# admin.py
from django.contrib import admin
from .models import Product, ProductVariant, AttributeType, AttributeValue
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 3  # একসাথে ৩টা খালি ফর্ম দেখাবে নতুন ভ্যারিয়েন্ট অ্যাড করার জন্য
    filter_horizontal = ('attributes',)  # color/size multi-select সহজ করে

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    inlines = [ProductVariantInline]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'sku', 'price', 'stock')
    list_filter = ('attributes',)


admin.site.register(AttributeType)
admin.site.register(AttributeValue)