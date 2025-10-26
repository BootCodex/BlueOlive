# tenancy/utils.py
from django.conf import settings
from django.db import connections
from django.core.management import call_command
import psycopg2
from psycopg2 import extensions
import time

def register_tenant_connection(tenant):
    alias = tenant.db_alias
    db_config = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": tenant.db_name,
        "USER": tenant.db_user,
        "PASSWORD": tenant.db_password,
        "HOST": tenant.db_host,
        "PORT": tenant.db_port,
        "CONN_MAX_AGE": 60,  # tune as needed
        "OPTIONS": {},
        "TIME_ZONE": settings.TIME_ZONE,
        "AUTOCOMMIT": True,
        "ATOMIC_REQUESTS": False,
        "CONN_HEALTH_CHECKS": False,
    }
    # Add to settings and ensure connections updated
    settings.DATABASES[alias] = db_config
    # Ensure connection handler sees it
    connections.databases[alias] = db_config

def create_tenant_database_postgres(tenant, superuser_conn_info):
    """
    Create the actual tenant database in Postgres using superuser credentials.
    superuser_conn_info: dict with host, port, dbname, user, password
    """
    # Connect with superuser to create DB/user if necessary
    dsn = (
        f"host={superuser_conn_info['host']} "
        f"port={superuser_conn_info['port']} "
        f"user={superuser_conn_info['user']} "
        f"password={superuser_conn_info['password']} "
        f"dbname=postgres"
    )
    conn = psycopg2.connect(dsn)
    try:
        conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        # Create DB
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (tenant.db_name,))
        if cur.fetchone() is None:
            cur.execute(f'CREATE DATABASE "{tenant.db_name}"')
        # Optionally create user and grant privileges
        # cur.execute("CREATE USER ...")
        # cur.execute("GRANT ALL PRIVILEGES ON DATABASE ...")
    finally:
        conn.close()
    # small sleep or verify connectable
    time.sleep(0.5)

def provision_tenant(tenant, superuser_conn_info):
    """
    1) Create database in Postgres
    2) Register the DB alias in Django settings
    3) Run migrations for 'shop_core' app into tenant DB
    """
    create_tenant_database_postgres(tenant, superuser_conn_info)
    register_tenant_connection(tenant)
    # Run migrations for tenant apps into the new DB
    call_command("migrate", database=tenant.db_alias, app_label="shop_core", verbosity=1)
    # Optionally create shared schema inside tenant DB (see shop creation)
