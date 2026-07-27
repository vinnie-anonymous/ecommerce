from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # ── Auth ──────────────────────────────────────────────────────────────
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='users/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', user_views.register, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),

    # ── Specific paths FIRST (before the greedy product slug catcher) ─────
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),

    # ── Products LAST — greedy <slug:slug>/ must be the final fallback ────
    path('', include('apps.products.urls', namespace='products')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)