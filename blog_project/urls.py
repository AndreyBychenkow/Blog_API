"""
URL configuration for blog_project project.

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
from django.urls import path
from blog.api import api
from blog.views import index
from ninja import Router
from ninja_jwt.tokens import RefreshToken

# Создаём router для JWT аутентификации
jwt_router = Router(tags=["JWT Authentication"])

@jwt_router.post("/token/", url_name="token_obtain_pair")
def obtain_token(request, username: str, password: str):
    from django.contrib.auth import get_user_model, authenticate
    
    User = get_user_model()
    user = authenticate(username=username, password=password)
    
    if user is None:
        return {"detail": "No active account found with the given credentials"}
    
    refresh = RefreshToken.for_user(user)
    
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

@jwt_router.post("/token/refresh/", url_name="token_refresh")
def refresh_token(request, refresh: str):
    try:
        refresh_token = RefreshToken(refresh)
        return {
            "access": str(refresh_token.access_token),
        }
    except Exception:
        return {"detail": "Token is invalid or expired"}

@jwt_router.post("/token/verify/", url_name="token_verify")
def verify_token(request, token: str):
    try:
        RefreshToken(token)
        return {}
    except Exception:
        return {"detail": "Token is invalid or expired"}

# Добавляем JWT маршруты к основному API
api.add_router("/jwt", jwt_router)

urlpatterns = [
    path('', index, name='index'),
    path('admin/', admin.site.urls),
    path('api/', api.urls),
]
