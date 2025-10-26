# tenancy/shop_manager.py
from django.db import connections
from django.core.management import call_command

def create_shop_schema(tenant, schema_name):
    """
    Create a schema in the tenant DB and run migrations that will create the shop tables in that schema.
    """
    alias = tenant.db_alias
    conn = connections[alias]
    with conn.cursor() as cur:
        # Create the schema if not exists
        cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
        # Optionally grant privileges, set owner etc.

        # Set the search_path to the new schema + public to ensure migrations create tables in schema
        cur.execute(f'SET search_path TO "{schema_name}", public;')

    # Now run migrations for shop_core app to create tables in that schema.
    # We call migrate with the tenant DB configured. The router allows migrating shop_core in tenant DB.
    # IMPORTANT: Ensure connection uses search_path by forcing a connection open where SET search_path executed
    call_command("migrate", database=alias, app_label="shop_core", verbosity=1)
