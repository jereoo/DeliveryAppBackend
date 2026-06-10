from rest_framework.exceptions import APIException
from rest_framework_simplejwt.views import TokenObtainPairView

from .auth_logging import log_jwt_login_failure


class LoggingTokenObtainPairView(TokenObtainPairView):
    """JWT token endpoint with structured logging on failed login."""

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except APIException:
            log_jwt_login_failure(request, request.data.get('username', ''))
            raise
