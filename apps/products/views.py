# apps/products/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Product, Category
from .forms import ProductForm, ProductImageForm
from django.urls import reverse_lazy

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        category_slug = self.kwargs.get('category_slug')
        
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)
        
        # Search
        search_query = self.request.GET.get('q') or self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Filtering
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Sorting
        sort_by = self.request.GET.get('sort')
        if sort_by == 'price':
            queryset = queryset.order_by('price')
        elif sort_by == '-price':
            queryset = queryset.order_by('-price')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent=None)
        context['search_query'] = self.request.GET.get('q') or self.request.GET.get('search', '')
        context['current_category'] = self.kwargs.get('category_slug', '')
        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        # Related products (same category)
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        context['categories'] = Category.objects.filter(parent=None)
        return context