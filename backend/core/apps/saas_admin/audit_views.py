"""
SaaS Admin — Audit Log Viewer

tenancy.audit.AuditLog already records logins/failed logins, user CRUD, role
changes, cross-tenant access attempts, and superuser impersonation - but the
only consumer was Django's own /admin/ (tenancy/admin.py AuditLogAdmin,
read-only there too). This exposes the same data over the saas-admin API so
the platform-owner admin app can show it without needing Django admin access.
"""

from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.response import Response
from tenancy.audit import AuditLog
from tenancy.models import Tenant

from .auth import PlatformOwnerJWTAuthentication
from .permissions import IsPlatformSuperuser


class AuditLogSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source="get_action_display", read_only=True)
    username = serializers.SerializerMethodField()
    tenant_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "action",
            "action_display",
            "user_id",
            "username",
            "tenant_id",
            "tenant_name",
            "resource_type",
            "resource_id",
            "ip_address",
            "details",
            "success",
            "error_message",
            "timestamp",
        ]

    def get_username(self, obj):
        # log_action() always stashes the acting user's username into
        # `details` when a user was passed - see tenancy/audit.py - so this
        # avoids resolving user_id against whichever tenant DB it lives in.
        return (obj.details or {}).get("username", "")

    def get_tenant_name(self, obj):
        return self.context.get("tenant_names", {}).get(obj.tenant_id)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only, platform-superuser-only view of every AuditLog entry."""

    authentication_classes = [PlatformOwnerJWTAuthentication]
    permission_classes = [IsPlatformSuperuser]
    serializer_class = AuditLogSerializer

    def get_queryset(self):
        queryset = AuditLog.objects.all().order_by("-timestamp")

        action = self.request.query_params.get("action")
        if action:
            queryset = queryset.filter(action=action)

        tenant_id = self.request.query_params.get("tenant_id")
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)

        success = self.request.query_params.get("success")
        if success is not None:
            queryset = queryset.filter(success=success.lower() == "true")

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(resource_id__icontains=search)
                | Q(resource_type__icontains=search)
                | Q(details__username__icontains=search)
            )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        objects = page if page is not None else queryset

        tenant_ids = {obj.tenant_id for obj in objects if obj.tenant_id}
        tenant_names = dict(
            Tenant.objects.filter(id__in=tenant_ids).values_list("id", "name")
        )

        serializer = self.get_serializer(
            objects,
            many=True,
            context={**self.get_serializer_context(), "tenant_names": tenant_names},
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
