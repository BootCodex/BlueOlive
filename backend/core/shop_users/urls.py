from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopUserViewSet, LoginView, LogoutView, current_user

router = DefaultRouter()
router.register(r'users', ShopUserViewSet, basename='shopuser')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/logout/', LogoutView.as_view(), name='api_logout'),
    path('api/current_user/', current_user, name='current_user'),
]