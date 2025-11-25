from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DebtorViewSet

router = DefaultRouter()
router.register(r'debtors', DebtorViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]