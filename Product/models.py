from django.db import models
from Category.models import Category


class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class AttributeType(models.Model):
    name = models.CharField(max_length=50)  # "Color", "Size"

class AttributeValue(models.Model):
    attribute_type = models.ForeignKey(AttributeType, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)  # "Red", "XL"

    def __str__(self):
        return f"{self.attribute_type.name}: {self.value}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    attributes = models.ManyToManyField(AttributeValue)  # Color=Red + Size=XL
    sku = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # variant-specific price
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='variants/', null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.sku}"