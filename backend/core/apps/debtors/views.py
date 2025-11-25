from rest_framework import viewsets
from .models import Debtor
from .serializers import DebtorSerializer

class DebtorViewSet(viewsets.ModelViewSet):
    queryset = Debtor.objects.all()
    serializer_class = DebtorSerializer
