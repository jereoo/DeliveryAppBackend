"""
URL configuration for DeliveryAppBackend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include  # Add 'include' here
from django.http import JsonResponse

def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'ok',
        'message': 'DeliveryApp API is running!',
        'version': '1.0.0'
    })

urlpatterns = [
    path('', health_check, name='health_check'),  # Root URL health check
    path('admin/', admin.site.urls),
    path('api/', include('delivery.urls')),  # Include delivery app URLs
    path('api/health/', health_check, name='api_health_check'),  # API health check
    path('api/address-validation/', include('address_validation.urls')),  # Include address validation URLs
]