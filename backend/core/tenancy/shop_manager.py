# tenancy/shop_manager.py
from django.db import connections
from django.core.management import call_command
from .tenant_context import set_current_tenant, clear_current_tenant

def create_shop_schema(tenant, schema_name):
    """
    Create a schema in the tenant DB and run migrations that will create the shop tables in that schema.
    """
    from django.conf import settings
    alias = tenant.db_alias

    # Temporarily set search_path in database options so all connections use it
    original_options = settings.DATABASES[alias].get('OPTIONS', {})
    settings.DATABASES[alias]['OPTIONS'] = {
        **original_options,
        'options': f'-c search_path={schema_name}'
    }
    # Update connections
    connections.databases[alias] = settings.DATABASES[alias]

    try:
        conn = connections[alias]
        with conn.cursor() as cur:
            # Create the schema if not exists
            cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')

        # Set current tenant so router allows migration of shop apps
        set_current_tenant(tenant)
        try:
            # Now run migrations for shop apps to create tables in that schema.
            for app_label in settings.SHOP_APPS:
                call_command("migrate", app_label, database=alias, verbosity=1)
        finally:
            clear_current_tenant()
    finally:
        # Restore original options
        settings.DATABASES[alias]['OPTIONS'] = original_options
        connections.databases[alias] = settings.DATABASES[alias]
