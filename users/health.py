from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import connection
from django.core.cache import cache
from datetime import datetime

class HealthCheckView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Проверка состояния всех сервисов"""
        
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {},
            'version': '1.0.0',
            'environment': 'development'
        }
        
        # 1. Проверка Django приложения
        try:
            health_status['services']['django'] = {
                'status': 'healthy',
                'message': 'Django приложение работает',
                'port': 8000
            }
        except Exception as e:
            health_status['services']['django'] = {
                'status': 'unhealthy',
                'message': str(e)
            }
            health_status['status'] = 'unhealthy'
        
        # 2. Проверка PostgreSQL
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    health_status['services']['postgresql'] = {
                        'status': 'healthy',
                        'message': 'PostgreSQL доступен',
                        'database': connection.settings_dict['NAME'],
                        'host': connection.settings_dict['HOST'],
                        'port': connection.settings_dict.get('PORT', 5432)
                    }
                else:
                    raise Exception("Неверный ответ от базы данных")
        except Exception as e:
            health_status['services']['postgresql'] = {
                'status': 'unhealthy',
                'message': str(e)
            }
            health_status['status'] = 'unhealthy'
        
        # 3. Проверка Redis
        try:
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') == 'ok':
                health_status['services']['redis'] = {
                    'status': 'healthy',
                    'message': 'Redis доступен',
                    'port': 6379
                }
            else:
                raise Exception("Redis не отвечает")
        except Exception as e:
            health_status['services']['redis'] = {
                'status': 'unhealthy',
                'message': str(e)
            }
            health_status['status'] = 'unhealthy'
        
        # 4. Статистика пользователей
        try:
            from .models import Client
            total_users = Client.objects.count()
            active_users = Client.objects.filter(is_active=True).count()
            health_status['statistics'] = {
                'total_users': total_users,
                'active_users': active_users,
                'pending_users': Client.objects.filter(status='pending').count(),
                'active_companies': Client.objects.filter(status='active', client_type='organization').count(),
                'individuals': Client.objects.filter(client_type='individual').count(),
                'organizations': Client.objects.filter(client_type='organization').count()
            }
        except Exception as e:
            health_status['statistics'] = {
                'error': str(e)
            }
        
        # 5. Информация о системе
        health_status['system'] = {
            'architecture': 'monolithic',
            'components': ['django', 'postgresql', 'redis', 'frontend'],
            'ports': {
                'api': 8000,
                'postgresql': 5433,
                'redis': 6380,
                'frontend': 3000
            }
        }
        
        return Response(health_status)