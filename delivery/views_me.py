from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .me_service import resolve_current_user_role


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payload = resolve_current_user_role(request.user)
        if payload is None:
            return Response(
                {'detail': 'No application profile found for this user.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(payload)
