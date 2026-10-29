"""Staff invite-by-email flow (Phase 4G Slice 5)."""

from __future__ import annotations

import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import StaffInvite, StaffProfile
from .staff_audit_service import record_staff_audit_event
from .staff_constants import StaffAuditEventType, StaffRole
from .staff_service import create_staff_user, require_can_manage_staff


def _invite_ttl_days() -> int:
    return int(getattr(settings, 'STAFF_INVITE_TTL_DAYS', 7))


def _invite_web_base_url() -> str:
    return getattr(settings, 'STAFF_INVITE_WEB_BASE_URL', 'https://www.buynhaul.com').rstrip('/')


def build_staff_invite_url(token: str) -> str:
    return f'{_invite_web_base_url()}/?staff_invite={token}'


def pending_invite_queryset():
    now = timezone.now()
    return StaffInvite.objects.filter(accepted_at__isnull=True, expires_at__gt=now)


@transaction.atomic
def create_staff_invite(
    actor: User,
    *,
    email: str,
    staff_role: str,
    first_name: str = '',
    last_name: str = '',
) -> StaffInvite:
    require_can_manage_staff(actor)

    normalized_email = email.strip().lower()
    if staff_role not in StaffRole.values:
        raise ValidationError({'staff_role': 'Invalid staff role.'})
    if User.objects.filter(email__iexact=normalized_email).exists():
        raise ValidationError({'email': 'This email is already registered.'})
    if pending_invite_queryset().filter(email__iexact=normalized_email).exists():
        raise ValidationError({'email': 'A pending invite already exists for this email.'})

    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(days=_invite_ttl_days())
    invite = StaffInvite.objects.create(
        token=token,
        email=normalized_email,
        staff_role=staff_role,
        first_name=(first_name or '').strip(),
        last_name=(last_name or '').strip(),
        invited_by=actor,
        expires_at=expires_at,
    )

    invite_url = build_staff_invite_url(token)
    send_mail(
        subject='BuyNHaul staff invitation',
        message=(
            f'You have been invited to join BuyNHaul as staff ({staff_role}).\n\n'
            f'Open this link to set your username and password (expires in {_invite_ttl_days()} days):\n'
            f'{invite_url}\n'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[normalized_email],
        fail_silently=False,
    )

    record_staff_audit_event(
        actor=actor,
        event_type=StaffAuditEventType.INVITE_SENT,
        target_email=normalized_email,
        new_role=staff_role,
        detail=f'Invite expires {expires_at.isoformat()}',
    )
    return invite


def get_valid_invite_for_token(token: str) -> StaffInvite:
    normalized = (token or '').strip()
    if not normalized:
        raise ValidationError({'token': 'Invite token is required.'})
    try:
        invite = StaffInvite.objects.get(token=normalized)
    except StaffInvite.DoesNotExist as exc:
        raise ValidationError({'token': 'Invalid or expired invite.'}) from exc
    if invite.accepted_at is not None:
        raise ValidationError({'token': 'This invite has already been used.'})
    if invite.expires_at <= timezone.now():
        raise ValidationError({'token': 'This invite has expired.'})
    return invite


@transaction.atomic
def accept_staff_invite(
    *,
    token: str,
    username: str,
    password: str,
    first_name: str = '',
    last_name: str = '',
) -> StaffProfile:
    invite = get_valid_invite_for_token(token)

    resolved_first = (first_name or invite.first_name or '').strip()
    resolved_last = (last_name or invite.last_name or '').strip()
    if not resolved_first or not resolved_last:
        raise ValidationError({'first_name': 'First and last name are required.'})

    actor = invite.invited_by
    if actor is None:
        actor = User.objects.filter(is_superuser=True, is_active=True).order_by('id').first()

    profile = create_staff_user(
        actor,
        username=username.strip(),
        email=invite.email,
        password=password,
        first_name=resolved_first,
        last_name=resolved_last,
        staff_role=invite.staff_role,
    )

    invite.accepted_at = timezone.now()
    invite.accepted_profile = profile
    invite.save(update_fields=['accepted_at', 'accepted_profile'])

    record_staff_audit_event(
        actor=actor,
        event_type=StaffAuditEventType.INVITE_ACCEPTED,
        target_profile=profile,
        target_email=invite.email,
        new_role=invite.staff_role,
        detail=f'Invite accepted by {profile.user.username}',
    )
    return profile
