#!/bin/sh

# Esperar a que el servicio de credenciales de AWS esté disponible
until aws sts get-caller-identity --region us-east-1 2>/dev/null; do
    echo "Esperando credenciales de AWS..."
    sleep 2
    if [ "$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI" ]; then
        break
    fi
done

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Ejecutar Gunicorn
exec gunicorn prestamosya.wsgi:application --bind 0.0.0.0:8000
