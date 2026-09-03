from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    can_delete = False
    readonly_fields = ('variant', 'product_name', 'variant_sku', 'price', 'quantity', 'subtotal_display')

    def subtotal_display(self, obj):
        return f"৳{obj.subtotal}"
    subtotal_display.short_description = 'Subtotal'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'full_name', 'phone', 'city',
        'payment_method', 'payment_status', 'status', 'total', 'created_at',
    )
    list_display_links = ('order_number', 'full_name')
    list_editable = ('status', 'payment_status')  # admin list theke shorashori status change kora jabe
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('order_number', 'full_name', 'phone', 'email')
    readonly_fields = (
        'order_number', 'user', 'session_key',
        'subtotal', 'shipping_fee', 'total', 'created_at', 'updated_at',
    )
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'status', 'created_at', 'updated_at')
        }),
        ('Customer', {
            'fields': ('user', 'session_key', 'full_name', 'phone', 'email')
        }),
        ('Shipping', {
            'fields': ('address_line', 'city', 'notes')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'subtotal', 'shipping_fee', 'total')
        }),
    )
