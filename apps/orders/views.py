# apps/orders/views.py
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from apps.cart.cart import Cart
from apps.orders.models import Order, OrderItem
from apps.orders.forms import CheckoutForm


def checkout(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.error(request, 'Your cart is empty!')
        return redirect('cart:cart_detail')

    cart_items = list(cart)

    order = Order()
    if request.user.is_authenticated:
        order.user = request.user

    if request.method == 'POST':
        form = CheckoutForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save(commit=False)
            order.order_number = f"ORD-{uuid.uuid4().hex[:10].upper()}"
            order.total = cart.get_total_price()
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    product_name=item['product'].name,
                    product_price=item['product'].price,
                    quantity=item['quantity'],
                    total_price=item['total_price'],
                )

            cart.clear()
            messages.success(request, f'Order #{order.order_number} placed!')
            return redirect('payments:mpesa_payment', order_id=order.id)

        else:
            # Show form errors in terminal for debugging
            print("Form errors:", form.errors)

    else:
        form = CheckoutForm(instance=order)

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total': cart.get_total_price(),
    })


@login_required
def order_history(request):
    orders = Order.objects.filter(
        user=request.user
    ).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.user:
        if not request.user.is_authenticated:
            raise Http404
        if request.user != order.user and not request.user.is_staff:
            raise Http404
    return render(request, 'orders/order_detail.html', {'order': order})


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_success.html', {'order': order})