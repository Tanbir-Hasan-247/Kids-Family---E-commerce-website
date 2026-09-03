from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from Product.models import Product
from .models import FavoriteItem


# ==========================================
# HELPER: guest hole session_key diye, login thakle user diye identity return kore
# ==========================================
def get_identity_filter(request):
    if request.user.is_authenticated:
        return {'user': request.user}

    if not request.session.session_key:
        request.session.create()

    return {'session_key': request.session.session_key}


def get_favorited_product_ids(request):
    """product_list_view / home_view theke call kore heart icon-er filled/unfilled
    state thik dekhanor jonno."""
    identity = get_identity_filter(request)
    return set(FavoriteItem.objects.filter(**identity).values_list('product_id', flat=True))


# ==========================================
# FUTURE USE: login korar shomoy guest favorite -> user favorite merge
# ==========================================
def merge_guest_favorites_into_user(request, user):
    if not request.session.session_key:
        return

    guest_items = FavoriteItem.objects.filter(session_key=request.session.session_key, user=None)
    for item in guest_items:
        FavoriteItem.objects.get_or_create(user=user, product=item.product)
    guest_items.delete()


# ==========================================
# TOGGLE FAVORITE (AJAX) — heart icon click (product list/detail page)
# ==========================================
@require_POST
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    identity = get_identity_filter(request)

    existing = FavoriteItem.objects.filter(product=product, **identity).first()
    if existing:
        existing.delete()
        favorited = False
    else:
        FavoriteItem.objects.create(product=product, **identity)
        favorited = True

    count = FavoriteItem.objects.filter(**identity).count()

    return JsonResponse({'success': True, 'favorited': favorited, 'count': count})


# ==========================================
# WISHLIST PAGE
# ==========================================
def favorites_view(request):
    identity = get_identity_filter(request)
    items = FavoriteItem.objects.filter(**identity).select_related('product').prefetch_related('product__variants')
    return render(request, 'favorites.html', {'items': items})


# ==========================================
# FAVORITES DRAWER (mini wishlist) — navbar icon click e AJAX diye load hoy
# base.html theke fetch('/favorites/mini/') call hoy, response e {'html':..., 'count':...} lagbe
# ==========================================
def favorites_mini_view(request):
    identity = get_identity_filter(request)
    items = FavoriteItem.objects.filter(**identity).select_related('product').prefetch_related('product__variants')
    html = render_to_string('favorites_drawer.html', {'items': items}, request=request)
    return JsonResponse({'html': html, 'count': items.count()})