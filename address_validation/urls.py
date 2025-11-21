"""
URL configuration for address_validation app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'validated-addresses', views.ValidatedAddressViewSet)
router.register(r'validation-logs', views.AddressValidationLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('validate/', views.ValidateAddressView.as_view(), name='validate-address'),
    path('statistics/', views.ValidationStatisticsView.as_view(), name='validation-statistics'),
]