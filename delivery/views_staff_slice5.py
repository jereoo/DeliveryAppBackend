"""Staff audit log and invite API (Phase 4G Slice 5)."""

from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .staff_audit_service import audit_queryset
from .models import StaffInvite
from .staff_invite_service import (
    accept_staff_invite,
    get_valid_invite_for_token,
    pending_invite_queryset,
)
from .staff_permissions import CanManageStaffUsers
from .staff_slice5_serializers import (
    StaffAuditEventSerializer,
    StaffInviteAcceptSerializer,
    StaffInviteCreateSerializer,
    StaffInviteSerializer,
    StaffInviteValidateSerializer,
)


class StaffAuditEventViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated, CanManageStaffUsers]
    serializer_class = StaffAuditEventSerializer
    pagination_class = None

    def get_queryset(self):
        return audit_queryset(limit=200)


class StaffInviteViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, CanManageStaffUsers]
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'create':
            return StaffInviteCreateSerializer
        return StaffInviteSerializer

    def get_queryset(self):
        if self.request.query_params.get('pending') == '1':
            return pending_invite_queryset().select_related('invited_by', 'accepted_profile')
        return StaffInvite.objects.select_related(
            'invited_by',
            'accepted_profile',
        ).order_by('-created_at')[:100]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invite = serializer.save()
        return Response(
            StaffInviteSerializer(invite).data,
            status=status.HTTP_201_CREATED,
        )


class StaffInvitePublicView(APIView):
    """Public invite validate + accept (no JWT)."""

    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get('token', '')
        try:
            invite = get_valid_invite_for_token(token)
        except ValidationError as exc:
            return Response({'valid': False, **exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        payload = StaffInviteValidateSerializer(invite).data
        payload['valid'] = True
        return Response(payload)

    def post(self, request):
        serializer = StaffInviteAcceptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = accept_staff_invite(**serializer.validated_data)
        return Response(
            {
                'username': profile.user.username,
                'staff_role': profile.staff_role,
            },
            status=status.HTTP_201_CREATED,
        )
