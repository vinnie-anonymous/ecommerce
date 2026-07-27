"""
Seller Dashboard Views
─────────────────────────────────────────────────────────────────────────────
All views here are staff-only (is_staff=True).
This is a CUSTOM dashboard at /dashboard/ — not the Django /admin/ panel.

dashboard_home      – overview stats: revenue, orders, products
product_list        – list all products with edit/delete
product_create      – add new product + images
product_edit        – edit existing product
product_delete      – delete product
order_list          – all orders with filters by status
order_detail        – view single order + update status
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Q
from apps.orders.models import Order, OrderItem
from apps.products.models import Product, Category, ProductImage
from apps.dashboard.forms import ProductForm, ProductImageFormSet, OrderStatusForm
from .forms import ProductForm, ProductImageFormSet, OrderStatusForm

# ── Access Control ──────────────────────────────────────────────────────────

def staff_required(view_func):
    """Decorator: redirects non-staff users to login."""
    decorated = user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='/accounts/login/'
    )(view_func)
    return login_required(decorated)


# ── Dashboard Home ──────────────────────────────────────────────────────────

@staff_required
def dashboard_home(request):
    """Overview with key metrics."""
    total_orders   = Order.objects.count()
    pending_orders = Order.objects.filter(status=Order.Status.PENDING).count()
    paid_orders    = Order.objects.filter(status=Order.Status.PAID).count()

    # Revenue = sum of (price × quantity) for all paid orders
    revenue = OrderItem.objects.filter(
        order__status__in=[Order.Status.PAID, Order.Status.SHIPPED, Order.Status.DELIVERED]
    ).aggregate(
        total=Sum(models_expr := None)  # see below
    )

    # Cleaner revenue calculation
    from django.db.models import F, ExpressionWrapper, DecimalField
    revenue = OrderItem.objects.filter(
        order__status__in=['paid', 'shipped', 'delivered']
    ).annotate(
        line_total=ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField())
    ).aggregate(total=Sum('line_total'))['total'] or 0

    low_stock_products = Product.objects.filter(stock__lte=5, is_active=True)
    recent_orders = Order.objects.select_related('user').prefetch_related('items')[:10]

    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'paid_orders': paid_orders,
        'revenue': revenue,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/home.html', context)


# ── Product Management ──────────────────────────────────────────────────────

@staff_required
def product_list(request):
    products = Product.objects.select_related('category').prefetch_related('images')
    search = request.GET.get('search', '')
    if search:
        products = products.filter(Q(name__icontains=search))
    context = {'products': products, 'search': search}
    return render(request, 'dashboard/product_list.html', context)


@staff_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            product = form.save()
            formset.instance = product
            formset.save()
            messages.success(request, f'Product "{product.name}" created.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm()
        formset = ProductImageFormSet()
    return render(request, 'dashboard/product_form.html', {
        'form': form, 'formset': formset, 'action': 'Create'
    })


@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, f'"{product.name}" updated.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)
    return render(request, 'dashboard/product_form.html', {
        'form': form, 'formset': formset, 'action': 'Edit', 'product': product
    })


@staff_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" deleted.')
        return redirect('dashboard:product_list')
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})


# ── Order Management ────────────────────────────────────────────────────────

@staff_required
def order_list(request):
    orders = Order.objects.select_related('user').prefetch_related('items')
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)
    context = {
        'orders': orders,
        'status_filter': status_filter,
        'status_choices': Order.Status.choices,
    }
    return render(request, 'dashboard/order_list.html', context)


@staff_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), pk=pk)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, f'Order #{order.pk} status updated.')
            return redirect('dashboard:order_detail', pk=order.pk)
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'dashboard/order_detail.html', {'order': order, 'form': form})