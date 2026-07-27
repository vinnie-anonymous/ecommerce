# apps/users/views.py (or create a separate dashboard app)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from apps.products.models import Product, Category
from apps.products.forms import ProductForm, ProductImageForm
from apps.orders.models import Order

def is_seller(user):
    """Check if user is a seller/admin"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(is_seller)
def dashboard_home(request):
    """Seller dashboard home"""
    # Dashboard statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()
    total_products = Product.objects.count()
    low_stock_products = Product.objects.filter(stock__lt=10, is_active=True)
    total_revenue = Order.objects.filter(payment_status='completed').aggregate(total=Sum('total'))['total'] or 0
    
    # Recent orders
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    # Monthly revenue
    thirty_days_ago = timezone.now() - timedelta(days=30)
    monthly_revenue = Order.objects.filter(
        payment_status='completed',
        created_at__gte=thirty_days_ago
    ).aggregate(total=Sum('total'))['total'] or 0
    
    context = {
        'revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'low_stock_products': low_stock_products,
        'total_revenue': total_revenue,
        'monthly_revenue': monthly_revenue,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
@user_passes_test(is_seller)
def product_list_dashboard(request):
    """List products for seller dashboard"""
    products = Product.objects.all().order_by('-created_at')
    
    if request.GET.get('search'):
        search = request.GET['search']
        products = products.filter(name__icontains=search)
    
    if request.GET.get('category'):
        products = products.filter(category_id=request.GET['category'])
    
    categories = Category.objects.all()
    
    return render(request, 'dashboard/product_list.html', {
        'products': products,
        'categories': categories,
        'search': request.GET.get('search', ''),
    })

@login_required
@user_passes_test(is_seller)
def product_create_dashboard(request):
    """Create product from dashboard"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('dashboard:product_detail', product_id=product.id)
    else:
        form = ProductForm()
    
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
@user_passes_test(is_seller)
def product_update_dashboard(request, product_id):
    """Update product from dashboard"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('dashboard:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'dashboard/product_form.html', {
        'form': form,
        'title': 'Edit Product',
        'product': product
    })

@login_required
@user_passes_test(is_seller)
def product_detail_dashboard(request, product_id):
    """View product details in dashboard"""
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'dashboard/product_detail.html', {'product': product})

@login_required
@user_passes_test(is_seller)
def product_delete_dashboard(request, product_id):
    """Delete product from dashboard"""
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" deleted successfully!')
        return redirect('dashboard:product_list')
    
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})

@login_required
@user_passes_test(is_seller)
def order_list_dashboard(request):
    """List all orders in dashboard"""
    orders = Order.objects.all().order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Filter by date
    date_filter = request.GET.get('date_filter')
    if date_filter:
        if date_filter == 'today':
            orders = orders.filter(created_at__date=timezone.now().date())
        elif date_filter == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            orders = orders.filter(created_at__gte=week_ago)
        elif date_filter == 'month':
            month_ago = timezone.now() - timedelta(days=30)
            orders = orders.filter(created_at__gte=month_ago)
    
    status_choices = Order.STATUS_CHOICES
    
    return render(request, 'dashboard/order_list.html', {
        'orders': orders,
        'status_choices': status_choices,
        'current_status': status,
        'date_filter': date_filter,
    })

@login_required
@user_passes_test(is_seller)
def order_detail_dashboard(request, order_id):
    """View order details in dashboard"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order status updated to {order.get_status_display()}')
            return redirect('dashboard:order_detail', order_id=order.id)
    
    return render(request, 'dashboard/order_detail.html', {'order': order})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('products:product_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('products:product_list')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})