import os
import boto3
from botocore.exceptions import ClientError

rekognition = boto3.client('rekognition')

def analyze_image(s3_key):
    """
    Analisa uma imagem no S3 usando Amazon Rekognition para detectar rostos humanos.

    Args:
        s3_key (str): Caminho do objeto dentro do bucket S3.

    Returns:
        str: Resultado da análise, indicando se a imagem contém pessoas e quantas.

    Raises:
        Exception: Em caso de falha na análise da imagem.
    """
    try:
        # Obtém o nome do bucket do ambiente
        bucket_name = os.environ['BUCKET_NAME']

        # Chama o Rekognition para detectar faces na imagem
        response = rekognition.detect_faces(
            Image={'S3Object': {'Bucket': bucket_name, 'Name': s3_key}},
            Attributes=['ALL']
        )

        # Obtém detalhes das faces detectadas
        faces = response.get('FaceDetails', [])
        if not faces:
            return "Nenhuma pessoa encontrada na imagem."

        # Retorna um resumo da análise
        return f"Pessoas encontradas: {len(faces)}"

    except ClientError as e:
        raise Exception(f"Erro ao analisar imagem no Rekognition: {e}")
