# apps/cart/models.py

from django.db import models
from apps.products.models import Product

class CartItem:
    def __init__(self, product, quantity=1):
        self.product_id = product.id
        self.name = product.name
        self.price = float(product.price)
        self.quantity = quantity
        self.image = product.get_primary_image() if hasattr(product, 'get_primary_image') else None
        
    def get_total_price(self):
        return self.price * self.quantity

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = {}
        self.cart = cart
    
    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': 0,
                'price': str(product.price)
            }
        self.cart[product_id]['quantity'] += quantity
        self.save()
    
    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def update(self, product_id, quantity):
        product_id = str(product_id)
        if product_id in self.cart:
            if quantity > 0:
                self.cart[product_id]['quantity'] = quantity
            else:
                del self.cart[product_id]
            self.save()
    
    def save(self):
        self.session['cart'] = self.cart
        self.session.modified = True
    
    def clear(self):
        self.session['cart'] = {}
        self.session.modified = True
    
    def get_cart_items(self):
        from apps.products.models import Product
        product_ids = list(self.cart.keys())
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        cart_items = []
        for product in products:
            product_id = str(product.id)
            item = self.cart[product_id]
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'price': product.price,
                'total_price': product.price * item['quantity']
            })
        return cart_items
    
    def get_total_price(self):
        total = 0
        cart_items = self.get_cart_items()
        for item in cart_items:
            total += item['total_price']
        return total
    
    def __len__(self):
        total_quantity = 0
        for item in self.cart.values():
            total_quantity += item['quantity']
        return total_quantity