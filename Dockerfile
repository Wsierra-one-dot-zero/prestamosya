# Usar imagen oficial de Python
FROM python:3.12-slim

# Evitar prompts durante las instalaciones
ENV DEBIAN_FRONTEND=noninteractive

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de requisitos
COPY requirements.txt .

# Instalar dependencias del sistema y Python
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto Django al contenedor
COPY . .

# Exponer el puerto (Django por defecto usa 8000)
EXPOSE 8000

# Comando por defecto para ejecutar la aplicación
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]