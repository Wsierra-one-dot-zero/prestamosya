import boto3
from botocore.exceptions import ClientError
import logging
import json
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_secret(secret_name: str = "rds!db-d9a26c18-a0cc-4a4c-aa73-820945d749e2", 
               region_name: str = "us-east-1") -> dict:
    """
    Obtiene un secreto de AWS Secrets Manager
    
    Args:
        secret_name: Nombre del secreto
        region_name: Nombre de la región AWS
        
    Returns:
        dict: Contenido del secreto como diccionario
    """
    try:
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
        
    except ClientError as e:
        logger.error(f"Error al obtener el secreto: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        raise

def main():
    try:
        # Ejemplo de uso
        secret_name = "rds!db-d9a26c18-a0cc-4a4c-aa73-820945d749e2"
        region_name = "us-east-1"
        
        secret = get_secret(secret_name, region_name)
        print("\nContenido del secreto:")
        print(json.dumps(secret, indent=2))
        
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

