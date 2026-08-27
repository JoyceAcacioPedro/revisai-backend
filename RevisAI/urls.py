from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

def create_admin_quick(request):
    User = get_user_model()
    user, _ = User.objects.get_or_create(username='admin', email='joyceacaciopedro2005@gmail.com')
    user.set_password('AdminRevisAI2026!')
    user.is_staff = True
    user.is_superuser = True
    user.is_verified = True
    user.save()
    return JsonResponse({"status": "Superuser criado com sucesso na nuvem!"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    
    # Rota atualizada para bater com a chamada do Frontend (/api/user/login/)
    path('api/user/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/setup-admin/', create_admin_quick),
]