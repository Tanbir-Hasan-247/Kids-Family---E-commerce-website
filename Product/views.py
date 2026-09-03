from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Min, Q
from .models import Product, ProductVariant, AttributeValue
from Category.models import Category

from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse

from Wishlist.views import get_favorited_product_ids


# ==========================================
# PRODUCT LIST & SEARCH VIEW
# ==========================================
def product_list_view(request, category_slug=None):
    category = None
    categories = Category.objects.filter(parent__isnull=True).prefetch_related('children')

    products = Product.objects.filter(is_active=True).annotate(
        starting_price=Min('variants__price')
    ).order_by('-id')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(
            Q(category=category) | Q(category__parent=category)
        )

    selected_slugs = request.GET.getlist('cat')
    if selected_slugs:
        products = products.filter(category__slug__in=selected_slugs)

    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('starting_price')
    elif sort == 'price_desc':
        products = products.order_by('-starting_price')

    paginator = Paginator(products.distinct(), 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # heart icon filled/unfilled thik dekhanor jonno
    favorited_ids = get_favorited_product_ids(request)

    context = {
        'category': category,
        'categories': categories,
        'products': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_slugs': selected_slugs,
        'sort': sort,
        'favorited_ids': favorited_ids,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('product_results.html', context, request=request)
        return JsonResponse({'html': html, 'count': paginator.count})

    return render(request, 'product_list.html', context)


# ==========================================
# PRODUCT DETAIL VIEW
# ==========================================
def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    variants = product.variants.all()

    colors = AttributeValue.objects.filter(
        attribute_type__name__iexact='Color',
        productvariant__product=product
    ).distinct()

    sizes = AttributeValue.objects.filter(
        attribute_type__name__iexact='Size',
        productvariant__product=product
    ).distinct()

    default_variant = variants.first()
    favorited_ids = get_favorited_product_ids(request)

    context = {
        'product': product,
        'colors': colors,
        'sizes': sizes,
        'variant': default_variant,
        'is_favorited': product.id in favorited_ids,
    }
    return render(request, 'product_detail.html', context)


# ==========================================
# AJAX VIEW: GET VARIANT DATA
# ==========================================
def get_variant_data(request, pk):
    color_id = request.GET.get('color')
    size_id = request.GET.get('size')

    variant = ProductVariant.objects.filter(
        product_id=pk,
        attributes__id=color_id
    ).filter(
        attributes__id=size_id
    ).first()

    if not variant:
        return JsonResponse({'available': False})

    image_url = variant.image.url if variant.image else 'https://placehold.co/600x800/0b0b0b/d4af37?text=No+Image'

    return JsonResponse({
        'available': True,
        'price': str(variant.price),
        'stock': variant.stock,
        'image_url': image_url,
        'sku': variant.sku,
        'variant_id': variant.id,
    })


# views.py
from django.shortcuts import render, redirect
from .forms import ProductForm, VariantFormSet

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            formset = VariantFormSet(request.POST, request.FILES, instance=product)
            if formset.is_valid():
                formset.save()
                return redirect('product_detail', pk=product.pk)
        else:
            formset = VariantFormSet(request.POST, request.FILES)
    else:
        form = ProductForm()
        formset = VariantFormSet()

    return render(request, 'add_product.html', {
        'form': form, 'formset': formset,
    })