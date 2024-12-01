import os
import json
import requests
import boto3

# Inicializa os clientes da AWS
lex = boto3.client('lexv2-runtime')

# URL base do Telegram
TELEGRAM_API_URL = f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}"

def webhook_handler(event, context):
    # Obtendo o corpo da requisição
    body = event.get('body', '')

    # Verificando se o corpo está vazio
    if not body:
        return {'statusCode': 400, 'body': 'Erro: corpo da requisição vazio'}

    # Decodifica o JSON do corpo
    try:
        body_json = json.loads(body)
    except json.JSONDecodeError:
        return {'statusCode': 400, 'body': 'Erro: falha ao decodificar JSON'}

    # Obtendo a mensagem e o ID do chat
    message = body_json.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')
    photo = message.get('photo', [])
    voice = message.get('voice', {})

    try:
        # Processa o texto com o Lex
        lex_response = lex.recognize_text(
            botId=os.environ['BOT_ID'],
            botAliasId=os.environ['BOT_ALIAS_ID'],
            localeId=os.environ['LOCALE_ID'],
            sessionId=str(chat_id),
            text=text
        )
        # Extrai a resposta do Lex
        lex_message = lex_response.get('messages', [{}])[0].get('content', 'Não entendi sua mensagem.')

        # Envia a resposta ao Telegram
        send_message_to_telegram(chat_id, lex_message)
        return {'statusCode': 200, 'body': 'Mensagem processada com sucesso'}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps(f'Erro ao processar com o Lex: {str(e)}')}

def send_message_to_telegram(chat_id, text):
    """Envia uma mensagem ao Telegram."""
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Erro ao enviar mensagem ao Telegram: {str(e)}")
