import os
import json
import requests
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
lex = boto3.client('lexv2-runtime')

def telegramWebhook(event, context):
    # Obtendo o corpo da requisição
    body = event.get('body', '')

    # Verificando se o corpo está vazio
    if not body:
        return {
            'statusCode': 400,
            'body': json.dumps('Erro: corpo da requisição vazio')
        }

    # Tentando fazer o parse do corpo JSON
    try:
        body_json = json.loads(body)
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps('Erro: falha ao decodificar JSON')
        }

    # Processando a mensagem
    message = body_json.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text')

    # Verificando se temos uma mensagem de texto e o chat_id
    if chat_id and text:
        # Processar texto com Lex
        try:
            lex_response = lex.recognize_text(
                botId=os.environ['BOT_ID'],
                botAliasId=os.environ['BOT_ALIAS_ID'],
                localeId=os.environ['LOCALE_ID'],
                sessionId=str(chat_id),  # Identificador único para a sessão
                text=text
            )
            # Obter a resposta gerada pelo Lex
            lex_message = lex_response.get('messages', [{}])[0].get('content', 'Não entendi sua mensagem.')

            # Enviar resposta ao Telegram
            url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': lex_message
            }
            try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
                return {
                    'statusCode': 200,
                    'body': json.dumps('Mensagem processada com sucesso')
                }
            except requests.exceptions.RequestException as e:
                return {
                    'statusCode': 500,
                    'body': json.dumps(f'Erro ao enviar a mensagem para o Telegram: {str(e)}')
                }
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Erro ao processar com o Lex: {str(e)}')
            }

    # Caso a mensagem seja uma foto
    if 'photo' in message:
        file_id = message['photo'][-1]['file_id']
        try:
            file_url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/getFile?file_id={file_id}"
            file_info = requests.get(file_url).json()
            file_path = file_info['result']['file_path']
            image_data = requests.get(f"https://api.telegram.org/file/bot{os.environ['TELEGRAM_TOKEN']}/{file_path}").content
            s3.put_object(Bucket=os.environ['BUCKET_NAME'], Key=file_id, Body=image_data)
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f'Erro ao salvar imagem no S3: {str(e)}')
            }
        return {'statusCode': 200, 'body': json.dumps('Imagem salva no S3')}

    # Caso de mensagem de voz
    elif 'voice' in message:
        return {'statusCode': 501, 'body': 'Processamento de áudio ainda não implementado'}

    # Mensagem não reconhecida
    return {'statusCode': 400, 'body': json.dumps('Tipo de mensagem não suportado')}
