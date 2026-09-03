import os
import django
import urllib.request
import random
from django.core.files.base import ContentFile
from django.utils.text import slugify
import uuid

# Apnar project er settings module ekhane din
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kids_family.settings') 
django.setup()

# App er nam onujayi import gulo thik kore niben
from Product.models import (
Product, AttributeType, AttributeValue, ProductVariant
)
from Category.models import Category

def download_placeholder_image(text, filename):
    """Placeholder image download korar function"""
    safe_text = text.replace(' ', '+').replace('&', 'and')
    # Random background color jate variant gulo alada dekhay
    bg_color = f"{random.randint(10, 50):02x}{random.randint(10, 50):02x}{random.randint(10, 50):02x}"
    url = f"https://placehold.co/600x800/{bg_color}/d4af37/png?text={safe_text}"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        return ContentFile(response.read(), name=filename)
    except Exception as e:
        print(f"Image download failed for {text}: {e}")
        return None

def populate():
    print("Populating DB with Hierarchical Categories & M2M Attributes...\n")

    # ==========================================
    # 1. Create Categories (Hierarchical)
    # ==========================================
    # Parent Categories
    parent_kids, _ = Category.objects.get_or_create(name="Kids", defaults={"slug": "kids"})
    parent_adults, _ = Category.objects.get_or_create(name="Adults", defaults={"slug": "adults"})
    
    # Child Categories
    categories_data = [
        {"name": "Boy", "parent": parent_kids},
        {"name": "Girl", "parent": parent_kids},
        {"name": "Newborn", "parent": parent_kids},
        {"name": "Men", "parent": parent_adults},
        {"name": "Women", "parent": parent_adults},
        {"name": "Family Sets", "parent": None}, # Independent Category
    ]

    cat_objects = {}
    for cat in categories_data:
        obj, _ = Category.objects.get_or_create(
            name=cat["name"],
            defaults={"slug": slugify(cat["name"]), "parent": cat["parent"]}
        )
        cat_objects[cat["name"]] = obj
    print(f"Created Categories.")

    # ==========================================
    # 2. Create Attributes (Types & Values)
    # ==========================================
    color_type, _ = AttributeType.objects.get_or_create(name="Color")
    size_type, _ = AttributeType.objects.get_or_create(name="Size")

    colors = ["Red", "Blue", "Black", "White", "Pink", "Navy"]
    sizes = ["S", "M", "L", "XL", "2-3Y", "4-5Y", "6-12M"]

    color_attrs = []
    for c in colors:
        obj, _ = AttributeValue.objects.get_or_create(attribute_type=color_type, value=c)
        color_attrs.append(obj)

    size_attrs = []
    for s in sizes:
        obj, _ = AttributeValue.objects.get_or_create(attribute_type=size_type, value=s)
        size_attrs.append(obj)
    print(f"Created Attributes (Colors & Sizes).")

    # ==========================================
    # 3. Create Products & Variants
    # ==========================================
    products_to_create = [
        ("Boys Graphic T-Shirt", "Boy", 550),
        ("Boys Denim Casual Shirt", "Boy", 950),
        ("Girls Floral Summer Frock", "Girl", 1200),
        ("Girls Pink Party Dress", "Girl", 1800),
        ("Soft Cotton Baby Romper", "Newborn", 450),
        ("Newborn Animal Print Onesie", "Newborn", 500),
        ("Mens Classic Polo", "Men", 1100),
        ("Womens Elegant Kurti", "Women", 1500),
        ("Family Matching Christmas Pajamas", "Family Sets", 3500),
        ("King Queen Prince Combo Tee", "Family Sets", 2500),
    ]

    total_variants = 0

    for p_name, cat_name, b_price in products_to_create:
        # Create Product
        product, created = Product.objects.get_or_create(
            name=p_name,
            defaults={
                "category": cat_objects[cat_name],
                "description": f"Premium quality {p_name.lower()} tailored for ultimate comfort.",
                "base_price": b_price
            }
        )

        if created:
            # Randomly select 2 colors and 2 sizes for variants
            selected_colors = random.sample(color_attrs, 2)
            selected_sizes = random.sample(size_attrs, 2)

            for color in selected_colors:
                for size in selected_sizes:
                    # Generate SKU
                    sku = f"{slugify(p_name)[:10].upper()}-{color.value[:3].upper()}-{size.value.upper()}-{str(uuid.uuid4())[:4]}"
                    
                    # Create Variant
                    variant = ProductVariant.objects.create(
                        product=product,
                        sku=sku,
                        price=b_price + random.choice([0, 50, 100]), # Variant price can be slightly higher
                        stock=random.randint(10, 50)
                    )
                    
                    # Add ManyToMany Attributes
                    variant.attributes.add(color, size)
                    
                    # Add Image
                    img_text = f"{p_name}\n{color.value} - {size.value}"
                    img_file = download_placeholder_image(img_text, f"{sku}.png")
                    if img_file:
                        variant.image.save(f"{sku}.png", img_file, save=True)

                    total_variants += 1
            
            print(f"Created: {product.name} | Variants: {len(selected_colors) * len(selected_sizes)}")

    print(f"\n--- SUCCESS! ---")
    print(f"Total Products Checked/Created: {len(products_to_create)}")
    print(f"Total Variants Auto-Generated: {total_variants}")
    print("Database populated successfully!")

if __name__ == '__main__':
    populate()