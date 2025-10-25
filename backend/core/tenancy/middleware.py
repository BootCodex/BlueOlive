# tenancy/middleware.py
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseForbidden
from django.db import connections
from tenancy.tenant_context import set_current_tenant, set_current_shop, clear_current
from tenancy.models import Tenant

class TenantMiddleware(MiddlewareMixin):
    """
    1) Identify tenant from request (subdomain / header / api key)
    2) Set thread-local tenant
    3) Ensure tenant connection is registered in settings.connections (register dynamically if missing)
    4) Optionally set shop schema based on request (header or URL)
    5) Set search_path for the tenant DB connection to the requested schema
    """
    def process_request(self, request):
        host = request.get_host().split(":")[0]
        # Example: tenant is subdomain
        # extract subdomain e.g. tenant1.example.com -> tenant1
        parts = host.split(".")
        subdomain = parts[0] if len(parts) > 2 else None

        # Or use header: X-Tenant or Authorization token
        tenant_key = request.headers.get("X-Tenant") or subdomain
        if not tenant_key:
            # If you allow public endpoints, skip; else block
            return HttpResponseForbidden("Tenant not specified")

        try:
            tenant = Tenant.objects.get(slug=tenant_key)
        except Tenant.DoesNotExist:
            return HttpResponseForbidden("Invalid tenant")

        # register tenant in thread-local
        set_current_tenant(tenant)

        # Ensure connections registered (register_tenant_connection may be called on creation)
        from tenancy.utils import register_tenant_connection
        register_tenant_connection(tenant)

        # Determine shop schema: from header or path
        shop_schema = request.headers.get("X-Shop-Schema")  # e.g. 'shop_123'
        if not shop_schema:
            # Could fallback to default shop
            shop_schema = "public"  # or tenant default
        set_current_shop(shop_schema)

        # Set search_path for this tenant DB connection immediately
        alias = tenant.db_alias
        conn = connections[alias]
        # If connection isn't established yet, Django will connect on first use;
        # but we can force a cursor and set search_path now.
        with conn.cursor() as cur:
            cur.execute(f'SET search_path TO "{shop_schema}", public;')

    def process_response(self, request, response):
        clear_current()
        return response
