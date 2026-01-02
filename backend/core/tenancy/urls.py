from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantViewSet, ShopViewSet, current_tenant, tenant_shops

router = DefaultRouter()
router.register(r'tenants', TenantViewSet, basename='tenant')
router.register(r'shops', ShopViewSet, basename='shop')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/current_tenant/', current_tenant),
    path('api/tenant_shops/', tenant_shops),
]