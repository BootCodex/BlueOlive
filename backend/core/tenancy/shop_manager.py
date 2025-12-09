# tenancy/shop_manager.py
from django.db import connections
from django.core.management import call_command
from django.apps import apps
from .tenant_context import set_current_tenant, clear_current_tenant


def create_shop_schema(tenant, schema_name):
    """
    Create a schema in the tenant DB and run migrations that will create the shop tables in that schema.
    """
    from django.conf import settings
    alias = tenant.db_alias

    try:
        # Modify database connection settings to use this schema by default BEFORE creating schema
        original_options = settings.DATABASES[alias].get('OPTIONS', {}).copy()
        settings.DATABASES[alias]['OPTIONS'] = settings.DATABASES[alias].get('OPTIONS', {}).copy()
        settings.DATABASES[alias]['OPTIONS']['options'] = f'-c search_path="{schema_name}",public'

        # Force reload of connection settings
        connections.databases[alias] = settings.DATABASES[alias].copy()

        # Close any existing connections to ensure new settings take effect
        if hasattr(connections._connections, alias):
            getattr(connections._connections, alias).close()
            delattr(connections._connections, alias)

        conn = connections[alias]

        # Create the schema
        with conn.cursor() as cur:
            cur.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')
            print(f"Schema '{schema_name}' created")

            # Create django_migrations table in this schema (search_path should be set by connection options)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS django_migrations (
                    id SERIAL PRIMARY KEY,
                    app VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    applied TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)
            print(f"Migration tracking table created in schema '{schema_name}'")

        # Set current tenant so router allows migration of shop apps
        set_current_tenant(tenant)

        try:
            # Run migrations for shop apps
            for app_name in settings.SHOP_APPS:
                app_label = app_name.split('.')[-1]

                try:
                    app_config = apps.get_app_config(app_label)
                    print(f"Migrating {app_config.label} to schema {schema_name}...")

                    # Verify connection settings before migration
                    test_conn = connections[alias]
                    with test_conn.cursor() as cur:
                        cur.execute("SHOW search_path")
                        sp = cur.fetchone()
                        print(f"  search_path before migration: {sp[0]}")

                    call_command("migrate", app_config.label, database=alias, verbosity=1)

                except LookupError:
                    print(f"Warning: App '{app_name}' not found in installed apps")

            # Verify tables were created
            with connections[alias].cursor() as cur:
                cur.execute(f'SET search_path TO "{schema_name}"')  # Set to shop schema to check
                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """, [schema_name])
                tables = cur.fetchall()

                if tables:
                    print(f"Tables created in schema '{schema_name}':")
                    for table in tables:
                        print(f"  - {table[0]}")
                else:
                    print(f"WARNING: No tables found in schema '{schema_name}'!")

                    # Debug: Check what tables exist in the database
                    cur.execute("SHOW search_path")
                    current_sp = cur.fetchone()
                    print(f"Current search_path: {current_sp[0]}")

                    cur.execute("""
                        SELECT schemaname, tablename
                        FROM pg_tables
                        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                        ORDER BY schemaname, tablename
                    """)
                    all_tables = cur.fetchall()
                    print("All tables in database:")
                    for schema, table in all_tables:
                        print(f"  {schema}.{table}")

        finally:
            clear_current_tenant()

            # Close connection before restoring settings
            connections[alias].close()
            if hasattr(connections._connections, alias):
                delattr(connections._connections, alias)

            # Restore original database options
            if original_options:
                settings.DATABASES[alias]['OPTIONS'] = original_options
            else:
                settings.DATABASES[alias].pop('OPTIONS', None)

            # Force reload with original settings
            connections.databases[alias] = settings.DATABASES[alias].copy()

    except Exception as e:
        print(f"Error creating schema {schema_name}: {e}")
        import traceback
        traceback.print_exc()
        raise