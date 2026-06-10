"""Structured logging for authentication and registration events (no passwords)."""
import logging
import uuid

logger = logging.getLogger('delivery.auth')


def assign_request_id(request):
    """Attach a request id for log correlation."""
    request_id = request.META.get('HTTP_X_REQUEST_ID') or str(uuid.uuid4())
    request.request_id = request_id
    return request_id


def _base_extra(request, event):
    return {
        'event': event,
        'request_id': getattr(request, 'request_id', None),
        'path': getattr(request, 'path', None),
        'method': getattr(request, 'method', None),
        'remote_addr': request.META.get('REMOTE_ADDR') if request else None,
    }


def log_jwt_login_failure(request, username=''):
    logger.warning(
        'JWT login failed',
        extra={
            **_base_extra(request, 'auth.login_failed'),
            'username': (username or '')[:150],
        },
    )


def log_registration_validation_failure(request, registration_type, errors):
    """Log field names only — not user-supplied values."""
    if hasattr(errors, 'keys'):
        fields = sorted(errors.keys())
    else:
        fields = []
    logger.warning(
        'Registration validation failed',
        extra={
            **_base_extra(request, 'registration.validation_failed'),
            'registration_type': registration_type,
            'fields': fields,
        },
    )
