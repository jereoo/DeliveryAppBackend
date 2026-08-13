"""Staff user admin API (Phase 4G Slice 2)."""

from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import StaffProfile
from .staff_permissions import CanManageStaffUsers
from .staff_serializers import (
    StaffUserCreateSerializer,
    StaffUserSerializer,
    StaffUserUpdateSerializer,
)
from .staff_service import staff_queryset


class StaffUserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Super Admin CRUD for operational staff accounts."""

    permission_classes = [IsAuthenticated, CanManageStaffUsers]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']
    pagination_class = None

    def get_queryset(self):
        search = self.request.query_params.get('search')
        return staff_queryset(search=search)

    def get_serializer_class(self):
        if self.action == 'create':
            return StaffUserCreateSerializer
        if self.action in ('partial_update', 'update'):
            return StaffUserUpdateSerializer
        return StaffUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response(
            StaffUserSerializer(profile).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        return Response(StaffUserSerializer(profile).data)

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
