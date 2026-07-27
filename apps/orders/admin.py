from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'quantity', 'total_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'email', 'total', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status')
    search_fields = ('order_number', 'email', 'phone')
    inlines = [OrderItemInline]
