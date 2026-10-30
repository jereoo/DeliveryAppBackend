"""Password change and reset API."""

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .password_auth_service import (
    change_password,
    get_valid_password_reset_token,
    request_password_reset,
    reset_password_with_token,
)
from .password_auth_serializers import (
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        change_password(
            request.user,
            current_password=serializer.validated_data['current_password'],
            new_password=serializer.validated_data['new_password'],
        )
        return Response({'detail': 'Password updated.'})


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_password_reset(email=serializer.validated_data['email'])
        return Response(
            {
                'detail': (
                    'If an account exists for this email, you will receive '
                    'password reset instructions shortly.'
                ),
            },
            status=status.HTTP_200_OK,
        )


class PasswordResetPublicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get('token', '')
        try:
            get_valid_password_reset_token(token)
        except ValidationError as exc:
            return Response({'valid': False, **exc.detail}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'valid': True})

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_password_with_token(
            token=serializer.validated_data['token'],
            new_password=serializer.validated_data['new_password'],
        )
        return Response({'detail': 'Password reset.'}, status=status.HTTP_200_OK)
