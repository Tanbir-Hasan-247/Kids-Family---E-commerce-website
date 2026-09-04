# forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Product, ProductVariant

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'base_price']

VariantFormSet = inlineformset_factory(
    Product, ProductVariant,
    fields=['attributes', 'sku', 'price', 'stock', 'image'],
    extra=1, can_delete=True
)