import boto3
import os

# Inicializar o recurso DynamoDB
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

def check_user_profile(chat_id):
    """
    Verifica se o perfil do usuário já existe na tabela.
    Retorna o item do perfil se encontrado, ou None caso contrário.
    """
    try:
        response = table.get_item(Key={'id': str(chat_id)})
        return response.get('Item')  # Retorna o item completo ou None
    except Exception as e:
        raise Exception(f"Erro ao verificar perfil do usuário: {e}")

def save_user_response(chat_id, response):
    """
    Salva uma resposta inicial ou dados do usuário no DynamoDB.
    Sobrescreve o item se já existir para o mesmo chat_id.
    """
    try:
        table.put_item(Item={'id': str(chat_id), 'response': response})
    except Exception as e:
        raise Exception(f"Erro ao salvar resposta do usuário: {e}")

def update_user_profile(chat_id, data):
    """
    Atualiza os dados do perfil do usuário com base no `chat_id` e nos dados fornecidos.
    """
    try:
        # Construção dinâmica da expressão de atualização
        update_expression = "SET " + ", ".join(f"#{k}=:{k}" for k in data.keys())
        expression_attribute_names = {f"#{k}": k for k in data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in data.items()}

        response = table.update_item(
            Key={'id': str(chat_id)},  # Chave primária
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="UPDATED_NEW"
        )
        return response
    except Exception as e:
        raise Exception(f"Erro ao atualizar o perfil do usuário: {e}")
