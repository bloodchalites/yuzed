from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Client
from .serializers import (
    ClientSerializer, 
    RegisterSerializer, 
    LoginSerializer,
    get_tokens_for_user
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# Существующий тестовый endpoint
@api_view(['GET'])
@permission_classes([AllowAny])
def test_api(request):
    return Response({
        'message': 'Users API работает!',
        'time': timezone.now().isoformat()
    })

# Кастомный сериализатор для JWT
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Добавляем дополнительные поля в токен
        token['username'] = user.username
        token['email'] = user.email
        token['inn'] = user.inn
        token['client_type'] = user.client_type
        token['company_name'] = user.company_name or ''
        return token

# Кастомные вьюхи для JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        # Добавляем данные пользователя в ответ при успешном входе
        if response.status_code == 200:
            try:
                username = request.data.get('username')
                user = Client.objects.get(username=username)
                user_data = ClientSerializer(user).data
                response.data['user'] = user_data
            except:
                pass
                
        return response

class CustomTokenRefreshView(TokenRefreshView):
    pass

# Профиль пользователя
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = ClientSerializer(request.user)
        return Response(serializer.data)

# Регистрация
class RegisterView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        request_body=RegisterSerializer,  # Используем ваш сериализатор
        responses={
            201: openapi.Response('Пользователь создан'),
            400: openapi.Response('Ошибка валидации')
        }
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = serializer.save()
                
                # Обновляем последнюю активность
                user.last_activity = timezone.now()
                user.save()
                
                # Получаем токены для нового пользователя
                tokens = get_tokens_for_user(user)
                user_data = ClientSerializer(user).data
                
                return Response({
                    'success': True,
                    'message': 'Регистрация успешна!',
                    'user': user_data,
                    'tokens': tokens
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': f'Ошибка при регистрации: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({
                'error': 'Ошибка валидации',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

# Вход в систему
class LoginView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_description="Вход в систему",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя или email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль', format='password')
            }
        ),
        
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Обновляем последнюю активность
            user.last_activity = timezone.now()
            user.save()
            
            # Получаем токены
            tokens = get_tokens_for_user(user)
            user_data = ClientSerializer(user).data
            
            return Response({
                'success': True,
                'message': 'Вход выполнен успешно',
                'user': user_data,
                'tokens': tokens
            })
        else:
            return Response({
                'error': 'Ошибка авторизации',
                'details': serializer.errors
            }, status=status.HTTP_401_UNAUTHORIZED)

# Выход из системы (добавление refresh токена в черный список)
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Выход из системы. Добавляет refresh токен в черный список.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Refresh токен для добавления в черный список',
                    example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
                )
            }
        ),
        
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Успешный выход из системы'
            })
        except TokenError:
            return Response({
                'error': 'Неверный токен'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Ошибка при выходе: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

# Проверка токена
class VerifyTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            'valid': True,
            'user': ClientSerializer(request.user).data
        })