from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenRefreshView

# Importa a view customizada da pasta api
from api.views import CustomTokenObtainPairView


def create_admin_quick(request):
    User = get_user_model()
    # Garante a busca pelo username admin
    user, _ = User.objects.get_or_create(username='admin')
    user.email = 'joyceacaciopedro2005@gmail.com'
    user.set_password('AdminRevisAI2026!')  # Redefine a senha com hash correto
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.is_verified = True
    user.save()
    return JsonResponse({"status": "Senha do Admin atualizada com sucesso!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rota usando o CustomTokenObtainPairView (posicionada antes do include('api.urls'))
    path('api/user/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/', include('api.urls')),
    path('api/setup-admin/', create_admin_quick),

    path('admin/', admin.site.urls),
    
    
]