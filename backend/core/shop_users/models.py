from django.db import models
from django.contrib.auth.models import AbstractUser

class ShopUser(AbstractUser):
    # Additional fields if needed
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        swappable = 'AUTH_USER_MODEL'  # If making it the default user, but since tenant-scoped, maybe not

    # But since it's tenant DB, and we want per-tenant users, this is fine.
    # Note: Django's auth is in default DB, so this might conflict.
    # For simplicity, make it a separate model, not extending AbstractUser.

# Alternative: Don't extend AbstractUser, as auth is in default.
class ShopUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
