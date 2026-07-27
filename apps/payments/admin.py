from django.contrib import admin
from .models import PaymentTransaction


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'order', 'amount', 'phone_number', 'status', 'created_at')
    list_filter = ('status',)
