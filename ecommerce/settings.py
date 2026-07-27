# ecommerce/settings.py
from decouple import config

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Allow ngrok URLs
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
# Add .ngrok.io to allowed hosts for ngrok
ALLOWED_HOSTS.extend(['.ngrok.io', '.ngrok-free.app'])

# For development, you can also use:
DEBUG = True
if DEBUG:
    ALLOWED_HOSTS = ['*']  # Allows all hosts (only for development!)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-default-key-for-development')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,*').split(',')

WSGI_APPLICATION = 'ecommerce.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
TIME_ZONE = 'Africa/Nairobi'
USE_TZ = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap4',
    'django_filters',
    'apps.products.apps.ProductsConfig',
    'apps.cart.apps.CartConfig',
    'apps.orders.apps.OrdersConfig',
    'apps.payments.apps.PaymentsConfig',
    'apps.users.apps.UsersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce.urls'

# ── Cart ──────────────────────────────────────────────────────────────────────
CART_SESSION_ID = 'cart'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'apps.cart.context_processors.cart_total',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'products:product_list'
LOGOUT_REDIRECT_URL = 'products:product_list'

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@ecommerce.com')

MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY', '')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET', '')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY', '')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE', '174379')
MPESA_ENVIRONMENT = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
MPESA_CALLBACK_URL = os.getenv(
    'MPESA_CALLBACK_URL',
    'http://127.0.0.1:8000/payments/mpesa/callback/',
)

CRISPY_TEMPLATE_PACK = 'bootstrap4'

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400

SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')

SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False') == 'True'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False') == 'True'
