# Test configuration for Django with pytest
import os
import django
from django.conf import settings
from datetime import timedelta

def pytest_configure():
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'rest_framework',
            'rest_framework_simplejwt',
            'rest_framework_simplejwt.token_blacklist',
            'delivery',
            'address_validation',
        ],
        SECRET_KEY='test-secret-key-for-pytest',
        ROOT_URLCONF='DeliveryAppBackend.urls',
        USE_TZ=True,
        REST_FRAMEWORK={
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.IsAuthenticated',
            ],
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'rest_framework_simplejwt.authentication.JWTAuthentication',
            ),
            'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
            'PAGE_SIZE': 10
        },
        SIMPLE_JWT={
            "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
            "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
            "ROTATE_REFRESH_TOKENS": True,
            "BLACKLIST_AFTER_ROTATION": True,
        },
    )
    django.setup()