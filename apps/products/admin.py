# apps/products/admin.py

from django.contrib import admin
from .models import Category, Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'category', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ['name']}
    inlines = [ProductImageInline]