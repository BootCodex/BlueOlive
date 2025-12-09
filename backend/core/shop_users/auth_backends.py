from django.contrib.auth.backends import BaseBackend
from tenancy.tenant_context import get_current_tenant

class ShopUserBackend(BaseBackend):
    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        return getattr(user, 'is_active', True)
    def authenticate(self, request, username=None, password=None, **kwargs):
        tenant = get_current_tenant()
        if not tenant:
            # Allow login without tenant for superusers or admin access
            from .models import ShopUser
            try:
                user = ShopUser.objects.get(username=username, tenant__isnull=True)
                if user.check_password(password) and self.user_can_authenticate(user):
                    return user
            except ShopUser.DoesNotExist:
                return None
            return None

        from .models import ShopUser
        try:
            user = ShopUser.objects.get(username=username, tenant=tenant)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except ShopUser.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        from .models import ShopUser
        try:
            user = ShopUser.objects.get(pk=user_id)
            # If user has tenant, check current tenant matches
            if user.tenant:
                tenant = get_current_tenant()
                if not tenant or tenant != user.tenant:
                    return None
            return user if self.user_can_authenticate(user) else None
        except ShopUser.DoesNotExist:
            return None