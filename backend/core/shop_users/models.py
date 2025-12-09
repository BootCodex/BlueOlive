from django.db import models
from django.contrib.auth.models import AbstractUser
from tenancy.models import Tenant

class ShopUser(AbstractUser):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.username
