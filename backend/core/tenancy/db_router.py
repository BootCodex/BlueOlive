from django.conf import settings
from tenancy.tenant_context import get_current_tenant


class TenantDatabaseRouter:
    def db_for_read(self, model, **hints):
        tenant = get_current_tenant()
        if tenant and model._meta.app_label in settings.TENANT_APPS:
            return tenant.db_alias
        return "default"

    def db_for_write(self, model, **hints):
        tenant = get_current_tenant()
        if tenant and model._meta.app_label in settings.TENANT_APPS:
            return tenant.db_alias
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # Tenant and shop apps only migrate on their specific tenant database
        if app_label in settings.TENANT_APPS or app_label in settings.SHOP_APPS:
            tenant = hints.get("tenant") or get_current_tenant()
            # Only allow if we have a specific tenant and it matches the db
            if tenant:
                return db == tenant.db_alias
            return False

        # Shared apps migrate only on default database
        if app_label in settings.SHARED_APPS:
            return db == "default"

        return db == "default"