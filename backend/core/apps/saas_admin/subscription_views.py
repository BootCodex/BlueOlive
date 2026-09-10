"""
SaaS Admin — Subscription/Billing Management API

Platform owners need to manage tenant subscription tiers, change plans,
suspend/reactivate billing, and review payment history across ALL tenants.
tenancy.views already has fully-built ModelViewSets for this
(SubscriptionPlanViewSet, SubscriptionViewSet, SubscriptionPaymentViewSet),
but they're wired up under core.urls with the DEFAULT authentication classes
(TenantJWTAuthentication + SessionAuthentication) - which only ever resolve a
user against a *tenant* database. A platform owner's ShopUser row lives only
in the `default` database (see tenancy/platform_auth.py), so their
po_access_token cookie can never authenticate against those endpoints: the
permission check (is_superuser) would pass in principle, but authentication
fails first. That leaves subscription management practically unreachable
from the owner portal even though the business logic already exists.

Rather than duplicating that logic, subclass the tenancy viewsets here and
swap in the same PlatformOwnerJWTAuthentication + IsPlatformSuperuser pair
every other saas_admin endpoint uses (see tenant_views.py, user_views.py).
This changes nothing about the original tenant-facing endpoints under
/api/v1/subscription/ - those keep their own permission classes and remain
separately registered.
"""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from tenancy.models import Subscription, SubscriptionPayment
from tenancy.views import SubscriptionPaymentViewSet as TenantSubscriptionPaymentViewSet
from tenancy.views import SubscriptionPlanViewSet as TenantSubscriptionPlanViewSet
from tenancy.views import SubscriptionViewSet as TenantSubscriptionViewSet

from .auth import PlatformOwnerJWTAuthentication
from .permissions import IsPlatformSuperuser


class PlatformSubscriptionPlanViewSet(TenantSubscriptionPlanViewSet):
    """Manage pricing tiers (SubscriptionPlan) as the platform owner."""

    authentication_classes = [PlatformOwnerJWTAuthentication]
    permission_classes = [IsPlatformSuperuser]


class PlatformSubscriptionViewSet(TenantSubscriptionViewSet):
    """
    Manage tenant subscriptions (assign/change tier, suspend, cancel, renew)
    as the platform owner. Reuses TenantSubscriptionViewSet's get_queryset(),
    which already grants unrestricted cross-tenant access when
    request.user.is_superuser - always true here since IsPlatformSuperuser
    gates every request.
    """

    authentication_classes = [PlatformOwnerJWTAuthentication]
    permission_classes = [IsPlatformSuperuser]

    @action(detail=False, methods=["get"])
    def overview(self, request):
        """Billing snapshot: subscriptions by status, MRR, revenue this month."""
        qs = Subscription.objects.select_related("plan")

        status_counts = {
            choice: qs.filter(status=choice).count()
            for choice, _ in Subscription.STATUS_CHOICES
        }

        mrr = Decimal("0")
        for sub in qs.filter(status__in=["ACTIVE", "TRIAL", "PAST_DUE"]):
            mrr += sub.plan.price * Decimal(30) / Decimal(sub.plan.billing_period_days)

        month_start = timezone.now().date().replace(day=1)
        revenue_this_month = (
            SubscriptionPayment.objects.filter(
                status="SUCCEEDED", paid_at__gte=month_start
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0")
        )

        expiring_soon = qs.filter(
            status__in=["ACTIVE", "TRIAL"],
            end_date__lte=timezone.now().date() + timedelta(days=7),
        ).count()

        return Response(
            {
                "status_counts": status_counts,
                "mrr": mrr,
                "revenue_this_month": revenue_this_month,
                "total_subscriptions": qs.count(),
                "expiring_within_7_days": expiring_soon,
            }
        )


class PlatformSubscriptionPaymentViewSet(TenantSubscriptionPaymentViewSet):
    """Review/process/refund subscription payments as the platform owner."""

    authentication_classes = [PlatformOwnerJWTAuthentication]
    permission_classes = [IsPlatformSuperuser]
