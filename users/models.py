from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class Client(AbstractUser):
    """
    Модель клиента системы документооборота.
    Расширяет стандартную модель User Django.
    """
    
    # Бизнес-реквизиты (обязательные для юрлиц)
    inn = models.CharField(
        _('ИНН'), 
        max_length=12, 
        unique=True, 
        help_text=_('12 цифр для организаций, 10 для ИП')
    )
    
    kpp = models.CharField(
        _('КПП'), 
        max_length=9, 
        blank=True, 
        null=True,
        help_text=_('9 символов, только для организаций')
    )
    
    # Контактная информация
    company_name = models.CharField(
        _('Название компании'),
        max_length=255,
        blank=True,
        null=True
    )
    
    legal_address = models.TextField(
        _('Юридический адрес'),
        max_length=500
    )
    
    physical_address = models.TextField(
        _('Фактический адрес'),
        max_length=500,
        blank=True,
        null=True,
        help_text=_('Если отличается от юридического')
    )
    
    phone = models.CharField(
        _('Телефон'),
        max_length=20,
        help_text=_('Формат: +7XXXXXXXXXX')
    )
    
    # Дополнительные поля
    registration_date = models.DateTimeField(
        _('Дата регистрации'),
        auto_now_add=True
    )
    
    last_activity = models.DateTimeField(
        _('Последняя активность'),
        auto_now=True
    )
    
    # Тип клиента
    CLIENT_TYPE_CHOICES = [
        ('individual', _('Физическое лицо')),
        ('entrepreneur', _('Индивидуальный предприниматель')),
        ('organization', _('Юридическое лицо')),
    ]
    
    client_type = models.CharField(
        _('Тип клиента'),
        max_length=20,
        choices=CLIENT_TYPE_CHOICES,
        default='organization'
    )
    
    # Статус клиента
    CLIENT_STATUS_CHOICES = [
        ('active', _('Активный')),
        ('inactive', _('Неактивный')),
        ('blocked', _('Заблокирован')),
        ('pending', _('Ожидает подтверждения')),
    ]
    
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=CLIENT_STATUS_CHOICES,
        default='pending'
    )
    
    # Исправляем конфликт related_name с моделью User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('Группы, к которым принадлежит пользователь'),
        related_name='client_set',  # Уникальный related_name
        related_query_name='client',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Конкретные права пользователя'),
        related_name='client_set',  # Уникальный related_name
        related_query_name='client',
    )
    
    class Meta:
        verbose_name = _('Клиент')
        verbose_name_plural = _('Клиенты')
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['inn']),
            models.Index(fields=['status', 'registration_date']),
            models.Index(fields=['client_type', 'status']),
        ]
    
    def __str__(self):
        if self.company_name:
            return f"{self.company_name} (ИНН: {self.inn})"
        return f"{self.username} (ИНН: {self.inn})"
    
    def save(self, *args, **kwargs):
        # Автоматически устанавливаем email как username если не указан
        if not self.username and self.email:
            self.username = self.email
        
        # Для физлиц и ИП убираем КПП
        if self.client_type in ['individual', 'entrepreneur']:
            self.kpp = None
        
        super().save(*args, **kwargs)
    
    @property
    def full_info(self):
        """Полная информация о клиенте"""
        info = []
        if self.company_name:
            info.append(self.company_name)
        info.append(f"ИНН: {self.inn}")
        if self.kpp:
            info.append(f"КПП: {self.kpp}")
        info.append(f"Email: {self.email}")
        return ", ".join(info)
    
    @property
    def is_verified(self):
        """Проверен ли клиент"""
        return self.status == 'active'
    
    @property
    def can_use_system(self):
        """Может ли клиент использовать систему"""
        return self.status in ['active', 'pending'] and self.is_active
