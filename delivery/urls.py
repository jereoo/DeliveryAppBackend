from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from delivery.views_auth import LoggingTokenObtainPairView
from delivery.views_me import CurrentUserView
from .views import (
    DeliveryViewSet, DriverViewSet, VehicleViewSet, DriverVehicleViewSet,
    DeliveryAssignmentViewSet, CustomerViewSet, LegalDocumentViewSet,
    VehicleCatalogViewSet, ComplianceAdminViewSet,
)
from .views_staff import StaffUserViewSet
from .views_staff_slice5 import StaffAuditEventViewSet, StaffInvitePublicView, StaffInviteViewSet
from .views_password_auth import ChangePasswordView, ForgotPasswordView, PasswordResetPublicView
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
router.register(r'vehicle-catalog', VehicleCatalogViewSet, basename='vehiclecatalog')
router.register(r'compliance/admin', ComplianceAdminViewSet, basename='complianceadmin')
router.register(r'staff', StaffUserViewSet, basename='staff')
router.register(r'staff-audit-events', StaffAuditEventViewSet, basename='staff-audit-events')
router.register(r'staff-invites', StaffInviteViewSet, basename='staff-invites')

urlpatterns = [
    path('token/', LoggingTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('auth/password/change/', ChangePasswordView.as_view(), name='auth-password-change'),
    path('auth/password/forgot/', ForgotPasswordView.as_view(), name='auth-password-forgot'),
    path('auth/password/reset/', PasswordResetPublicView.as_view(), name='auth-password-reset'),
    path('staff-invites/public/', StaffInvitePublicView.as_view(), name='staff-invites-public'),
]

urlpatterns += router.urls