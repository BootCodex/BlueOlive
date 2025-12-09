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
        tenant = get_current_tenant()

        # SHOP_APPS: Allow migration when tenant context is set and db matches
        shop_app_labels = [app.split('.')[-1] for app in settings.SHOP_APPS]
        if app_label in shop_app_labels:
            if tenant and db == tenant.db_alias:
                return True
            return False

        # TENANT_APPS: Allow migration when tenant context is set and db matches
        tenant_app_labels = [app.split('.')[-1] for app in settings.TENANT_APPS]
        if app_label in tenant_app_labels:
            if tenant and db == tenant.db_alias:
                return True
            return False

        # SHARED_APPS: Only migrate on default database
        shared_app_labels = [app.split('.')[-1] for app in settings.SHARED_APPS]
        if app_label in shared_app_labels:
            return db == "default"

        # All other apps: migrate on default database only
        return db == "default"