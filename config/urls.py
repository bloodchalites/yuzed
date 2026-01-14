from django.utils import timezone
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # Добавьте эту строку!
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Swagger схема
schema_view = get_schema_view(
    openapi.Info(
        title="ЮЗЭДО API",
        default_version='v1',
        description="API для системы ЮЗЭДО",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Простой тестовый view
@api_view(['GET'])
@permission_classes([AllowAny])  # Добавьте эту строку!
def api_root(request):
    return Response({
        'message': 'Добро пожаловать в API ЮЗЭДО!',
        'version': '1.0',
        'status': 'API работает корректно',
        'server_time': timezone.now().isoformat(),
        'endpoints': {
            'admin': '/admin/',
            'api_docs': '/swagger/',
            'test_post': '/api/test/',
            'users': '/api/users/',
            'documents': '/api/documents/',
            'payments': '/api/payments/',
        }
    })

@api_view(['POST'])
@permission_classes([AllowAny])  # Добавьте эту строку!
def test_api(request):
    return Response({
        'success': True,
        'message': 'Данные успешно получены!',
        'received_data': request.data,
        'server_time': timezone.now().isoformat(),
        'status': 'API работает корректно'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/', api_root, name='api-root'),
    path('api/test/', test_api, name='test-api'),
    # Добавьте ваши приложения
    path('api/users/', include('users.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/payments/', include('payments.urls')),
]