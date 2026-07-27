# apps/cart/context_processors.py

from .models import Cart

def cart_total(request):
    cart = Cart(request)
    return {
        'cart_total_items': len(cart),
        'cart_count': len(cart),
        'cart_total_price': cart.get_total_price(),
        'cart': cart,
    }