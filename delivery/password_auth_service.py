"""Password change and reset (Phase 4G — staff-first, all User accounts)."""

from __future__ import annotations

import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import PasswordResetToken, StaffProfile
def _reset_ttl_hours() -> int:
    return int(getattr(settings, 'PASSWORD_RESET_TTL_HOURS', 24))


def _password_reset_web_base_url() -> str:
    return getattr(settings, 'STAFF_INVITE_WEB_BASE_URL', 'https://www.buynhaul.com').rstrip('/')


def build_password_reset_url(token: str) -> str:
    return f'{_password_reset_web_base_url()}/?password_reset={token}'


def generate_temporary_password(length: int = 14) -> str:
    return secrets.token_urlsafe(max(length, 12))[:length]


def staff_must_change_password(user: User) -> bool:
    if not user.is_staff:
        return False
    try:
        return bool(user.staff_profile.must_change_password)
    except StaffProfile.DoesNotExist:
        return False


def set_staff_must_change_password(profile: StaffProfile, *, required: bool) -> None:
    if profile.must_change_password != required:
        profile.must_change_password = required
        profile.save(update_fields=['must_change_password'])


@transaction.atomic
def change_password(user: User, *, current_password: str, new_password: str) -> None:
    if not user.check_password(current_password):
        raise ValidationError({'current_password': 'Current password is incorrect.'})
    if len(new_password) < 8:
        raise ValidationError({'new_password': 'Password must be at least 8 characters.'})
    if current_password == new_password:
        raise ValidationError({'new_password': 'New password must differ from the current password.'})

    user.set_password(new_password)
    user.save(update_fields=['password'])

    if user.is_staff:
        try:
            set_staff_must_change_password(user.staff_profile, required=False)
        except StaffProfile.DoesNotExist:
            pass


def request_password_reset(*, email: str) -> None:
    """Send reset email when a matching active user exists (no user enumeration in API)."""
    normalized = email.strip().lower()
    if not normalized:
        raise ValidationError({'email': 'Email is required.'})

    user = User.objects.filter(email__iexact=normalized, is_active=True).first()
    if user is None:
        return

    token = secrets.token_urlsafe(32)
    PasswordResetToken.objects.create(
        user=user,
        token=token,
        expires_at=timezone.now() + timedelta(hours=_reset_ttl_hours()),
    )
    reset_url = build_password_reset_url(token)
    send_mail(
        subject='BuyNHaul password reset',
        message=(
            'We received a request to reset your password.\n\n'
            f'Open this link to set a new password (expires in {_reset_ttl_hours()} hours):\n'
            f'{reset_url}\n\n'
            'If you did not request this, you can ignore this email.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def get_valid_password_reset_token(token: str) -> PasswordResetToken:
    normalized = (token or '').strip()
    if not normalized:
        raise ValidationError({'token': 'Reset token is required.'})
    try:
        row = PasswordResetToken.objects.select_related('user').get(token=normalized)
    except PasswordResetToken.DoesNotExist as exc:
        raise ValidationError({'token': 'Invalid or expired reset link.'}) from exc
    if row.used_at is not None:
        raise ValidationError({'token': 'This reset link has already been used.'})
    if row.expires_at <= timezone.now():
        raise ValidationError({'token': 'This reset link has expired.'})
    return row


@transaction.atomic
def reset_password_with_token(*, token: str, new_password: str) -> None:
    if len(new_password) < 8:
        raise ValidationError({'new_password': 'Password must be at least 8 characters.'})
    row = get_valid_password_reset_token(token)
    user = row.user
    user.set_password(new_password)
    user.save(update_fields=['password'])
    row.used_at = timezone.now()
    row.save(update_fields=['used_at'])
    if user.is_staff:
        try:
            set_staff_must_change_password(user.staff_profile, required=False)
        except StaffProfile.DoesNotExist:
            pass


def email_temporary_staff_password(*, user: User, temporary_password: str) -> None:
    send_mail(
        subject='BuyNHaul staff account — temporary password',
        message=(
            f'Your BuyNHaul staff account has been created.\n\n'
            f'Username: {user.username}\n'
            f'Temporary password: {temporary_password}\n\n'
            'Sign in at https://www.buynhaul.com and you will be prompted to choose a new password.\n'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
