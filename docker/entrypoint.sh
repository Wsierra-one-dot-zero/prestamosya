#!/bin/sh

# Esperar a que el servicio de credenciales de AWS esté disponible
until aws sts get-caller-identity --region us-east-1 2>/dev/null; do
    echo "Esperando credenciales de AWS..."
    sleep 2
    if [ "$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI" ]; then
        break
    fi
done

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
