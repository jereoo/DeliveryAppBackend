from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import DeliveryViewSet
from rest_framework.routers import DefaultRouter

# 20250827 updated to include JWT auth endpoints
router = DefaultRouter()
router.register(r'deliveries', DeliveryViewSet, basename='delivery')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls