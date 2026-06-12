from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from delivery.views_auth import LoggingTokenObtainPairView
from .views import (
    DeliveryViewSet, DriverViewSet, VehicleViewSet, DriverVehicleViewSet,
    DeliveryAssignmentViewSet, CustomerViewSet, LegalDocumentViewSet,
)
from rest_framework.routers import DefaultRouter

# 20250827 updated to include JWT auth endpoints
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'deliveries', DeliveryViewSet, basename='delivery')
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'driver-vehicles', DriverVehicleViewSet, basename='drivervehicle')
router.register(r'assignments', DeliveryAssignmentViewSet, basename='deliveryassignment')
router.register(r'documents', LegalDocumentViewSet, basename='legaldocument')

urlpatterns = [
    path('token/', LoggingTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls