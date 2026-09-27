import os

from flask import Flask, request
import psycopg
from psycopg.types.json import Jsonb
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env
conn = psycopg.connect(os.environ["DATABASE_URL"], autocommit=True)

@app.route('/waha', methods=['POST'])
def receber_webhook():
    dados = request.get_json()
    chat_id = dados['payload']['from']
    resultado = conn.execute("SELECT * FROM grupos_monitorados WHERE chat_id = %s AND ativo", (chat_id,)).fetchall()

    if not resultado:
        return "ignorado", 200

    conn.execute(
        "INSERT INTO mensagens_cruas (wa_message_id, chat_id, payload) VALUES (%s, %s, %s) ON CONFLICT (wa_message_id) DO NOTHING", (dados['payload']['id'], chat_id, Jsonb(dados['payload']))
    )
    print(f"Mensagem recebida e armazenada: {dados['payload']['id']} do chat {chat_id}")
    return "ok", 200

app.run(host="0.0.0.0", port=8080, debug=True)

