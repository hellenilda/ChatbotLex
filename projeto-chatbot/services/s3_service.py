import boto3
import os
import requests
import uuid
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

def save_image_to_s3(file_id, chat_id):
    """
    Salva uma imagem enviada pelo usuário no Telegram em um bucket do S3.

    Args:
        file_id (str): ID do arquivo no Telegram.
        chat_id (str): ID do chat do Telegram (para organizar no bucket).

    Returns:
        str: Nome do arquivo salvo no S3.
    """
    token = os.environ['TELEGRAM_TOKEN']
    bucket_name = os.environ['BUCKET_NAME']

    try:
        # Obter o caminho do arquivo através da API do Telegram
        file_info = requests.get(f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}").json()
        file_path = file_info['result']['file_path']

        # Baixar os dados da imagem
        image_data = requests.get(f"https://api.telegram.org/file/bot{token}/{file_path}").content

        # Gerar um nome único para o arquivo no S3
        file_name = f"{chat_id}/{uuid.uuid4()}.jpg"

        # Fazer upload da imagem para o S3
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=image_data,
            ContentType="image/jpeg"
        )

        return file_name
    except ClientError as e:
        raise Exception(f"Erro ao salvar no S3: {e}")
    except Exception as e:
        raise Exception(f"Erro ao processar a imagem: {e}")
