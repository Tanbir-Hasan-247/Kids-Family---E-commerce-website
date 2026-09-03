from Cart.views import get_or_create_cart
from Wishlist.views import get_identity_filter
from Wishlist.models import FavoriteItem
from Category.models import Category


def cart_and_favorites_count(request):
    """
    Shob template e {{ cart_count }} ar {{ favorite_count }} available kore dey,
    navbar badge e use korar jonno. Prottek request e ekbar-i query hoy.
    """
    try:
        cart = get_or_create_cart(request)
        cart_count = cart.total_items
    except Exception:
        cart_count = 0

    try:
        identity = get_identity_filter(request)
        favorite_count = FavoriteItem.objects.filter(**identity).count()
    except Exception:
        favorite_count = 0

    return {
        'cart_count': cart_count,
        'favorite_count': favorite_count,
    }


def nav_categories(request):
    """
    Navbar-er 'Categories' dropdown (desktop) ar mobile accordion e use korar jonno
    shob page e top-level category + tader children available kore dey.
    """
    try:
        categories = Category.objects.filter(parent__isnull=True).prefetch_related('children')
    except Exception:
        categories = []

    return {'nav_categories': categories}