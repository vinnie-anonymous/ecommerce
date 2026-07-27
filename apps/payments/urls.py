from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('mpesa/<int:order_id>/', views.mpesa_payment, name='mpesa_payment'),
    path('mpesa/callback/', views.mpesa_callback, name='mpesa_callback'),
    path('success/<int:order_id>/', views.payment_success, name='payment_success'),
]