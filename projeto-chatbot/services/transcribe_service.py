import os
import uuid
import boto3
import requests
from botocore.exceptions import ClientError
import time

transcribe = boto3.client('transcribe')

def transcribe_audio(audio_url):
    """
    Transcreve um arquivo de áudio enviado pelo Telegram.

    Args:
        audio_url (str): URL do arquivo de áudio.

    Returns:
        str: Transcrição do áudio.
    """
    try:
        job_name = f"transcribe-job-{uuid.uuid4()}"
        response = transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': audio_url},
            MediaFormat='ogg',  # Pode ser ajustado dependendo do formato do áudio
            LanguageCode='pt-BR'
        )

        # Aguarda a conclusão do job (com timeout ou callback)
        while True:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status['TranscriptionJob']['TranscriptionJobStatus']
            if job_status in ['COMPLETED', 'FAILED']:
                break
            time.sleep(5)  # Aguardar 5 segundos antes de verificar novamente

        if job_status == 'FAILED':
            raise Exception(f"Erro ao transcrever o áudio. Status: {job_status}")

        transcription_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
        transcription_response = requests.get(transcription_url).json()

        return transcription_response['results']['transcripts'][0]['transcript']

    except ClientError as e:
        raise Exception(f"Erro de cliente no serviço Transcribe: {e}")
    except Exception as e:
        raise Exception(f"Erro no serviço Transcribe: {e}")
