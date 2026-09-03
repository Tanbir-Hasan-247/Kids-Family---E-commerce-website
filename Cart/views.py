from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from Product.models import ProductVariant
from .models import Cart, CartItem


# ==========================================
# HELPER: guest hole session diye, login thakle user diye cart khuje/banay
# ==========================================
def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    if not request.session.session_key:
        request.session.create()

    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
    return cart


# ==========================================
# FUTURE USE: login korar shomoy (signal/view e call korte hobe) guest cart
# ke user cart er shathe merge kore dey
# ==========================================
def merge_guest_cart_into_user(request, user):
    if not request.session.session_key:
        return

    try:
        guest_cart = Cart.objects.get(session_key=request.session.session_key, user=None)
    except Cart.DoesNotExist:
        return

    user_cart, _ = Cart.objects.get_or_create(user=user)

    for item in guest_cart.items.all():
        existing = CartItem.objects.filter(cart=user_cart, variant=item.variant).first()
        if existing:
            existing.quantity += item.quantity
            existing.save()
        else:
            item.cart = user_cart
            item.save()

    guest_cart.delete()


# ==========================================
# ADD TO CART (AJAX)
# ==========================================
@require_POST
def add_to_cart(request, product_id):
    variant_id = request.POST.get('variant_id')

    if not variant_id or not str(variant_id).isdigit():
        return JsonResponse({'success': False, 'message': 'Please select a valid color and size.'}, status=400)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    variant = get_object_or_404(ProductVariant, pk=int(variant_id), product_id=product_id)

    if variant.stock < 1:
        return JsonResponse({'success': False, 'message': 'This item is out of stock.'}, status=400)

    cart = get_or_create_cart(request)

    item, created = CartItem.objects.get_or_create(cart=cart, variant=variant, defaults={'quantity': quantity})
    if not created:
        item.quantity += quantity
        item.save()

    if item.quantity > variant.stock:
        item.quantity = variant.stock
        item.save()

    total_qty = sum(i.quantity for i in cart.items.all())

    return JsonResponse({
        'success': True,
        'message': 'Added to your bag!',
        'cart_count': total_qty,
        # cart_total o pathiye dilam — drawer khola thakle add-to-cart-er por
        # eta diyeo total price update kora jabe (product_detail.html-e ekhon use hocche na,
        # future-e drawer live-refresh korte chaile kaje lagbe)
        'cart_total': str(cart.total_price),
        'item_quantity': item.quantity,
    })


# ==========================================
# UPDATE QUANTITY (AJAX) — cart page theke +/- button
# ==========================================
@require_POST
def update_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    action = request.POST.get('action')
    if action == 'increase' and item.quantity < item.variant.stock:
        item.quantity += 1
        item.save()
    elif action == 'decrease':
        item.quantity -= 1
        if item.quantity < 1:
            item.delete()
            return JsonResponse({
                'success': True, 'removed': True,
                'cart_count': cart.total_items, 'cart_total': str(cart.total_price),
            })
        item.save()

    return JsonResponse({
        'success': True, 'removed': False,
        'quantity': item.quantity,
        'subtotal': str(item.subtotal),
        'cart_count': cart.total_items,
        'cart_total': str(cart.total_price),
    })


# ==========================================
# REMOVE ITEM (AJAX)
# ==========================================
@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()

    return JsonResponse({
        'success': True,
        'cart_count': cart.total_items,
        'cart_total': str(cart.total_price),
    })


# ==========================================
# CART PAGE
# ==========================================
def cart_view(request):
    cart = get_or_create_cart(request)
    return render(request, 'cart.html', {'cart': cart, 'items': cart.items.select_related('variant__product').all()})


# ==========================================
# CART DRAWER (AJAX) — navbar icon click e load hobe
# ==========================================
def cart_drawer(request):
    cart = get_or_create_cart(request)

    items = cart.items.select_related('variant__product').all()

    html = render_to_string(
        'cart_drawer_items.html',
        {'cart': cart, 'items': items},
        request=request
    )

    # JSON response e html, total count, abong total price — tinta-i pathacche
    return JsonResponse({
        'html': html,
        'count': cart.total_items,
        'total': str(cart.total_price),
    })