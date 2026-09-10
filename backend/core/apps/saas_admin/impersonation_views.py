"""
SaaS Admin — Support Login (tenant impersonation for support)

Mints a one-time code that lets the platform owner sign into the real
tenant frontend as a chosen tenant user, for support/debugging. See
tenancy/support_login.py for the code mechanics and
shop_users/views.py:SupportLoginExchangeView for where the tenant frontend
redeems it.

Every mint is audit-logged via TenantAuditLog.log_superuser_impersonation
(action=SUPERUSER_IMPERSONATION), same as the existing (previously unused)
IsSuperUserWithImpersonation path - this is the first real caller of that
audit trail.
"""

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from shop_users.models import ShopUser
from tenancy.audit import TenantAuditLog
from tenancy.models import Tenant
from tenancy.support_login import generate_support_login_code

from .auth import PlatformOwnerJWTAuthentication
from .permissions import IsPlatformSuperuser


@api_view(["POST"])
@authentication_classes([PlatformOwnerJWTAuthentication])
@permission_classes([IsPlatformSuperuser])
def support_login(request, tenant_id):
    """
    POST /api/v1/saas-admin/tenants/{id}/support-login/
    { "user_id": <ShopUser id>, "reason": "optional" }

    Returns { "redirect_url": "..." } - open it (new tab) to land in the
    tenant frontend already signed in as that user.
    """
    try:
        tenant = Tenant.objects.get(id=tenant_id, is_active=True)
    except Tenant.DoesNotExist:
        return Response(
            {"error": "Tenant not found or inactive"}, status=status.HTTP_404_NOT_FOUND
        )

    user_id = request.data.get("user_id")
    if not user_id:
        return Response(
            {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        target_user = ShopUser.objects.using(tenant.db_alias).get(
            id=user_id, tenant_id=tenant.id, is_active=True
        )
    except ShopUser.DoesNotExist:
        return Response(
            {"error": "Active user not found in this tenant"},
            status=status.HTTP_404_NOT_FOUND,
        )

    reason = request.data.get("reason") or ""

    code = generate_support_login_code(
        tenant_id=tenant.id,
        user_id=target_user.id,
        superuser_id=request.user.id,
        superuser_username=request.user.username,
        reason=reason,
    )

    TenantAuditLog.log_superuser_impersonation(
        request=request, superuser=request.user, target_tenant=tenant, reason=reason
    )

    redirect_url = f"{settings.TENANT_FRONTEND_URL}/support-login?code={code}"
    return Response({"redirect_url": redirect_url})
