"""Staff user lifecycle — create, role update, deactivate (Phase 4G Slice 2)."""

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import StaffProfile
from .staff_constants import PERM_STAFF_MANAGE, StaffRole
from .staff_permissions import user_has_staff_permission


def require_can_manage_staff(user: User) -> None:
    if not user_has_staff_permission(user, PERM_STAFF_MANAGE):
        raise PermissionDenied('Only Super Admin may manage staff users.')


def staff_queryset(*, search: str | None = None):
    qs = StaffProfile.objects.select_related('user').order_by('user__username')
    term = (search or '').strip()
    if term:
        qs = qs.filter(
            Q(user__username__icontains=term)
            | Q(user__email__icontains=term)
            | Q(user__first_name__icontains=term)
            | Q(user__last_name__icontains=term)
        )
    return qs


def _active_super_admin_count(*, exclude_profile_id: int | None = None) -> int:
    qs = StaffProfile.objects.filter(
        staff_role=StaffRole.SUPER_ADMIN,
        user__is_active=True,
    )
    if exclude_profile_id is not None:
        qs = qs.exclude(pk=exclude_profile_id)
    return qs.count()


def _ensure_super_admin_remains(profile: StaffProfile, *, demoting: bool = False, deactivating: bool = False) -> None:
    if profile.staff_role != StaffRole.SUPER_ADMIN:
        return
    if demoting or deactivating:
        if _active_super_admin_count(exclude_profile_id=profile.id) < 1:
            raise ValidationError('At least one active Super Admin is required.')


def _sync_user_superuser_flag(user: User, staff_role: str) -> None:
    is_super = staff_role == StaffRole.SUPER_ADMIN
    if user.is_superuser != is_super:
        user.is_superuser = is_super
        user.save(update_fields=['is_superuser'])


@transaction.atomic
def create_staff_user(
    actor: User,
    *,
    username: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    staff_role: str,
    job_title: str = '',
    phone_number: str = '',
) -> StaffProfile:
    require_can_manage_staff(actor)

    if staff_role not in StaffRole.values:
        raise ValidationError({'staff_role': 'Invalid staff role.'})
    if User.objects.filter(username=username).exists():
        raise ValidationError({'username': 'This username is already taken.'})
    if User.objects.filter(email=email).exists():
        raise ValidationError({'email': 'This email is already registered.'})

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_staff=True,
        is_superuser=(staff_role == StaffRole.SUPER_ADMIN),
    )
    return StaffProfile.objects.create(
        user=user,
        staff_role=staff_role,
        job_title=job_title or '',
        phone_number=phone_number or '',
    )


@transaction.atomic
def update_staff_profile(
    actor: User,
    profile: StaffProfile,
    *,
    staff_role: str | None = None,
    job_title: str | None = None,
    phone_number: str | None = None,
    is_active: bool | None = None,
) -> StaffProfile:
    require_can_manage_staff(actor)

    user = profile.user
    updates: list[str] = []

    if is_active is not None and is_active != user.is_active:
        if profile.user_id == actor.id and not is_active:
            raise ValidationError({'is_active': 'You cannot deactivate your own account.'})
        if not is_active:
            _ensure_super_admin_remains(profile, deactivating=True)
        user.is_active = is_active
        updates.append('is_active')

    if staff_role is not None and staff_role != profile.staff_role:
        if staff_role not in StaffRole.values:
            raise ValidationError({'staff_role': 'Invalid staff role.'})
        if profile.staff_role == StaffRole.SUPER_ADMIN and staff_role != StaffRole.SUPER_ADMIN:
            _ensure_super_admin_remains(profile, demoting=True)
        profile.staff_role = staff_role
        _sync_user_superuser_flag(user, staff_role)

    if job_title is not None:
        profile.job_title = job_title
    if phone_number is not None:
        profile.phone_number = phone_number

    if updates:
        user.save(update_fields=updates)
    profile.save()
    return profile
