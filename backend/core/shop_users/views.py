from rest_framework import viewsets
from .models import ShopUser
from .serializers import ShopUserSerializer

class ShopUserViewSet(viewsets.ModelViewSet):
    queryset = ShopUser.objects.all()
    serializer_class = ShopUserSerializer
