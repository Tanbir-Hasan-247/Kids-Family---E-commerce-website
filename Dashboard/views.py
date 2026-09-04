from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.http import JsonResponse
from django.core.paginator import Paginator

from Order.models import Order, OrderItem
from Product.models import Product
from Product.forms import ProductForm, VariantFormSet
from .decorators import staff_or_moderator_required


# ==========================================
# DASHBOARD HOME — sales performance
# ==========================================
@staff_or_moderator_required
def dashboard_home(request):
    valid_orders = Order.objects.exclude(status='cancelled')

    total_revenue = valid_orders.aggregate(total=Sum('total'))['total'] or 0
    total_orders = valid_orders.count()
    pending_orders = Order.objects.filter(status='pending').count()

    today = timezone.now().date()
    today_revenue = valid_orders.filter(created_at__date=today).aggregate(total=Sum('total'))['total'] or 0

    # Last 14 din er revenue — line chart er jonno
    since = today - timedelta(days=13)
    daily_sales = (
        valid_orders.filter(created_at__date__gte=since)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(revenue=Sum('total'))
        .order_by('day')
    )
    sales_by_day = {entry['day']: float(entry['revenue']) for entry in daily_sales}
    chart_labels = []
    chart_values = []
    for i in range(14):
        d = since + timedelta(days=i)
        chart_labels.append(d.strftime('%d %b'))
        chart_values.append(sales_by_day.get(d, 0))

    # Top selling products (quantity diye)
    top_products = (
        OrderItem.objects.filter(order__in=valid_orders)
        .values('product_name')
        .annotate(total_qty=Sum('quantity'), total_revenue=Sum('price'))
        .order_by('-total_qty')[:5]
    )

    recent_orders = Order.objects.select_related().order_by('-created_at')[:8]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'today_revenue': today_revenue,
        'chart_labels': chart_labels,
        'chart_values': chart_values,
        'top_products': top_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard_home.html', context)


# ==========================================
# NOTIFICATION COUNT (polling endpoint)
# ==========================================
@staff_or_moderator_required
def notifications_count(request):
    count = Order.objects.filter(status='pending').count()
    return JsonResponse({'count': count})


# ==========================================
# PRODUCT MANAGEMENT
# ==========================================
@staff_or_moderator_required
def product_list_admin(request):
    products = Product.objects.select_related('category').prefetch_related('variants').order_by('-id')

    search = request.GET.get('q')
    if search:
        products = products.filter(name__icontains=search)

    paginator = Paginator(products, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'product_list_admin.html', {'page_obj': page_obj, 'search': search or ''})


@staff_or_moderator_required
def product_delete_admin(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" has been deleted.')
        return redirect('dashboard:product_list_admin')

    return render(request, 'product_delete_confirm.html', {'product': product})


@staff_or_moderator_required
def product_create_admin(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            formset = VariantFormSet(request.POST, request.FILES, instance=product)
            if formset.is_valid():
                formset.save()
                messages.success(request, f'"{product.name}" has been added.')
                return redirect('dashboard:product_list_admin')
        else:
            formset = VariantFormSet(request.POST, request.FILES)
    else:
        form = ProductForm()
        formset = VariantFormSet()

    return render(request, 'product_form_admin.html', {
        'form': form, 'formset': formset, 'is_edit': False,
    })


@staff_or_moderator_required
def product_edit_admin(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = VariantFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'"{product.name}" has been updated.')
            return redirect('dashboard:product_list_admin')
    else:
        form = ProductForm(instance=product)
        formset = VariantFormSet(instance=product)

    return render(request, 'product_form_admin.html', {
        'form': form, 'formset': formset, 'is_edit': True, 'product': product,
    })


# ==========================================
# ORDER MANAGEMENT
# ==========================================
@staff_or_moderator_required
def order_list_admin(request):
    orders = Order.objects.order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)

    paginator = Paginator(orders, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'order_list_admin.html', {
        'page_obj': page_obj,
        'status_filter': status_filter or '',
        'status_choices': Order.STATUS_CHOICES,
    })


@staff_or_moderator_required
def order_detail_admin(request, order_number):
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_payment_status = request.POST.get('payment_status')

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
        if new_payment_status in dict(Order.PAYMENT_STATUS_CHOICES):
            order.payment_status = new_payment_status

        order.save()
        messages.success(request, f'Order {order.order_number} updated.')
        return redirect('dashboard:order_detail_admin', order_number=order.order_number)

    return render(request, 'order_detail_admin.html', {'order': order})
