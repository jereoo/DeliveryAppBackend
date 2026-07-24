"""DRF permissions for legal document compliance (Phase 4A)."""

from rest_framework.permissions import BasePermission, IsAuthenticated

from . import compliance_service


class IsStaffOrDocumentOwner(BasePermission):
    """Staff or driver who owns the document subject."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return compliance_service.user_can_access_document(request.user, obj)


class CanVerifyLegalDocument(BasePermission):
    """Admin verify/reject actions."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class CanManageDriverDocuments(BasePermission):
    """Staff or driver accessing their own driver record."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return compliance_service.user_can_access_driver(request.user, obj)


class CanManageVehicleDocuments(BasePermission):
    """Staff or driver with assigned vehicle."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return compliance_service.user_can_access_vehicle(request.user, obj)


class IsStaffUser(BasePermission):
    """Staff-only admin compliance ops (Phase 4D)."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
