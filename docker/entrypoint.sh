#!/bin/sh

# Esperar a que las credenciales de AWS estén disponibles
echo "Esperando credenciales de AWS..."
for i in {1..30}; do
    if aws sts get-caller-identity --region us-east-1 2>/dev/null; then
        echo "Credenciales de AWS disponibles"
        break
    fi
    echo "Intento $i/30"
    sleep 2
done

if ! aws sts get-caller-identity --region us-east-1 2>/dev/null; then
    echo "ERROR: No se pudieron obtener las credenciales de AWS después de 60 segundos"
    exit 1
fi

# Verificar que la variable DB_SECRET_NAME está configurada
if [ -z "$DB_SECRET_NAME" ]; then
    echo "ERROR: La variable DB_SECRET_NAME no está configurada"
    exit 1
fi

# Recolectar archivos estáticos
python manage.py collectstatic --noinput || {
    echo "ERROR: Fallo al recolectar archivos estáticos"
    exit 1
}

# Ejecutar Gunicorn
exec gunicorn prestamosya.wsgi:application --bind 0.0.0.0:8000
