from django.http import JsonResponse
from django.views import View
from django.db import connection

class HealthCheckView(View):
    """
    Vista para el health check de la aplicación.
    Verifica la conexión a la base de datos y devuelve el estado del servicio.
    """
    def get(self, request, *args, **kwargs):
        # Verificar la conexión a la base de datos
        db_connected = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_connected = True
        except Exception:
            db_connected = False
        
        status = 200 if db_connected else 503
        
        return JsonResponse({
            'status': 'ok' if db_connected else 'error',
            'database': 'connected' if db_connected else 'disconnected',
            'timestamp': timezone.now().isoformat(),
        }, status=status)
