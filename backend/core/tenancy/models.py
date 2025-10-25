# tenancy/models.py
from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    db_name = models.CharField(max_length=200)
    db_user = models.CharField(max_length=200)
    db_password = models.CharField(max_length=200)
    db_host = models.CharField(max_length=200)
    db_port = models.IntegerField(default=5432)
    created_at = models.DateTimeField(auto_now_add=True)
    tenant_control = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tenant"

    @property
    def db_alias(self):
        return f"tenant_{self.id}"

    def __str__(self):
        return self.name


class Shop(models.Model):
    """
    Represents a shop under a tenant.
    The actual shop data tables live in the tenant DB, in a schema named `schema_name`.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="shops")
    name = models.CharField(max_length=200)
    schema_name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    tenant_control = True

    class Meta:
        verbose_name = "Shop"

    def __str__(self):
        return f"{self.tenant.name} - {self.name}"
