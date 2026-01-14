
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone

@api_view(['GET'])
@permission_classes([AllowAny])
def payment_list(request):
    return Response({
        'message': 'Payments API работает!',
        'time': timezone.now().isoformat()
    })
