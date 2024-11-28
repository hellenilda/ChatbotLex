# PollyBot

## Como usar

1. Crie um arquivo `.env` seguindo o modelo do `.env.example`.
    - Onde encontrar o BOT_ID:
    ![bot-id](./assets/bot%20id.png)
    - Onde encontrar o BOT_ALIAS_ID:
    ![alias-id](./assets/alias%20id.png)
2. Instale as dependências.
    ```bash
    pip install -r requirements.txt
    npm install
    ```
3. Dentro do diretório do arquivo `serverless.yml`, execute o comando `sls deploy`.
4. Execute o comando a seguir para acionar o Webhook do Telegram:
    ```bash
    curl -X POST "https://api.telegram.org/bot<TOKEN DO BOT>/setWebhook?url=<ENDPOINT GERADO PELO SERVERLESS>"
    ```