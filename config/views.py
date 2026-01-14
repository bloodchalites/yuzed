from django.shortcuts import render
from django.http import HttpResponse

def home_view(request):
    """Главная страница"""
    context = {
        'title': 'YUZEDO - Система документооборота',
        'user': request.user,
    }
    return render(request, 'home.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from users.models import Client
from django.contrib.auth.hashers import make_password

def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password1')
            inn = request.POST.get('inn')
            company_name = request.POST.get('company_name')
            legal_address = request.POST.get('legal_address')
            phone = request.POST.get('phone')
            
            # Проверяем что пароли совпадают
            if password != request.POST.get('password2'):
                messages.error(request, 'Пароли не совпадают')
                return redirect('register')
            
            # Проверяем что пользователя с таким username или email нет
            if Client.objects.filter(username=username).exists():
                messages.error(request, 'Пользователь с таким именем уже существует')
                return redirect('register')
            
            if Client.objects.filter(email=email).exists():
                messages.error(request, 'Пользователь с таким email уже существует')
                return redirect('register')
            
            if Client.objects.filter(inn=inn).exists():
                messages.error(request, 'Пользователь с таким ИНН уже зарегистрирован')
                return redirect('register')
            
            # Создаем пользователя
            user = Client.objects.create(
                username=username,
                email=email,
                password=make_password(password),
                inn=inn,
                company_name=company_name,
                legal_address=legal_address,
                phone=phone,
                is_active=True
            )
            
            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Ошибка регистрации: {str(e)}')
            return redirect('register')
    
    return render(request, 'registration/register.html')

from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    """Страница профиля пользователя"""
    return render(request, 'profile.html', {'user': request.user})

@login_required
def dashboard_view(request):
    """Личный кабинет"""
    return render(request, 'dashboard.html', {'user': request.user})
