"""
URL configuration for RevisAI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),   # login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # renovar token
]


from django.urls import path
from django.http import JsonResponse
from django.contrib.auth import get_user_model

def create_admin_quick(request):
    User = get_user_model()
    user, _ = User.objects.get_or_create(username='admin', email='joyceacaciopedro2005@gmail.com')
    user.set_password('AdminRevisAI2026!')
    user.is_staff = True
    user.is_superuser = True
    user.is_verified = True
    user.save()
    return JsonResponse({"status": "Superuser criado com sucesso na nuvem!"})

# Adiciona esta linha dentro de urlpatterns = [ ... ]
path('api/setup-admin/', create_admin_quick),