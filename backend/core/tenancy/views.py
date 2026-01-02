from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Tenant, Shop
from .serializers import TenantSerializer, ShopSerializer
from tenancy.tenant_context import get_current_tenant

@api_view(['GET'])
def current_tenant(request):
    host = request.get_host().split(":")[0]
    parts = host.split(".")
    if len(parts) > 2:
        subdomain = parts[0]
    elif len(parts) == 2 and parts[1] == "localhost":
        subdomain = parts[0]
    else:
        subdomain = None

    tenant_key = request.headers.get("X-Tenant") or subdomain
    if tenant_key:
        tenant = None
        try:
            tenant = Tenant.objects.get(slug=tenant_key)
        except Tenant.DoesNotExist:
            # Try to find by shop name
            try:
                shop = Shop.objects.get(name=tenant_key)
                tenant = shop.tenant
            except Shop.DoesNotExist:
                pass
        if tenant:
            return Response({'name': tenant.name, 'slug': tenant.slug})
    return Response({'tenant': None})

@api_view(['GET'])
def tenant_shops(request):
    tenant = get_current_tenant()
    if tenant:
        shops = tenant.shops.all().values('id', 'name')
        return Response(list(shops))
    return Response([])

class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class ShopViewSet(viewsets.ModelViewSet):
    serializer_class = ShopSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        tenant = get_current_tenant()
        if tenant:
            return Shop.objects.filter(tenant=tenant)
        return Shop.objects.none()
