# apps/products/models.py

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:category_detail', args=[self.slug])

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('products:product_detail', args=[self.slug])
    
    def get_primary_image(self):
        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image.url
        first_image = self.images.first()
        if first_image:
            return first_image.image.url
        return '/static/images/no-image.png'
    
    def is_in_stock(self):
        return self.stock > 0
    
    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/%Y/%m/%d/')
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
    
    def save(self, *args, **kwargs):
        # If this image is primary, make all other images not primary
        if self.is_primary:
            ProductImage.objects.filter(product=self.product).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)