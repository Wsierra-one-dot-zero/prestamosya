# Imagen base oficial de Python
FROM python:3.12-slim

# Directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia solo los archivos de dependencias primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el código fuente de la app
COPY . .

# Agregar versión a la imagen
RUN python -c "from version import __version__; print('PRESTAMOSYA_VERSION=' + __version__)" > /app/version.txt

# Crear carpeta para archivos estáticos
RUN mkdir -p /app/staticfiles

# Expone el puerto 8000
EXPOSE 8000

# Hacer el script de entrada ejecutable
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Comando por defecto para producción
ENTRYPOINT ["/entrypoint.sh"]