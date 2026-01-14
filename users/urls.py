from django.urls import path
from . import views
from .health import HealthCheckView

app_name = 'users'

urlpatterns = [
    # JWT токены
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # Аутентификация
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('verify/', views.VerifyTokenView.as_view(), name='verify_token'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    
    # Профиль пользователя
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    
    # Регистрация
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # Тестовый endpoint
    path('test/', views.test_api, name='test'),
]