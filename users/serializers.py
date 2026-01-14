from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Client
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

class ClientSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Client
        fields = [
            'id', 'username', 'email', 'password',
            'first_name', 'last_name',
            'inn', 'kpp', 'company_name',
            'legal_address', 'physical_address',
            'phone', 'client_type', 'status',
            'date_joined', 'last_login', 'last_activity'
        ]
        read_only_fields = [
            'id', 'status', 'date_joined', 
            'last_login', 'last_activity'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'inn': {'required': True},
            'phone': {'required': True},
            'legal_address': {'required': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Client(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

# Сериализатор для регистрации
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True, 
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Client
        fields = [
            'username', 'email', 'password', 'password2',
            'first_name', 'last_name',
            'inn', 'kpp', 'company_name',
            'legal_address', 'physical_address',
            'phone', 'client_type'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        
        inn = attrs.get('inn', '')
        if not inn.isdigit() or len(inn) not in [10, 12]:
            raise serializers.ValidationError({"inn": "ИНН должен содержать 10 или 12 цифр"})
        
        phone = attrs.get('phone', '')
        if not phone.startswith('+'):
            raise serializers.ValidationError({"phone": "Телефон должен начинаться с +"})
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = Client.objects.create_user(**validated_data)
        return user

# Сериализатор для входа
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError("Неверные учетные данные")
            if not user.is_active:
                raise serializers.ValidationError("Пользователь неактивен")
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError("Необходимо указать имя пользователя и пароль")
        
        return attrs

# Утилита для создания токенов
def get_tokens_for_user(user):
    """Создание JWT токенов для пользователя"""
    refresh = RefreshToken.for_user(user)
    
    # Добавляем кастомные данные в токен (как в CustomTokenObtainPairSerializer)
    refresh['username'] = user.username
    refresh['email'] = user.email
    refresh['inn'] = user.inn
    refresh['client_type'] = user.client_type
    refresh['company_name'] = user.company_name or ''
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }