"""
SaaS Admin — Provisioning Health

Tenant/shop signup runs async (tenancy/tasks.py): DB creation, schema
migration, addon provisioning. Tenant.setup_status / Shop.setup_status
already track pending -> db_ready -> ready -> failed, and a periodic sweep
(sweep_stuck_tenant_provisioning) re-queues anything stuck in 'pending' past
10 minutes - but until now nothing surfaced this outside Celery worker logs,
so a stuck or failed signup was invisible to the platform owner. This adds
read visibility plus a manual "retry now" action equivalent to what the
sweep already does automatically, just on demand.

Retrying complete_tenant_signup_async (the stage that creates the default
shop + admin user) is deliberately NOT exposed here: it needs the original
admin_password_hash, which is never persisted anywhere (see that task's
docstring) - there is no safe way to replay it from stored state. A tenant
stuck 'failed' after its database is already ready needs the platform owner
to finish setup manually via the existing tenant detail page (New Shop / New
Admin buttons), not an automatic retry.
"""

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response
from tenancy.models import Shop, Tenant
from tenancy.tasks import setup_shop_schema_async, setup_tenant_database_async

from .auth import PlatformOwnerJWTAuthentication
from .permissions import IsPlatformSuperuser


def _tenant_payload(tenant):
    return {
        "id": tenant.id,
        "name": tenant.name,
        "slug": tenant.slug,
        "setup_status": tenant.setup_status,
        "setup_error": tenant.setup_error,
        "created_at": tenant.created_at,
        "minutes_since_created": int(
            (timezone.now() - tenant.created_at).total_seconds() // 60
        ),
    }


def _shop_payload(shop):
    return {
        "id": shop.id,
        "name": shop.name,
        "tenant_id": shop.tenant_id,
        "tenant_name": shop.tenant.name,
        "setup_status": shop.setup_status,
        "setup_error": shop.setup_error,
        "created_at": shop.created_at,
        "minutes_since_created": int(
            (timezone.now() - shop.created_at).total_seconds() // 60
        ),
    }


@api_view(["GET"])
@authentication_classes([PlatformOwnerJWTAuthentication])
@permission_classes([IsPlatformSuperuser])
def provisioning_health(request):
    """
    List every tenant/shop not yet in 'ready' state, most-stuck first.
    Distinct from TenantStatsViewSet.overview - this is about provisioning
    *problems*, not overall counts.
    """
    tenants = Tenant.objects.exclude(setup_status="ready").order_by("created_at")
    shops = (
        Shop.objects.exclude(setup_status="ready")
        .select_related("tenant")
        .order_by("created_at")
    )

    return Response(
        {
            "tenants": [_tenant_payload(t) for t in tenants],
            "shops": [_shop_payload(s) for s in shops],
        }
    )


@api_view(["POST"])
@authentication_classes([PlatformOwnerJWTAuthentication])
@permission_classes([IsPlatformSuperuser])
def retry_tenant_provisioning(request, tenant_id):
    """
    Re-run database provisioning for a tenant stuck in 'pending' or 'failed'.
    Idempotent (see setup_tenant_database_async docstring), so safe to fire
    on demand rather than waiting for the periodic sweep.
    """
    try:
        tenant = Tenant.objects.get(id=tenant_id)
    except Tenant.DoesNotExist:
        return Response({"error": "Tenant not found"}, status=status.HTTP_404_NOT_FOUND)

    tenant.setup_status = "pending"
    tenant.setup_error = ""
    tenant.save(update_fields=["setup_status", "setup_error"])
    setup_tenant_database_async.delay(tenant.id)

    return Response({"message": f"Re-queued database provisioning for {tenant.name}"})


@api_view(["POST"])
@authentication_classes([PlatformOwnerJWTAuthentication])
@permission_classes([IsPlatformSuperuser])
def retry_shop_provisioning(request, shop_id):
    """Re-run schema setup for a shop stuck in 'pending' or 'failed'."""
    try:
        shop = Shop.objects.select_related("tenant").get(id=shop_id)
    except Shop.DoesNotExist:
        return Response({"error": "Shop not found"}, status=status.HTTP_404_NOT_FOUND)

    shop.setup_status = "pending"
    shop.setup_error = ""
    shop.save(update_fields=["setup_status", "setup_error"])
    setup_shop_schema_async.delay(shop.id)

    return Response({"message": f"Re-queued schema setup for {shop.name}"})
