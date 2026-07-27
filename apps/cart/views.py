from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from apps.products.models import Product
from apps.cart.cart import Cart
from apps.cart.forms import CartAddProductForm


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override'],
        )
        messages.success(request, f'"{product.name}" added to your cart.')
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f'"{product.name}" removed from cart.')
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=True,
        )
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    # Attach an update form to each item for the quantity selector
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
            initial={
                'quantity': item['quantity'],
                'override': True,
            }
        )
    context = {'cart': cart}
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def cart_clear(request):
    """Empties the entire cart — used by a 'Clear Cart' button."""
    cart = Cart(request)
    cart.clear()
    messages.info(request, 'Your cart has been cleared.')
    return redirect('cart:cart_detail')