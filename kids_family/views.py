from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Min
from Category.models import Category
from Product.models import Product

# Wishlist app er views theke helper function-ti import kora hocche
from Wishlist.views import get_favorited_product_ids


def home_view(request):
    # [:4] sorai dilam — slider-e slide korar jonno shob category lagbe
    categories = Category.objects.all()

    featured_products = Product.objects.select_related('category').prefetch_related('variants').filter(
        is_active=True
    ).annotate(
        starting_price=Min('variants__price')
    ).order_by('-id')[:8]

    # User er favorited product id gulo fetch kora
    favorited_product_ids = get_favorited_product_ids(request)

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'favorited_product_ids': favorited_product_ids,  # Context e add kora holo
    }
    return render(request, 'home.html', context)


def filter_products_ajax(request, slug=None):
    """AJAX endpoint — page reload chara category onujayi product grid filter kore"""
    products_qs = Product.objects.select_related('category').prefetch_related('variants').filter(
        is_active=True
    ).annotate(
        starting_price=Min('variants__price')
    ).order_by('-id')

    if slug:
        products_qs = products_qs.filter(category__slug=slug)

    products = products_qs[:8]

    # AJAX theke asha list-er jonno abar favorite id fetch korte hobe
    favorited_product_ids = get_favorited_product_ids(request)

    # request=request pass kora important jate template request object pay
    html = render_to_string('product_grid.html', {
        'featured_products': products,
        'favorited_product_ids': favorited_product_ids, # Context e add kora holo
    }, request=request)
    
    return JsonResponse({'html': html})