import boto3

translate_client = boto3.client('translate')

def translate_text(text, target_language):
    """
    Traduz um texto usando Amazon Translate.

    Args:
        text (str): Texto a ser traduzido.
        target_language (str): Código do idioma destino (ex.: 'en', 'es').

    Returns:
        str: Texto traduzido.
    """
    try:
        response = translate_client.translate_text(
            Text=text,
            SourceLanguageCode='auto',
            TargetLanguageCode=target_language
        )
        return response.get('TranslatedText', '')
    except Exception as e:
        raise Exception(f"Erro ao traduzir texto: {e}")
