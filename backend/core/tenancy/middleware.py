# # tenancy/middleware.py
# import logging
# from django.http import HttpResponseForbidden
# from django.db import connections
# from tenancy.tenant_context import set_current_tenant, set_current_shop, clear_current
# from tenancy.models import Tenant, Shop

# logger = logging.getLogger(__name__)

# class TenantMiddleware:
#     """
#     1) Identify tenant from request (subdomain / header / api key)
#     2) Set thread-local tenant
#     3) Ensure tenant connection is registered in settings.connections (register dynamically if missing)
#     4) Optionally set shop schema based on request (header or URL)
#     5) Set search_path for the tenant DB connection to the requested schema
#     """
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Allow public endpoints without tenant check
#         public_paths = ['/admin', '/favicon.ico', '/api/tenants/', '/api/current_tenant/']
#         if (request.path == '/' or any(request.path.startswith(path) for path in public_paths)) and not request.path.startswith('/api/login/'):
#             logger.debug(f"Skipping tenant middleware for public path: {request.path}")
#             response = self.get_response(request)
#             clear_current()
#             return response

#         # Log tenant setting for login requests
#         if request.path.startswith('/api/login/'):
#             logger.info(f"Processing login request for path: {request.path}, host: {request.get_host()}")

#         host = request.get_host().split(":")[0]
#         # Example: tenant is subdomain
#         # extract subdomain e.g. tenant1.example.com -> tenant1
#         # Also support localhost: tenant.localhost -> tenant
#         parts = host.split(".")
#         if len(parts) > 2:
#             subdomain = parts[0]
#         elif len(parts) == 2 and parts[1] == "localhost":
#             subdomain = parts[0]
#         else:
#             subdomain = None

#         # Or use header: X-Tenant or Authorization token
#         tenant_key = request.headers.get("X-Tenant") or subdomain
#         if not tenant_key:
#             # If you allow public endpoints, skip; else block
#             logger.warning(f"No tenant specified for path: {request.path}")
#             return HttpResponseForbidden("Tenant not specified")

#         tenant = None
#         try:
#             tenant = Tenant.objects.get(subdomain=tenant_key)
#             logger.info(f"Resolved tenant: {tenant.name} for subdomain: {tenant_key}")
#         except Tenant.DoesNotExist:
#             logger.warning(f"Invalid subdomain: {tenant_key}")
#             return HttpResponseForbidden("Invalid subdomain")

#         # register tenant in thread-local
#         set_current_tenant(tenant)
#         logger.info(f"Set current tenant: {tenant.name} (id={tenant.id}) for request path: {request.path}")

#         # Ensure connections registered (register_tenant_connection may be called on creation)
#         from tenancy.utils import register_tenant_connection
#         register_tenant_connection(tenant)

#         # Determine shop schema: from user, header, or default
#         shop_schema = None
#         if hasattr(request, 'user') and request.user.is_authenticated and request.user.shop:
#             # Use user's assigned shop
#             shop_schema = request.user.shop.schema_name
#         if not shop_schema:
#             shop_schema = request.headers.get("X-Shop-Schema")  # e.g. 'shop_123'
#         if not shop_schema:
#             # Fallback to head office shop schema
#             try:
#                 head_office = tenant.shops.get(is_head_office=True)
#                 shop_schema = head_office.schema_name
#             except Shop.DoesNotExist:
#                 shop_schema = "public"  # fallback if no head office
#         set_current_shop(shop_schema)
#         logger.info(f"Set current shop schema: {shop_schema} for request path: {request.path}")

#         # Set search_path for this tenant DB connection immediately
#         alias = tenant.db_alias
#         conn = connections[alias]
#         # If connection isn't established yet, Django will connect on first use;
#         # but we can force a cursor and set search_path now.
#         with conn.cursor() as cur:
#             cur.execute(f'SET search_path TO "{shop_schema}", public;')

#         response = self.get_response(request)
#         clear_current()
#         return response


# tenancy/middleware.py
import logging
from django.http import HttpResponseForbidden
from django.db import connections
from tenancy.tenant_context import set_current_tenant, set_current_shop, clear_current
from tenancy.models import Tenant, Shop

logger = logging.getLogger(__name__)

