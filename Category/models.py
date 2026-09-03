from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)  # Men, Women, Boy, Girl, Shoes
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    