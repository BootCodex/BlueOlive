# tenancy/db_router.py
from django.conf import settings
from tenancy.tenant_context import get_current_tenant

class TenantDatabaseRouter:
    """
    Routes DB operations for tenant-scoped models to the tenant database alias.
    Control (tenant) models remain on 'default'.
    Assumes tenant instance has .db_alias attribute (string).
    """

    def _tenant_db_alias(self):
        tenant = get_current_tenant()
        if tenant:
            return getattr(tenant, "db_alias", None)
        return None

    def db_for_read(self, model, **hints):
        # Ensure tenancy app models pinned to default
        if getattr(model._meta, "tenant_control", False):
            return "default"
        # If we have a tenant in context, return its alias
        alias = self._tenant_db_alias()
        return alias or "default"

    def db_for_write(self, model, **hints):
        if getattr(model._meta, "tenant_control", False):
            return "default"
        alias = self._tenant_db_alias()
        return alias or "default"

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations only inside the same database (simple policy)
        db1 = getattr(obj1._state, "db", None)
        db2 = getattr(obj2._state, "db", None)
        if db1 and db2:
            return db1 == db2
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Control app migrations -> default DB.
        Tenant DB migrations -> handled programmatically.
        """
        # Default (control) DB: allow Django core apps + tenancy
        if db == "default":
            return app_label in (
                "tenancy",
                "auth",
                "admin",
                "contenttypes",
                "sessions",
                "messages",
                "staticfiles",
            )

        # Tenant DBs (e.g. tenant_1, tenant_2): migrate tenant apps only
        if db and db.startswith("tenant_"):
            return app_label in ("shop_core",)

        return False
