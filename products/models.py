from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.urls import reverse


def product_image_path(instance, filename):
    return f'products/images/{instance.slug}/{filename}'
# Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to=product_image_path, blank=True)
    current_quantity = models.PositiveIntegerField(default=0,validators=[MinValueValidator(0)])
    critical_quantity = models.PositiveIntegerField(default=0,validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product-detail', kwargs={'slug': self.slug})

    def is_stock_critical(self):
        return 0 < self.current_quantity < self.critical_quantity