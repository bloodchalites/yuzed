from rest_framework import serializers
from django.contrib.auth import authenticate
from ..models import Client

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    class Meta:
        model = Client
        fields = ('id', 'username', 'email', 'inn', 'kpp', 
                  'company_name', 'legal_address', 'physical_address',
                  'phone', 'registration_date', 'is_active', 'is_staff')
        read_only_fields = ('id', 'registration_date', 'is_active', 'is_staff')


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = Client
        fields = ('username', 'email', 'password', 'password_confirm',
                  'inn', 'kpp', 'company_name', 'legal_address',
                  'physical_address', 'phone')
    
    def validate(self, data):
        """Проверка паролей"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        
        # Проверяем уникальность ИНН
        if Client.objects.filter(inn=data['inn']).exists():
            raise serializers.ValidationError({"inn": "Пользователь с таким ИНН уже существует"})
        
        return data
    
    def create(self, validated_data):
        """Создание пользователя"""
        validated_data.pop('password_confirm')
        user = Client.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            inn=validated_data['inn'],
            kpp=validated_data.get('kpp'),
            company_name=validated_data.get('company_name'),
            legal_address=validated_data['legal_address'],
            physical_address=validated_data.get('physical_address'),
            phone=validated_data['phone'],
            is_active=True
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Аутентификация пользователя"""
        user = authenticate(
            username=data['username'],
            password=data['password']
        )
        
        if not user:
            raise serializers.ValidationError("Неверные учетные данные")
        
        if not user.is_active:
            raise serializers.ValidationError("Аккаунт неактивен")
        
        data['user'] = user
        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор для JWT токенов"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