class TenantMiddleware:
    """
    1) Identify tenant from request (subdomain / header / api key)
    2) Identify shop from nested subdomain or header
    3) Set thread-local tenant and shop
    4) Ensure tenant connection is registered in settings.connections (register dynamically if missing)
    5) Set search_path for the tenant DB connection to the requested schema
    
    Supported formats:
    - tenant.localhost -> tenant only, uses head office shop
    - shop.tenant.localhost -> tenant and shop via nested subdomain
    - tenant.example.com -> tenant only
    - shop.tenant.example.com -> tenant and shop via nested subdomain
    - Headers: X-Tenant and X-Shop-Schema for explicit specification
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow public endpoints without tenant check
        public_paths = ['/admin', '/favicon.ico', '/api/tenants/', '/api/current_tenant/']
        if (request.path == '/' or any(request.path.startswith(path) for path in public_paths)) and not request.path.startswith('/api/login/'):
            logger.debug(f"Skipping tenant middleware for public path: {request.path}")
            response = self.get_response(request)
            clear_current()
            return response

        # Log tenant setting for login requests
        if request.path.startswith('/api/login/'):
            logger.info(f"Processing login request for path: {request.path}, host: {request.get_host()}")

        host = request.get_host().split(":")[0]
        
        # Parse subdomain(s) to extract tenant and optionally shop
        tenant_key, shop_subdomain = self._parse_subdomains(host)
        
        # Allow header override for tenant
        tenant_key = request.headers.get("X-Tenant") or tenant_key
        
        if not tenant_key:
            logger.warning(f"No tenant specified for path: {request.path}")
            return HttpResponseForbidden("Tenant not specified")

        # Resolve tenant
        tenant = None
        try:
            tenant = Tenant.objects.get(subdomain=tenant_key)
            logger.info(f"Resolved tenant: {tenant.name} for subdomain: {tenant_key}")
        except Tenant.DoesNotExist:
            logger.warning(f"Invalid tenant subdomain: {tenant_key}")
            return HttpResponseForbidden("Invalid tenant subdomain")

        # Register tenant in thread-local
        set_current_tenant(tenant)
        logger.info(f"Set current tenant: {tenant.name} (id={tenant.id}) for request path: {request.path}")

        # Ensure connections registered
        from tenancy.utils import register_tenant_connection
        register_tenant_connection(tenant)

        # Determine shop schema with priority:
        # 1. Authenticated user's assigned shop
        # 2. X-Shop-Schema header
        # 3. Shop subdomain from URL
        # 4. Head office (default fallback)
        shop_schema = None
        
        # Priority 1: User's assigned shop
        if hasattr(request, 'user') and request.user.is_authenticated and hasattr(request.user, 'shop') and request.user.shop:
            shop_schema = request.user.shop.schema_name
            logger.info(f"Using shop from authenticated user: {shop_schema}")
        
        # Priority 2: Header override
        if not shop_schema:
            header_shop = request.headers.get("X-Shop-Schema")
            if header_shop:
                shop_schema = header_shop
                logger.info(f"Using shop from X-Shop-Schema header: {shop_schema}")
        
        # Priority 3: Shop subdomain from URL
        if not shop_schema and shop_subdomain:
            try:
                shop = Shop.objects.get(tenant=tenant, subdomain=shop_subdomain)
                shop_schema = shop.schema_name
                logger.info(f"Resolved shop from subdomain '{shop_subdomain}': {shop_schema}")
            except Shop.DoesNotExist:
                logger.warning(f"Shop subdomain '{shop_subdomain}' not found for tenant {tenant.name}")
                # Don't fail here, fall through to head office
        
        # Priority 4: Fallback to head office
        if not shop_schema:
            try:
                head_office = tenant.shops.get(is_head_office=True)
                shop_schema = head_office.schema_name
                logger.info(f"Using head office shop: {shop_schema}")
            except Shop.DoesNotExist:
                shop_schema = "public"  # Ultimate fallback
                logger.warning(f"No head office found for tenant {tenant.name}, using 'public' schema")
        
        set_current_shop(shop_schema)
        logger.info(f"Set current shop schema: {shop_schema} for request path: {request.path}")

        # Set search_path for this tenant DB connection immediately
        alias = tenant.db_alias
        conn = connections[alias]
        # Force connection and set search_path
        with conn.cursor() as cur:
            cur.execute(f'SET search_path TO "{shop_schema}", public;')
            logger.debug(f"Set search_path to '{shop_schema}' for connection {alias}")

        response = self.get_response(request)
        clear_current()
        return response
    
    def _parse_subdomains(self, host):
        """
        Parse the host to extract tenant subdomain and optional shop subdomain.
        
        Examples:
        - localhost -> (None, None)
        - tenant.localhost -> ('tenant', None)
        - shop.tenant.localhost -> ('tenant', 'shop')
        - example.com -> (None, None)
        - tenant.example.com -> ('tenant', None)
        - shop.tenant.example.com -> ('tenant', 'shop')
        
        Returns:
            tuple: (tenant_subdomain, shop_subdomain)
        """
        parts = host.split(".")
        
        # Handle localhost scenarios
        if "localhost" in parts:
            if len(parts) == 1:
                # Just 'localhost'
                return (None, None)
            elif len(parts) == 2:
                # tenant.localhost
                return (parts[0], None)
            elif len(parts) >= 3:
                # shop.tenant.localhost (or more nested)
                # Take the rightmost subdomain as tenant, leftmost as shop
                return (parts[-2], parts[0])
        
        # Handle regular domain scenarios (example.com)
        else:
            if len(parts) <= 2:
                # example.com or just domain
                return (None, None)
            elif len(parts) == 3:
                # tenant.example.com
                return (parts[0], None)
            elif len(parts) >= 4:
                # shop.tenant.example.com (or more nested)
                # Take second-to-last subdomain as tenant, leftmost as shop
                return (parts[-3], parts[0])
        
        return (None, None)