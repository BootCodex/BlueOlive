from django.test import TestCase, TransactionTestCase
from django.db import connections
from tenancy.models import Tenant, Shop
from django.conf import settings

class ShopSchemaCreationTest(TransactionTestCase):
    """Test that schemas are created and migrated when shops are added."""

    databases = {'default', 'tenant_1'}  # Allow connections to tenant database

    def setUp(self):
        # Create a test tenant
        self.tenant = Tenant.objects.create(
            name="Test Tenant",
            slug="test-tenant",
            db_name="test_tenant_db",
            db_user="postgres",
            db_password="0660089932@G",
            db_host="localhost",
            db_port=5432
        )

    def test_schema_creation_on_shop_save(self):
        """Test that creating a shop triggers schema creation and migration."""
        # Create a shop
        shop = Shop.objects.create(
            tenant=self.tenant,
            name="Test Shop",
            schema_name="test_shop_schema"
        )

        # Check that schema exists in the database
        db_alias = self.tenant.db_alias
        with connections[db_alias].cursor() as cursor:
            # Check if schema exists
            cursor.execute("""
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name = %s
            """, [shop.schema_name])
            result = cursor.fetchone()
            self.assertIsNotNone(result, f"Schema {shop.schema_name} was not created")

            # Check if tables were created in the schema
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_type = 'BASE TABLE'
            """, [shop.schema_name])
            tables = cursor.fetchall()
            self.assertGreater(len(tables), 0, f"No tables found in schema {shop.schema_name}")

            # Check if django_migrations table exists
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                AND table_name = 'django_migrations'
            """, [shop.schema_name])
            migrations_table = cursor.fetchone()
            self.assertIsNotNone(migrations_table, "django_migrations table not found in schema")
