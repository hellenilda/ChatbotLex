import os
import json
import boto3
import requests
from services.s3_service import save_image_to_s3
from services.transcribe_service import transcribe_audio
from services.rekognition_service import analyze_image
from services.translate_service import translate_text
from services.dynamodb_service import update_user_profile

# Inicializando cliente AWS
s3_client = boto3.client('s3')
lex_client = boto3.client('lexv2-runtime')

def get_telegram_file_url(file_id):
    token = os.environ['TELEGRAM_TOKEN']
    file_info = requests.get(f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}").json()
    file_path = file_info['result']['file_path']
    return f"https://api.telegram.org/file/bot{token}/{file_path}"

def process_message(event, context):
    body = json.loads(event.get('body', '{}'))
    message = body.get('message', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text')
    photo = message.get('photo')
    voice = message.get('voice')

    if text:
        try:
            # Detecta se o texto precisa ser traduzido para português
            translated_text = translate_text(text, 'pt')
            body['text'] = translated_text
            
            session_id = body.get('session_id', 'default_session')
            from_user = message.get('from', {})
            user_id = from_user.get('id')

            if not user_id:
                return {'statusCode': 400, 'body': json.dumps('Não foi possível identificar o usuário.')}

            # Enviando mensagem ao Lex
            lex_response = lex_client.recognize_text(
                botId=os.environ['BOT_ID'],
                botAliasId=os.environ['BOT_ALIAS_ID'],
                localeId=os.environ['LOCALE_ID'],
                sessionId=session_id,
                text=translated_text
            )

            lex_message = lex_response.get('messages', [{}])[0].get('content', 'Não entendi sua mensagem.')

            # Verificar se a intenção é "CriarPerfil"
            if lex_response.get('sessionState', {}).get('intent', {}).get('name') == 'CriarPerfil':
                update_user_profile(user_id, {'status': 'perfil_criado'})

            return {'statusCode': 200, 'body': json.dumps({'message': lex_message})}

        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'error': f'Erro ao processar texto no Lex: {str(e)}'})}

    elif photo:
        try:
            file_id = photo[-1]['file_id']
            file_url = get_telegram_file_url(file_id)
            saved_file_name = save_image_to_s3(file_id, file_url, chat_id)
            analysis_result = analyze_image(saved_file_name)
            return {'statusCode': 200, 'body': json.dumps({'message': analysis_result})}
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'error': f'Erro ao processar imagem: {str(e)}'})}

    elif voice:
        try:
            file_id = voice['file_id']
            audio_url = get_telegram_file_url(file_id)
            transcription = transcribe_audio(audio_url)
            body['text'] = transcription
            return process_message({'body': json.dumps(body)}, context)  # Recursão para processar texto
        except Exception as e:
            return {'statusCode': 500, 'body': json.dumps({'error': f'Erro ao processar áudio: {str(e)}'})}

    return {'statusCode': 400, 'body': json.dumps('Tipo de mensagem não suportado.')}