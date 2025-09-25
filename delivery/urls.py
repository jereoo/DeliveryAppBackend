from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import DeliveryViewSet, DriverViewSet, VehicleViewSet, DriverVehicleViewSet, DeliveryAssignmentViewSet, CustomerViewSet
from rest_framework.routers import DefaultRouter

# 20250827 updated to include JWT auth endpoints
router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'deliveries', DeliveryViewSet, basename='delivery')
router.register(r'drivers', DriverViewSet, basename='driver')
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'driver-vehicles', DriverVehicleViewSet, basename='drivervehicle')
router.register(r'assignments', DeliveryAssignmentViewSet, basename='deliveryassignment')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls