import os
import sys
import psycopg2
from django.conf import settings
from django.db import connections, DEFAULT_DB_ALIAS
from django.db.backends.postgresql.base import DatabaseCreation
from django.dispatch import receiver
from django.db.models.signals import post_save
from tenancy.models import Tenant


@receiver(post_save, sender=Tenant)
def create_tenant_database(sender, instance, created, **kwargs):
    """Create a new database and run migrations when a Tenant is created."""
    
    # Skip database creation during tests
    if 'test' in sys.argv or os.environ.get('DJANGO_TESTING'):
        return
    
    if not created:
        return

    tenant = instance
    
    # Validate that tenant has required fields
    if not tenant.db_name:
        print(f"Warning: Tenant {tenant.name} has no db_name, skipping database creation")
        return
    
    db_alias = tenant.db_alias

    # Step 1: Create the database
    try:
        _create_database(db_alias, tenant)
        print(f"Database created: {tenant.db_name}")
    except Exception as e:
        print(f"Error creating database: {e}")
        # Optionally: delete the tenant or mark it as failed
        tenant.delete()
        raise

    # Step 2: Add database to Django's DATABASES
    _add_database_to_settings(db_alias, tenant)
    print(f"Database added to settings: {db_alias}")

    # Step 3: Run migrations on the new database
    try:
        _run_migrations(db_alias)
        print(f"Migrations completed on: {db_alias}")
    except Exception as e:
        print(f"Error running migrations: {e}")
        # Optionally: clean up the database
        raise


def _create_database(db_alias, tenant):
    """Create a PostgreSQL database for the tenant."""
    default_db = settings.DATABASES["default"]

    # Connect to the default database to create the new one
    conn = psycopg2.connect(
        dbname=default_db["NAME"],
        user=default_db["USER"],
        password=default_db["PASSWORD"],
        host=default_db["HOST"],
        port=default_db["PORT"],
    )
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Validate db_name before creating
        if not tenant.db_name or tenant.db_name.strip() == "":
            raise ValueError(f"Invalid database name for tenant {tenant.name}")
        
        # Create the database (ignore if it already exists)
        cursor.execute(f'CREATE DATABASE "{tenant.db_name}"')
    except psycopg2.errors.DuplicateDatabase:
        print(f"Database {tenant.db_name} already exists, skipping creation")
    except Exception as e:
        print(f"Error creating database {tenant.db_name}: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _add_database_to_settings(db_alias, tenant):
    """Add the new database to Django's DATABASES setting at runtime."""
    default_db = settings.DATABASES["default"]

    settings.DATABASES[db_alias] = {
        "ENGINE": default_db["ENGINE"],
        "NAME": tenant.db_name,
        "USER": tenant.db_user or default_db["USER"],
        "PASSWORD": tenant.db_password or default_db["PASSWORD"],
        "HOST": tenant.db_host or default_db["HOST"],
        "PORT": tenant.db_port or default_db["PORT"],
        "CONN_MAX_AGE": 0,
        "OPTIONS": {},
        "TIME_ZONE": settings.TIME_ZONE,
        "AUTOCOMMIT": True,
        "ATOMIC_REQUESTS": False,
        "CONN_HEALTH_CHECKS": False,
    }

    # Register the new database connection
    connections.databases[db_alias] = settings.DATABASES[db_alias]


def _run_migrations(db_alias):
    """Run all pending migrations on the tenant database."""
    from django.core.management import call_command
    
    # Check if TENANT_APPS is defined
    tenant_apps = getattr(settings, 'TENANT_APPS', [])
    
    if not tenant_apps:
        # If no TENANT_APPS defined, run all migrations
        call_command(
            "migrate",
            database=db_alias,
            verbosity=1,
        )
    else:
        # Run migrations for tenant apps only on this database
        for app_label in tenant_apps:
            call_command(
                "migrate",
                app_label=app_label,
                database=db_alias,
                verbosity=1,
            )