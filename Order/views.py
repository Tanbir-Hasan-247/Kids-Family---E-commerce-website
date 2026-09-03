from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction

from Cart.views import get_or_create_cart
from .models import Order, OrderItem
from .forms import CheckoutForm


# ==========================================
# HELPER: guest hole session_key diye, login thakle user diye identity return kore
# ==========================================
def get_order_identity(request):
    if request.user.is_authenticated:
        return {'user': request.user}

    if not request.session.session_key:
        request.session.create()

    return {'session_key': request.session.session_key}


# ==========================================
# CHECKOUT PAGE
# ==========================================
def checkout_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('variant__product').all()

    if not cart_items.exists():
        messages.info(request, "Your bag is empty — add something first.")
        return redirect('cart:cart_view')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            # Stock abar check kora hocche, karon cart e add korar por stock kome giye thakte pare
            insufficient = []
            for item in cart_items:
                if item.quantity > item.variant.stock:
                    insufficient.append(item.variant.product.name)

            if insufficient:
                messages.error(
                    request,
                    f"Sorry, not enough stock for: {', '.join(insufficient)}. Please update your bag."
                )
                return redirect('cart:cart_view')

            with transaction.atomic():
                identity = get_order_identity(request)
                subtotal = cart.total_price
                shipping_fee = 60  # static shipping fee — pore dynamic (city/weight based) kora jabe
                total = subtotal + shipping_fee

                order = Order.objects.create(
                    **identity,
                    full_name=form.cleaned_data['full_name'],
                    phone=form.cleaned_data['phone'],
                    email=form.cleaned_data['email'],
                    address_line=form.cleaned_data['address_line'],
                    city=form.cleaned_data['city'],
                    notes=form.cleaned_data['notes'],
                    payment_method=form.cleaned_data['payment_method'],
                    subtotal=subtotal,
                    shipping_fee=shipping_fee,
                    total=total,
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        variant=item.variant,
                        product_name=item.variant.product.name,
                        variant_sku=item.variant.sku,
                        price=item.variant.price,
                        quantity=item.quantity,
                    )
                    # Stock kome jabe order confirm howar shathe shathe
                    item.variant.stock -= item.quantity
                    item.variant.save()

                # Order hoye gele cart khali kore dao
                cart_items.delete()

            if order.payment_method == 'online':
                # Static placeholder — real gateway ekhane pore integrate hobe
                return redirect('orders:payment_stub', order_number=order.order_number)

            messages.success(request, "Your order has been placed!")
            return redirect('orders:order_success', order_number=order.order_number)
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['email'] = request.user.email
        form = CheckoutForm(initial=initial)

    context = {
        'form': form,
        'cart': cart,
        'items': cart_items,
        'shipping_fee': 60,
        'grand_total': cart.total_price + 60,
    }
    return render(request, 'checkout.html', context)


# ==========================================
# PAYMENT STUB (Online payment placeholder — static for now)
# ==========================================
def payment_stub_view(request, order_number):
    identity = get_order_identity(request)
    order = get_object_or_404(Order, order_number=order_number, **identity)

    if order.payment_status == 'paid':
        return redirect('orders:order_success', order_number=order.order_number)

    if request.method == 'POST':
        # TODO: ekhane real payment gateway (SSLCommerz / Stripe / bKash API) integrate hobe.
        # Ekhon shudhu static "paid" mark kore dicche demo/testing er jonno.
        order.payment_status = 'paid'
        order.status = 'confirmed'
        order.save()
        messages.success(request, "Payment successful!")
        return redirect('orders:order_success', order_number=order.order_number)

    return render(request, 'payment_stub.html', {'order': order})


# ==========================================
# ORDER SUCCESS / CONFIRMATION PAGE
# ==========================================
def order_success_view(request, order_number):
    identity = get_order_identity(request)
    order = get_object_or_404(Order, order_number=order_number, **identity)
    return render(request, 'order_success.html', {'order': order})


# ==========================================
# ORDER HISTORY (logged-in user ba guest session er shob order)
# ==========================================
def order_history_view(request):
    identity = get_order_identity(request)
    orders = Order.objects.filter(**identity).prefetch_related('items').order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})


# ==========================================
# ORDER DETAIL
# ==========================================
def order_detail_view(request, order_number):
    identity = get_order_identity(request)
    order = get_object_or_404(
        Order.objects.prefetch_related('items__variant__product'),
        order_number=order_number, **identity
    )
    return render(request, 'order_detail.html', {'order': order})
