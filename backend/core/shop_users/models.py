from django.db import models
from django.contrib.auth.models import AbstractUser
from tenancy.models import Tenant
from .managers import TenantUserManager

class ShopUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STAFF = 'STAFF', 'Staff'
        MANAGER = 'MANAGER', 'Manager'
        CUSTOMER = 'CUSTOMER', 'Customer'
    
    # Override username to remove unique constraint from AbstractUser
    username = models.CharField(
        max_length=150,
        help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
    )
    
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='users', 
        null=True, 
        blank=True,
        help_text="Leave blank for superusers only"
    )
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
        help_text="User role within the tenant"
    )
    
    objects = TenantUserManager()

    class Meta:
        swappable = 'AUTH_USER_MODEL'
        unique_together = [['username', 'tenant']]
        indexes = [
            models.Index(fields=['tenant', 'role']),
            models.Index(fields=['tenant', 'username']),
        ]

    def __str__(self):
        tenant_name = self.tenant.name if self.tenant else "Global"
        return f"{self.username} ({tenant_name})"
    
    def has_role(self, role):
        """Check if user has a specific role"""
        return self.role == role
    
    def is_admin_user(self):
        """Check if user is an admin within their tenant"""
        return self.role == self.Role.ADMIN
    
    def is_staff_user(self):
        """Check if user is staff or higher"""
        return self.role in [self.Role.ADMIN, self.Role.STAFF, self.Role.MANAGER]
    
    def save(self, *args, **kwargs):
        # Ensure superusers don't have a tenant
        if self.is_superuser and self.tenant:
            self.tenant = None
        # Ensure regular users have a tenant
        elif not self.is_superuser and not self.tenant:
            raise ValueError("Regular users must belong to a tenant")
        super().save(*args, **kwargs)