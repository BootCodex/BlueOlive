from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopUserViewSet

router = DefaultRouter()
router.register(r'users', ShopUserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]