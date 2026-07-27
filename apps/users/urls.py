from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('products/', views.product_list_dashboard, name='product_list'),
    path('products/new/', views.product_create_dashboard, name='product_create'),
    path('products/<int:product_id>/', views.product_detail_dashboard, name='product_detail'),
    path('products/<int:product_id>/edit/', views.product_update_dashboard, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete_dashboard, name='product_delete'),
    path('orders/', views.order_list_dashboard, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail_dashboard, name='order_detail'),
]