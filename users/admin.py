from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Client

@admin.register(Client)
class ClientAdmin(UserAdmin):
    list_display = ('username', 'email', 'inn', 'company_name', 'client_type', 'status', 'is_active')
    list_filter = ('status', 'client_type', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'inn', 'company_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Бизнес информация', {'fields': ('inn', 'kpp', 'company_name', 'client_type')}),
        ('Контактная информация', {'fields': ('legal_address', 'physical_address', 'phone')}),
        ('Статус системы', {'fields': ('status', 'last_activity')}),
    )
    
    readonly_fields = ('registration_date', 'last_activity')