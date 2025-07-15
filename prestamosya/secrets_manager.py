import boto3
from botocore.exceptions import ClientError
import logging
import json
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_secret(secret_name: str = None, region_name: str = None) -> dict:
    """
    Obtiene un secreto de AWS Secrets Manager
    
    Args:
        secret_name: Nombre del secreto (opcional, se obtendrá de la variable de entorno DB_SECRET_NAME si no se especifica)
        region_name: Nombre de la región AWS (opcional, se obtendrá de la variable de entorno AWS_REGION si no se especifica)
        
    Returns:
        dict: Contenido del secreto como diccionario
    """
    try:
        # Verificar que las credenciales de AWS están disponibles
        try:
            boto3.client('sts').get_caller_identity()
        except Exception as e:
            logger.error(f"No se pudieron obtener las credenciales de AWS: {str(e)}")
            raise Exception("No se pudieron obtener las credenciales de AWS. Verifique que las credenciales están configuradas correctamente.")

        # Obtener region y nombre del secreto de variables de entorno si no se especifican
        if not secret_name:
            secret_name = os.getenv('DB_SECRET_NAME')
            if not secret_name:
                raise ValueError("No se especificó el nombre del secreto y la variable DB_SECRET_NAME no está configurada")
        
        if not region_name:
            region_name = os.getenv('AWS_REGION', 'us-east-1')
            
        # Crear sesión y cliente de Secrets Manager
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        
        # Obtener el valor del secreto
        logger.info(f"Obteniendo secreto: {secret_name} de región: {region_name}")
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        
        # Manejar diferentes tipos de secretos
        if 'SecretString' in get_secret_value_response:
            secret = json.loads(get_secret_value_response['SecretString'])
            logger.info("Secreto obtenido exitosamente")
        else:
            # Si es un secreto binario
            decoded_binary_secret = get_secret_value_response['SecretBinary'].decode('utf-8')
            secret = json.loads(decoded_binary_secret)
            logger.info("Secreto binario obtenido exitosamente")
        
        return secret
        
    except Exception as e:
        logger.error(f"Error al obtener el secreto: {str(e)}")
        return None

