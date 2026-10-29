"""Append-only staff audit events (Phase 4G Slice 5)."""

from django.contrib.auth.models import User

from .models import StaffAuditEvent, StaffProfile
from .staff_constants import StaffAuditEventType


def record_staff_audit_event(
    *,
    actor: User | None,
    event_type: str,
    target_profile: StaffProfile | None = None,
    target_email: str = '',
    old_role: str = '',
    new_role: str = '',
    detail: str = '',
) -> StaffAuditEvent:
    return StaffAuditEvent.objects.create(
        actor=actor,
        target_profile=target_profile,
        target_email=(target_email or '').strip(),
        event_type=event_type,
        old_role=old_role or '',
        new_role=new_role or '',
        detail=detail or '',
    )


def audit_queryset(*, limit: int = 100):
    return (
        StaffAuditEvent.objects.select_related(
            'actor',
            'target_profile',
            'target_profile__user',
        )
        .order_by('-created_at')[:limit]
    )
