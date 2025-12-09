# tenancy/models.py
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from .shop_manager import create_shop_schema
from .utils import register_tenant_connection

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
    is_head_office = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    tenant_control = True

    class Meta:
        verbose_name = "Shop"
        constraints = [
            models.UniqueConstraint(fields=['tenant', 'is_head_office'], condition=models.Q(is_head_office=True), name='unique_head_office_per_tenant')
        ]

    def __str__(self):
        return f"{self.tenant.name} - {self.name}"

    def save(self, *args, **kwargs):
        if self.is_head_office:
            # Ensure no other head office for this tenant
            Shop.objects.filter(tenant=self.tenant, is_head_office=True).exclude(pk=self.pk).update(is_head_office=False)
        super().save(*args, **kwargs)


@receiver(post_save, sender=Shop)
def create_shop_schema_on_save(sender, instance, created, **kwargs):
    if created:
        register_tenant_connection(instance.tenant)
        create_shop_schema(instance.tenant, instance.schema_name)
