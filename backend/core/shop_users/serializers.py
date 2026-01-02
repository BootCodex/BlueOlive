from rest_framework import serializers
from .models import ShopUser

class ShopUserSerializer(serializers.ModelSerializer):
    shop_name = serializers.CharField(source='shop.name', read_only=True)

    class Meta:
        model = ShopUser
        fields = '__all__'
        read_only_fields = ['tenant']  # Tenant is set automatically

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and not request.user.is_superuser:
            self.fields.pop('tenant', None)
            # For non-admins, limit shop choices to tenant's shops
            if hasattr(request.user, 'tenant') and request.user.tenant:
                self.fields['shop'].queryset = request.user.tenant.shops.all()