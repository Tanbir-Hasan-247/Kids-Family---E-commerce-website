from django.conf import settings
from django.db import models
from Product.models import Product


class FavoriteItem(models.Model):
    """
    Favorite/wishlist product-level e rakha hocche (variant-level na),
    karon heart icon shadharonoto size/color chara-i thake.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.CASCADE, related_name='favorites'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'], condition=models.Q(user__isnull=False),
                name='unique_favorite_per_user'
            ),
            models.UniqueConstraint(
                fields=['session_key', 'product'], condition=models.Q(session_key__isnull=False),
                name='unique_favorite_per_session'
            ),
        ]

    def __str__(self):
        owner = self.user if self.user else f"guest:{self.session_key}"
        return f"{owner} \u2665 {self.product.name}"