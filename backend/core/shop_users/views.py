from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from tenancy.tenant_context import get_current_tenant
from .models import ShopUser
from .serializers import ShopUserSerializer

class IsTenantUserOrSuperuser(permissions.BasePermission):
    """
    Custom permission to only allow users to access their own tenant's users,
    or superusers to access all.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Superusers can do anything
        if request.user.is_superuser:
            return True
        # For tenant users, check if they are admin
        return request.user.role == 'ADMIN'

    def has_object_permission(self, request, view, obj):
        # Superusers can access all
        if request.user.is_superuser:
            return True
        # Users can only access objects in their tenant and must be admin
        return obj.tenant == request.user.tenant and request.user.role == 'ADMIN'

class LoginView(DjangoLoginView):
    def form_valid(self, form):
        login(self.request, form.get_user())
        return JsonResponse({'message': 'Login successful'})

    def form_invalid(self, form):
        return JsonResponse({'error': 'Invalid credentials'}, status=400)

class LogoutView(DjangoLogoutView):
    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'message': 'Logout successful'})

class ShopUserViewSet(viewsets.ModelViewSet):
    serializer_class = ShopUserSerializer
    permission_classes = [IsTenantUserOrSuperuser]

    def get_queryset(self):
        """
        Return users for the current tenant, or all users if superuser
        """
        user = self.request.user
        if user.is_superuser:
            return ShopUser.objects.all()
        else:
            tenant = get_current_tenant()
            if tenant:
                return ShopUser.objects.filter(tenant=tenant)
            else:
                # Fallback: only show user's own tenant
                return ShopUser.objects.filter(tenant=user.tenant)

    def perform_create(self, serializer):
        """
        Set the tenant for new users
        """
        user = self.request.user
        if user.is_superuser:
            # Superuser can set tenant explicitly
            serializer.save()
        else:
            # Regular admin creates users in their tenant
            tenant = get_current_tenant() or user.tenant
            serializer.save(tenant=tenant)

@api_view(['GET'])
def current_user(request):
    if request.user.is_authenticated:
        return Response({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'role': request.user.role,
            'is_superuser': request.user.is_superuser,
        })
    return Response({'user': None})
