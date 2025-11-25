from rest_framework import serializers
from .models import ShopUser

class ShopUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUser
        fields = '__all__'